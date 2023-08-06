"""
    This file contains the definition of beam steps to perform in
    the realtime pipeline analysis for Vibration signals that arrives.
"""

###################################################
# Imports declarations
###################################################
import logging
from typing import List, Dict, Tuple
import txp.common.utils.metrics as metrics
from txp.common.models import AssetMetrics
from apache_beam.transforms.window import FixedWindows
from scipy.fft import fft
import numpy as np
import apache_beam as beam
from txp.common import edge
from google.cloud import firestore
from txp.common.utils import firestore_utils
import datetime


###################################################
# Constant definitions
###################################################

# This steps only makes sense for this devices at the moment.
# They are not fully generic.
_VALID_DEVICES = {"Icomox"}


###################################################
# Declaration of functions and Apache Beam classes
###################################################
def compute_rms_smooth(data: List, window_size: int = 8):
    """Computes a RMS smoothing for some vibration signal.

    Args:
        data (list): A matrix of values for each axis.

    Returns:
        List of BigQuery column JSON value:
            "values": the list of samples for the axis.
            "index": the axis index (x:1, y:2, z:3)
    """
    rms_data_axis = []

    for index, single_axis_sample in enumerate(data):
        rms_data_axis.append({"values": [], "index": index})
        n = len(rms_data_axis)
        rms_data_axis[n - 1]["values"] = metrics.rolling_rms(
            np.asarray(single_axis_sample)
        ).tolist()

    return rms_data_axis


def compute_fft(data: List[Dict]):
    """Compute the FFT on the array of values.

    Args:
        data (List[Dict]): The list of values to be persisted in the column
            `data`. Each value is an object with the structure:
                 "values": the list of samples for the axis.
                 "index": the axis index (x:1, y:2, z:3)

    Returns:
        List of BigQuery column JSON value:
            "values": the list of samples for the axis.
            "index": the axis index (x:1, y:2, z:3)
    """
    fft_data = []
    for dimension_signal_sample in data:
        fft_data.append({"values": [], "index": dimension_signal_sample["index"]})
        n = len(fft_data)
        for z in fft(dimension_signal_sample["values"]):
            fft_data[n - 1]["values"].append(
                {"real": float(z.real), "imag": float(z.imag)}
            )

    return fft_data


def compute_rpm(mag_axis_data: List):
    """Compute the RPM of a conveyor engine given the magnetometer data.

    Args:
        mag_axis_data: Matrix of magnetometer collected data. Each row corresponds
            for a given axis.

    Returns:
        Returns the list of RPM float values, each position in the array
            corresponds to an axis.

    TODO: Required information motor specific should be pulled down from persistence layer.
    """
    from iCOMOXSDK.sensors import BMM150

    rpm_axis = []
    BMM150_quantile_for_noise_floor_estimator = 0.25
    BMM150_minimum_SNR_for_speed_detection_dB = 20
    BMM150_ = BMM150.class_BMM150(
        quantile_for_noise_floor_estimator=BMM150_quantile_for_noise_floor_estimator,
        minimum_SNR_for_speed_detection_dB=BMM150_minimum_SNR_for_speed_detection_dB,
    )

    for axis in mag_axis_data:
        ASYNC_MOTOR_number_of_poles_pairs = 2
        ASYNC_MOTOR_slip_factor_percentages = 0.0
        network_frequency_Hz = BMM150_.maximum_of_PSD(axis)
        synchronous_frequency_Hz = (
            network_frequency_Hz / ASYNC_MOTOR_number_of_poles_pairs
        )
        rotor_frequency_Hz = synchronous_frequency_Hz * (
            1 - ASYNC_MOTOR_slip_factor_percentages / 100
        )
        rpm = rotor_frequency_Hz * 60
        rpm_axis.append(rpm)
    return rpm_axis


class VibrationProcessing(beam.DoFn):
    """This beam step is used to generate the RMS smoothed wave given an input
    gateway package collected in field.
    """

    def to_runner_api_parameter(self, unused_context):
        return "beam:transforms:custom_parsing:custom_v0", None

    def is_valid_device(self, element) -> bool:
        """Only valid devices will be processed in the step"""
        return element["device_type"] in _VALID_DEVICES

    def get_signal_data(self, elements, signal_type):
        """Returns the data corresponding to the specified signal type.

        Args:
            elements: The list of dictionaries. Each element represent a Gateway Package
                collected signal.

        Returns:
            The data for the given element if found. Else None.
        """
        data = None
        for e in elements:
            if e["perception_name"] == signal_type.perception_name():
                logging.info(
                    f"Vibration processing found signal for {signal_type.perception_name()}"
                )
                data = e["data"]
        if not data:
            return None

        fmt_data = [list(dimension["values"]) for dimension in data]

        return fmt_data

    def get_edge_from_db(self, db_client: firestore.Client, element: Dict):
        """Returns the edge document from the persistence layer."""
        edge_doc = firestore_utils.get_edge_from_firestore(
            element["configuration_id"],
            element["tenant_id"],
            element["edge_logical_id"],
            db_client,
        )
        return edge_doc

    def get_machine_id_by_edge(
        self, db_client: firestore.Client, element: Dict, edge_ref
    ):
        """Returns the machine document from the persistence layer."""
        machine = firestore_utils.get_machine_from_firestore_by_edge(
            db_client, element["tenant_id"], edge_ref
        )

        if not machine:
            logging.warning(
                f"Could not find machine for the package received from "
                f"{element['edge_logical_id']}"
            )
            machine_id = ""

        else:
            logging.info(
                f"The package received belongs to the machine: {machine['asset_id']}"
            )
            machine_id = machine["asset_id"]

        return machine_id

    def get_bigquery_row(
        self, element, machine_id, magnetometer_data, temperature_data
    ):
        perception_data = [list(dimension["values"]) for dimension in element["data"]]
        rms_data_axis = compute_rms_smooth(perception_data)
        fft_data = compute_fft(rms_data_axis)
        rmp_data = compute_rpm(magnetometer_data)

        data_formatted = []
        for i, dimension_signal_sample in enumerate(perception_data):
            data_formatted.append({"values": list(dimension_signal_sample), "index": i})
            i += 1

        return {
            "signal": data_formatted,
            "rms_smoothed_signal": rms_data_axis,
            "fft": fft_data,
            "rpm": rmp_data,
            "temperature": temperature_data[0][0],
            "failure_frequencies": [],
            "perception_name": element["perception_name"],
            "edge_logical_id": element["edge_logical_id"],
            "asset_id": machine_id,
            "configuration_id": element["configuration_id"],
            "observation_timestamp": element["observation_timestamp"],
            "tenant_id": element["tenant_id"],
            "partition_timestamp": element["partition_timestamp"],
            "observation_time_secs": element["sampling_window_observation_time"],
        }

    def process(
        self, elements, timestamp=beam.DoFn.TimestampParam, window=beam.DoFn.WindowParam
    ):
        # Get first element for metadata access
        element = elements[0]
        # Only process Vibration data from Icomox box
        if not self.is_valid_device(element):
            logging.info(
                f"Decive of {element['device_type']} is not "
                f"valid for Vibration Processing step."
            )
            return

        magnetometer_data = self.get_signal_data(elements, edge.MagnetometerSignal)
        temperature_data = self.get_signal_data(elements, edge.TemperatureSignal)
        firestore_client = firestore.Client()
        edge_doc = self.get_edge_from_db(firestore_client, element)
        machine_id = self.get_machine_id_by_edge(
            firestore_client, element, edge_doc.reference
        )

        # For the vibration received data, it will yield the database row element to
        # persist in the vibration warehouse.
        # Other kind of signals will not yield any element.
        for e in elements:
            if e["perception_name"] not in {
                edge.VibrationSpeedSignal.perception_name(),
                edge.VibrationAccelerationSignal.perception_name(),
            }:
                continue
            logging.info(
                f"Processing vibration step for {e['perception_name']} from edge: {e['edge_logical_id']}"
            )
            bigquery_row = self.get_bigquery_row(
                e, machine_id, magnetometer_data, temperature_data
            )

            logging.info(
                f"Yielding vibration steps result for {e['perception_name']} from edge: {e['edge_logical_id']}"
            )

            yield bigquery_row


###############################  Windows processing of metrics ###################################
class ProcessMachineMetricsForVibrationRows(beam.DoFn):
    """This beam step will take care of processing the vibration data rows
    produced by the VibrationProcessing.

    This step is designed to work with a windowed input. Metrics are computed
    for elements that arrives in some defined fixed window timelapse.

    The step is designed to work with a grouped set of elements given a window of data.
    The elements are grouped by a key. The key is built using the following template:
        - "[edge_logical_id]-[perception_name]"


    """

    def process(self, key_value):
        """Process the grouped windowed elements.

        Args:
            key_value: a tuple of grouped elements:
                - key_value[0]: The key
                - key_value[1]: The elements which match that key.

        Returns
            Yields a tuple with the following values:
                - 0: The dictionary representing an instance of AssetMetrics object.
                - 1: The `tenant-id` to which the data belongs.
        """
        import pytz

        k, v = key_value

        logging.info(f"Received window of {len(v)} packages for {k}")

        rows = sorted(v, key=lambda row: row["observation_timestamp"], reverse=True)

        if rows[0]["perception_name"] != "VibrationAcceleration":
            return

        # Values for new metrics
        timestamp = self._get_new_timestamp(rows)
        new_worked_time = self._compute_total_new_worked_time(rows)
        temperature = self._get_temperature(rows)
        rpm = self._get_rpm(rows)

        # logging messages of metrics
        logging.info(
            f"New metrics computed for {k}: "
            f"Timestamp - {datetime.datetime.fromtimestamp(timestamp, tz=pytz.timezone('America/Mexico_City'))} | "
            f"Additional Worked Time - {new_worked_time} hrs |"
            f"Temperature - {temperature} C |"
            f"RPM - {rpm} "
        )

        asset_metrics = {
            "asset_type": "Conveyor",
            "last_seen": datetime.datetime.fromtimestamp(
                timestamp, tz=pytz.timezone("America/Mexico_City")
            ).strftime(AssetMetrics.last_seen_format()),
            "rpm": rpm[0],
            "temperature": temperature,
            "worked_hours": new_worked_time,
            "asset_id": rows[0]["asset_id"],
        }

        yield (asset_metrics, rows[0]["tenant_id"])

    def _get_rpm(self, rows: List[Dict]):
        return rows[0]["rpm"]

    def _get_temperature(self, rows: List[Dict]):
        return rows[0]["temperature"]

    def _get_new_timestamp(self, rows: List[Dict]):
        return rows[0]["observation_timestamp"] // 1e9

    def _compute_total_new_worked_time(self, rows: List[Dict]) -> float:
        """Given a list of BigQuery Rows for an edge device, then
        computes the total time worked added by each observation.

        Returns:
            Int value of added time in HOURS.
        """
        observation_time_col = list(map(lambda d: d["observation_time_secs"], rows))
        return float(sum(observation_time_col) / 3600)


class WriteMetricsToFirestore(beam.DoFn):
    """This beam step receives an AssetMetrics instance and stores it on
    Firestore.
    """

    def process(self, element, *args, **kwargs):
        """
        Args:
            element: The AssetMetrics dictionary instance produced by step
            `ProcessMachineMetricsForVibrationRows`

        Returns:
            Nothing. End of this beam branch.
        """
        AssetMetrics.update_metric_in_firestore(
            AssetMetrics.get_instance_from_proto(
                AssetMetrics.get_proto_from_dict(element[0])
            ),
            element[1],
        )


class GatewayPackagesByFixedWindow(beam.PTransform):
    """This beam transform applies windowing for the input unbound collection."""

    def __init__(self, windows_size):
        self.windows_size = windows_size * 60

    def expand(self, pcoll):
        return pcoll | "Deserialize Protobuf" >> beam.WindowInto(
            FixedWindows(self.windows_size)
        )
