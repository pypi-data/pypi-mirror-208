from utils.time.Time import Time
from utils.time.TimeFormat import TIME_FORMAT_DATE_ID, TIME_FORMAT_TIME_ID


def get_time_id():
    return TIME_FORMAT_TIME_ID.stringify(Time.now())


def get_date_id():
    return TIME_FORMAT_DATE_ID.stringify(Time.now())
