import abc
import pandas as pd
from google.oauth2 import service_account
from typing import Dict


class TimeSeriesDbConnector(abc.ABC):
    def __init__(
        self,
        credentials: service_account.Credentials
    ):
        self._credentials: service_account.Credentials = credentials
        self._db = self._get_db_client()

    @abc.abstractmethod
    def _get_db_client(self):
        pass

    @abc.abstractmethod
    def get_metrics_dataframe(
        self,
        time_series_interval: "TimeSeriesInterval"
    ) -> pd.DataFrame:
        pass
