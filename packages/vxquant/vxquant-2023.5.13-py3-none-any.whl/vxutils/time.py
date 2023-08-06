"""量化交易时间计时器"""


import time
import contextlib
from multiprocessing.dummy import Process, Condition
from typing import Any, Callable, List
from vxutils.convertors import (
    combine_datetime,
    to_timestring,
    to_datetime,
    to_timestamp,
)


__all__ = ["vxtime"]


class _ShowProcessBar(Process):
    def __init__(self, prefix: str, *args, **kwargs) -> None:
        from tqdm import tqdm

        self._is_started = False
        self._prefix = prefix
        self._start_dt = None
        self._keep_waiting = Condition()
        self._pbar = tqdm()
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        self._is_started = True
        self._start_dt = time.perf_counter()
        with self._keep_waiting:
            while self._is_started:
                self._pbar.set_description(
                    f"计时器({self._prefix})  用时"
                    f" {(time.perf_counter()-self._start_dt)*1000:,.2f}ms"
                )
                self._pbar.update()
                self._keep_waiting.wait(1)

    def stop(self) -> None:
        with self._keep_waiting:
            cost_time = (time.perf_counter() - self._start_dt) * 1000
            self._is_started = False
            self._keep_waiting.notify()
            self._pbar.set_description(
                f"计时器({self._prefix}) 用时 {cost_time:,.2f}ms"
            )
            self._pbar.close()
        self.join()
        return cost_time


class vxtime:
    """量化交易时间机器"""

    _timefunc = time.time
    _delayfunc = time.sleep
    __holidays__ = set()
    __businessdays__ = set()

    @classmethod
    def now(cls) -> float:
        """当前时间"""
        return cls._timefunc()

    @classmethod
    def sleep(cls, seconds: float) -> None:
        """延时等待函数"""
        cls._delayfunc(seconds)

    @classmethod
    @contextlib.contextmanager
    def timeit(
        cls, prefix: str = None, show_title: bool = False, show_pbar: bool = False
    ) -> None:
        """计时器"""
        pbar = _ShowProcessBar(prefix or "default")
        pbar.start()
        try:
            yield
        finally:
            pbar.stop()

    @classmethod
    def is_holiday(cls, date_: Any = None) -> bool:
        """是否假日"""
        date_ = date_ if date_ is not None else cls.now()
        if to_datetime(date_).weekday in [0, 1]:
            # 星期六日 均为休息日
            return True

        date_ = to_timestring(date_, "%Y-%m-%d")
        return date_ in cls.__holidays__

    @classmethod
    def set_timefunc(cls, timefunc: Callable) -> None:
        """设置timefunc函数"""
        if not callable(timefunc):
            raise ValueError(f"{timefunc} is not callable.")
        cls._timefunc = timefunc

    @classmethod
    def set_delayfunc(cls, delayfunc: Callable) -> None:
        """设置delayfunc函数"""
        if not callable(delayfunc):
            raise ValueError(f"{delayfunc} is not callable.")
        cls._delayfunc = delayfunc

    @classmethod
    def today(cls, time_str: str = "00:00:00") -> float:
        """今天 hh:mm:ss 对应的时间"""

        date_str = to_timestring(cls.now(), "%Y-%m-%d")
        return combine_datetime(date_str, time_str)

    @classmethod
    def add_holidays(cls, *holidays: List):
        """增加假期时间"""
        if len(holidays) == 1 and isinstance(holidays[0], list):
            holidays = holidays[0]
        cls.__holidays__.update(map(lambda d: to_timestring(d, "%Y-%m-%d"), holidays))

    def get_next_business_day(self, date_: Any = None) -> float:
        """获取下一个交易日"""

        date_ = to_timestamp(date_ if date_ is not None else self.now())

        while self.is_holiday(date_):
            date_ += 24 * 60 * 60
        return date_


if __name__ == "__main__":
    with vxtime.timeit("test2"):
        print(11)
        with vxtime.timeit("step 1"):
            vxtime.sleep(1)
        with vxtime.timeit("step 2"):
            vxtime.sleep(2)

        with vxtime.timeit("setp 3"):
            vxtime.sleep(3)

        with vxtime.timeit("step 4"):
            vxtime.sleep(4)

        vxtime.sleep(0.3)
