import time

from utils.time.Time import Time
from utils.time.TIMEZONE_OFFSET import TIMEZONE_OFFSET


class TimeFormat:
    def __init__(self, format_str: str, timezone_offset=TIMEZONE_OFFSET.LK):
        self.format_str = format_str
        self.timezone_offset = timezone_offset

    @property
    def dut_timezone(self):
        return time.timezone - self.timezone_offset

    def parse(self, time_str: str) -> Time:
        ut_base = time.mktime(time.strptime(time_str, self.format_str))
        ut = ut_base - self.dut_timezone
        return Time(ut)

    def stringify(self, t: Time) -> str:
        return time.strftime(
            self.format_str, time.localtime(t.ut + self.dut_timezone)
        )


TIME_FORMAT_DATE = TimeFormat('%Y-%m-%d')
TIME_FORMAT_TIME = TimeFormat('%Y-%m-%d %H:%M:%S')

TIME_FORMAT_DATE_ID = TimeFormat('%Y%m%d')
TIME_FORMAT_TIME_ID = TimeFormat('%Y%m%d.%H%M%S')
