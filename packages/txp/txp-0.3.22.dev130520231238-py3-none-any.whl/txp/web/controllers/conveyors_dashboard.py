"""
    This script defines objects and functions to organize the information
    to show in the new interface focused on Conveyors & Transportation systems.
"""
import dataclasses
import datetime

from google.cloud import bigquery
from txp.common.ml.tasks import AssetStateCondition
from txp.common.edge.common import MachineMetadata, EdgeDescriptor
from typing import List, Dict, Any, Tuple

from txp.common.models import ProjectFirestoreModel, get_assets_metrics, AssetMetrics
import txp.common.utils.iot_core_utils as iot_controller
import txp.common.utils.bigquery_utils as bq_utils
import time
import enum
import pytz
import pandas as pd
import streamlit as st
import logging
from txp.common.config import settings
log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)


class TransportationLineConnectivity(enum.Enum):
    OPTIMAL = 0
    REGULAR = 1
    BAD = 2


@dataclasses.dataclass
class ConveyorMetrics:
    last_temperature_value: float
    last_rpm_value: float
    last_seen_date: Any
    total_worked_seconds: int


@dataclasses.dataclass
class TransportationLine:
    """A Transportation line a machines group.

    This holds the information to show the Transportations Lines table
    on the main dashboard.
    """

    name: str
    num_of_machines: int
    project_model: ProjectFirestoreModel
    cloud_credentials: Any

    def __post_init__(self):
        self._machines_dict = {}
        self._machine_to_edge_dict = {}
        for machine in self.project_model.assets_table:
            self._machines_dict[machine]: Dict[
                str, MachineMetadata
            ] = self.project_model.assets_table[machine]
            edge = self._machines_dict[machine].associated_with_edges[0]  # NOTE: Take only 1 edge p/conveyor
            self._machine_to_edge_dict[machine]: Dict[
                str, EdgeDescriptor
            ] = self.project_model.edges_table[edge]

        self._machine_metrics: Dict[str, AssetMetrics] = {}
        self._pull_information_from_db()

    def _pull_information_from_db(self):
        assets_metrics = get_assets_metrics(
            self.cloud_credentials,
            list(self.project_model.assets_table.keys()),
            st.secrets['tenant_id']
        )

        for asset_metric in assets_metrics:
            if asset_metric is None:
                continue
            self._machine_metrics[asset_metric.asset_id] = asset_metric

    def get_machine_by_id(self, mid) -> MachineMetadata:
        return self._machines_dict[mid]

    def get_edge_by_machine(self, machine) -> EdgeDescriptor:
        return self._machine_to_edge_dict[machine]

    def get_connectivity(self) -> TransportationLineConnectivity:
        total_edges = len(self._machine_to_edge_dict)
        total_connected_or_sampling = 0
        total_disconnected_or_recovering = 0
        for edge in self._machine_to_edge_dict.values():
            if (
                self.project_model.edges_table[edge.logical_id] == "Disconnected"
                or self.project_model.edges_table[edge.logical_id] == "Recovering"
            ):
                total_disconnected_or_recovering += 1
            else:
                total_connected_or_sampling += 1

        if total_edges == total_connected_or_sampling:
            return TransportationLineConnectivity.OPTIMAL
        elif abs(total_edges - total_disconnected_or_recovering) >= total_edges/3:
            return TransportationLineConnectivity.REGULAR
        else:
            return TransportationLineConnectivity.BAD


def change_utc_timezone(timestamp):
    utc = pytz.timezone("UTC")
    timezone = pytz.timezone("America/Mexico_City")
    date_time = pd.to_datetime(timestamp)
    localized_timestamp = utc.localize(date_time)
    new_timezone = localized_timestamp.astimezone(timezone)
    return new_timezone.strftime('%Y-%m-%d %H:%M:%S')
