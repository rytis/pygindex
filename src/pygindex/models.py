from enum import Enum, unique


class DocEnum(Enum):
    def __new__(cls, value, doc=None):
        self = object.__new__(cls)  # calling super().__new__(value) here would fail
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
        return self


@unique
class IGPriceResolution(DocEnum):
    """Set of values defining available resolution settings
    when requesting historical price data.

    Resolution means that the returned price values are going to be aggregates
    for the time period specified by the resolution value.

    For example, selecting :enum:`IGPriceResolution.WEEK` will return max/min open/close values for
    each week, whereas :enum:`IGPriceResolution.HOUR_3` will return max/min open/close values for
    every 3 hour period.
    """

    SECOND = "SECOND", "1 second"
    HOUR = "HOUR", "1 hour"
    HOUR_2 = "HOUR_2", "2 hours"
    HOUR_3 = "HOUR_3", "3 hours"
    HOUR_4 = "HOUR_4", "4 hours"
    DAY = "DAY", "1 day"
    WEEK = "WEEK", "1 week"
    MONTH = "MONTH", "1 month"
    MINUTE = "MINUTE", "1 minute"
    MINUTE_2 = "MINUTE_2", "2 minutes"
    MINUTE_3 = "MINUTE_3", "3 minutes"
    MINUTE_5 = "MINUTE_5", "5 minutes"
    MINUTE_10 = "MINUTE_10", "10 minutes"
    MINUTE_15 = "MINUTE_15", "15 minutes"
    MINUTE_30 = "MINUTE_30", "30 minutes"
