from txp.common.timeseries.connectors.bigquery_connector import BigQueryTimeSeries
from txp.common.timeseries.time_series_interval import TimeSeriesInterval
from txp.common.timeseries.temperature_chart import TemperatureChart
from txp.common.timeseries.rpm_chart import RpmChart
from datetime import datetime, timedelta


def get_last_hour_interval():
    start = int(( datetime.now() - timedelta(hours=2) ).timestamp() * 1e6)
    end = int(datetime.now().timestamp() * 1e6)
    return start, end

