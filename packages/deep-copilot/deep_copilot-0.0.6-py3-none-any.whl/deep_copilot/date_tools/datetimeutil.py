import datetime
import random
import time
import typing as typ
from deep_copilot.log_tools.log_tool import logger

STANDARD_FORMAT = '%Y-%m-%d %H:%M:%S'
COMPACT_FORMAT = '%Y%m%d%H%M%S'


def second_to_millis(n: typ.Union[int, float]) -> int:
    return int(n * 1000) if n else 0


def unix_timestamp_to_datetime(t: typ.Union[int, str],
                               dt_format: typ.Optional[str] = None) -> typ.Union[datetime.datetime, str]:
    # 固定使用中文时区吧
    dt = datetime.datetime.fromtimestamp(int(t), tz=datetime.timezone(datetime.timedelta(hours=8)))
    return dt if dt_format is None else dt.strftime(dt_format)


def datetime_to_unix_timestamp_millis(dt: datetime.datetime) -> int:
    return second_to_millis(dt.timestamp())


def reformat(s: str, old_format: str, new_format: str) -> str:
    dt = datetime.datetime.strptime(s, old_format)
    return dt.strftime(new_format)


def sleep_millis(ms: int = 0, min_ms: int = 0, max_ms: int = 0) -> None:
    if ms > 0:
        time.sleep(ms / 1000.0)
    else:
        if min_ms < 0:
            min_ms = 0
        if max_ms < 0:
            max_ms = 0
        if min_ms > max_ms:
            min_ms, max_ms = max_ms, min_ms
        if min_ms > 0 or max_ms > 0:
            if min_ms == max_ms:
                time.sleep(ms / 1000.0)
            else:
                time.sleep(random.randint(min_ms, max_ms) / 1000.0)


def second_to_hms(n: typ.Union[int, float]) -> str:
    m, s = divmod(n, 60)
    h, m = divmod(m, 60)
    return '{}:{}:{}'.format(int(h), int(m), float(s))


def hms_to_second(t: str) -> float:
    """
    例如 20:10:07 20点10分7秒转成秒
    :param t: 时间 以 ： 分割
    :return:
    """
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def time_record(function):
    """
    装饰器函数time_record
    :param function:想要计时的函数
    :return:
    """

    def wrapper(*args, **kwargs):
        time_start = time.time()
        res = function(*args, **kwargs)
        cost_time = time.time() - time_start
        logger.info("【%s】运行时间：【%s】秒" % (function.__name__, cost_time))
        return res

    return wrapper
