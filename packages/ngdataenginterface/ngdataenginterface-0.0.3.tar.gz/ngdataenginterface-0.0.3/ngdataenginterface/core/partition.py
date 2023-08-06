from datetime import datetime, timedelta

PARTITION_MAP = {
    "part_year": lambda dt: dt.strftime("%Y"),
    "part_month": lambda dt: dt.strftime("%m"),
    "part_day": lambda dt: dt.strftime("%d"),
    "part_hour": lambda dt: dt.strftime("%H"),
}


def handle_partition_path(partition: str, date) -> str:
    """Constructs the partition path from each partition and current execution date

    Parameters
    ----------
    partition : str
        String which contains the description of each partition of the table following
    the standard `part_year`, `part_month`, ...
    date : dict
        Date used to construct the partition path

    Returns
    -------
    str
        the resulting partition path
    """

    partition_path = ""

    # iterates on each partition
    for part in partition.split("/"):
        # constructs the partition path from 'ref_date'
        partition_path += part + "=" + PARTITION_MAP[part](date) + "/"

    # returns the partition_path without last '/' charactere
    return partition_path[:-1]

def get_year_month_day(execution_date: datetime):
    year = execution_date.strftime("%Y")
    month = execution_date.strftime("%m")
    day = execution_date.strftime("%d")
    return year, month, day

def get_last_partition(execution_date: datetime):
    previous_year, previous_month, previous_day = get_year_month_day(
        datetime(execution_date.year, execution_date.month, execution_date.day)
        - timedelta(days=1)
    )
    return datetime(int(previous_year), int(previous_month), int(previous_day))