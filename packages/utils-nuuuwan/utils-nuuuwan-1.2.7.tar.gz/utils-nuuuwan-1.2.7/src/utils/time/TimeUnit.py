class TimeUnit:
    def __init__(self, seconds: int):
        self.seconds = seconds

    def __truediv__(self, other):
        if isinstance(other, TimeUnit):
            return self.seconds / other.seconds
        if isinstance(other, float) or isinstance(other, int):
            return TimeUnit(self.seconds / other)
        raise TypeError(
            f'unsupported operand type(s) for /: {type(self)} and {type(other)}'
        )

    def __mul__(self, other):
        return TimeUnit(self.seconds * other)

    def __eq__(self, other):
        if isinstance(other, TimeUnit):
            return self.seconds == other.seconds
        return False


SECOND = TimeUnit(1)
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
FORTNIGHT = WEEK * 7

AVG_YEAR = DAY * 365.25
AVG_QTR = AVG_YEAR / 4
AVG_MONTH = AVG_YEAR / 12


class SECONDS_IN:
    MINUTE = MINUTE / SECOND
    HOUR = HOUR / SECOND
    DAY = DAY / SECOND
    WEEK = WEEK / SECOND
    FORTNIGHT = FORTNIGHT / SECOND

    AVG_MONTH = AVG_MONTH / SECOND
    AVG_QTR = AVG_QTR / SECOND
    AVG_YEAR = AVG_YEAR / SECOND


class DAYS_IN:
    AVG_MONTH = AVG_MONTH / DAY
    AVG_QTR = AVG_QTR / DAY
    AVG_YEAR = AVG_YEAR / DAY
