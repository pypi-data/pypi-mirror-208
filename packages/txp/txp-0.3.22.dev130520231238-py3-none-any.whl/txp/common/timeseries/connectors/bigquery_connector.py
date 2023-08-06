import time
from datetime import datetime, timedelta

from google.cloud import bigquery
from txp.common.timeseries.connectors.connector import TimeSeriesDbConnector
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
from typing import Dict
import pandas as pd
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class BigQueryTimeSeries(TimeSeriesDbConnector):
    def __init__(
            self,
            credentials: service_account.Credentials
    ):
        super(BigQueryTimeSeries, self).__init__(
            credentials
        )

    @classmethod
    def _metrics_bigquery_parameters(cls):
        return {
            "dataset": "telemetry",
            "table": "vibration"
        }

    def _get_db_client(self) -> bigquery.Client:
        try:
            # Create a BigQuery client
            client = bigquery.Client(credentials=self._credentials)
            return client
        except DefaultCredentialsError as e:
            # Handle authentication errors
            log.error(f"Unable to authenticate creating "
                      f"BigQuery client: {e}")
            raise e
        except Exception as e:
            # Handle other possible errors
            log.error(f"Unexpected error authenticating BigQuery: {e}")
            raise e

    def _get_partition_utc_date(self, observation_timestamp):
        partition_timestamp = datetime.utcfromtimestamp(observation_timestamp // 1e6)
        partition_timestamp = partition_timestamp - timedelta(minutes=partition_timestamp.minute,
                                                              seconds=partition_timestamp.second)
        return partition_timestamp

    def _pull_metrics_df(self, values: Dict):
        start_datetime = self._get_partition_utc_date(
            values["start_time"]
        )
        end_datetime = self._get_partition_utc_date(
            values["end_time"]
        )

        # Set columns
        if values["columns"]:
            columns = ",".join(values["columns"])
        else:
            columns = "*"

        select_query = f"""
            SELECT {columns} FROM `{values["table_full_name"]}`
            WHERE partition_timestamp >= "{start_datetime}" 
            AND partition_timestamp <= "{end_datetime}"
            AND tenant_id = "{values["tenant_id"]}"
            AND asset_id = "{values["asset_id"]}"
            AND perception_name = "{values["perception"]}"
            ORDER BY observation_timestamp ASC;
        """
        start = time.time()
        df = (self._db.query(select_query).result().to_dataframe())
        end = time.time()
        print(select_query)
        log.info(f"This query took: {end - start} seconds for metrics: "
                 f"Asset:{values['asset_id']}")

        return df

    def get_metrics_dataframe(
            self,
            time_series_interval: "TimeSeriesInterval",
    ) -> pd.DataFrame:
        query_params: Dict = self._metrics_bigquery_parameters()
        d = {
            "start_time": time_series_interval.start_timestamp,
            "end_time": time_series_interval.end_timestamp,
            "bigquery_dataset": query_params["dataset"],
            "bigquery_table": query_params["table"],
            "tenant_id": time_series_interval.tenant_id,
            "asset_id": time_series_interval.asset_id,
            "perception": time_series_interval.perception,
            "table_full_name": f"{query_params['dataset']}.{query_params['table']}",
            "columns": time_series_interval.columns
        }
        df = self._pull_metrics_df(d)
        return df
