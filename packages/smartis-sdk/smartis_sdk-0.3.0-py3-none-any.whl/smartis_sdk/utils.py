from datetime import datetime

Y_M_D = "%Y-%m-%d"


def normalize_date(date: str | datetime) -> str:
    return date.strftime(Y_M_D) if type(date) == datetime else date
