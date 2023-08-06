import datetime
import dataclasses
import abc
from typing import List
from enum import Enum


class VibrationIntervalOption(Enum):
    FULL_DETAILED = ("detailed", "Detallado")
    HOURLY_AVG = ("hourly_avg", "Promedio cada hora")
    # WEEKLY = ("weekly", "Semanal")

    def __init__(self, value: str, readable: str):
        self._value_ = value
        self.readable = readable

    @classmethod
    def from_readable(cls, readable_value):
        for option in cls:
            if option.readable == readable_value:
                return option
        raise ValueError(
            f"No {cls.__name__} option with readable value {readable_value!r}"
        )


@dataclasses.dataclass
class TimeSeriesInterval:
    """Helper class to wrap time series values"""

    start_timestamp: int
    end_timestamp: int
    tenant_id: str
    asset_id: str
    perception: str
    columns: List[str] = dataclasses.field(
        default_factory=list
    )  # Represents the columns that we want to download

    def __post_init__(self):
        self.start_datetime = datetime.datetime.fromtimestamp(
            self.start_timestamp // 1e6
        )
        self.end_datetime = datetime.datetime.fromtimestamp(self.end_timestamp // 1e6)

    def diff(self):
        """
        Returns the absoulute value of the interval in seconds
        """
        return (self.end_datetime - self.start_datetime).total_seconds()
