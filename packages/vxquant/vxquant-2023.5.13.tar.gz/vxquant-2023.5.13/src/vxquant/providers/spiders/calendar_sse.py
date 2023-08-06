"""交易日期基础接口"""

import requests
import random
import datetime
from itertools import product
from typing import List
from tqdm import tqdm
from vxutils import vxtime, logger, to_datetime
from vxquant.model.typehint import DateTimeType
from vxquant.providers.base import vxCalendarProvider

SSE_CALENDAR_LIST = "http://www.szse.cn/api/report/exchange/onepersistenthour/monthList?month={year}-{month}&random={timestamp}"


class CNCalenderProvider(vxCalendarProvider):
    def get_trade_dates(
        self,
        market: str = "cn",
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
    ) -> List:
        if market != "cn":
            raise NotImplementedError(f"暂不支持 {market}类型")

        start_date = to_datetime(start_date) or datetime.datetime(2005, 1, 1)
        end_date = to_datetime(end_date) or datetime.datetime.now().replace(
            month=12, day=31, hour=0, minute=0, second=0
        )

        cals = []

        for year, month in tqdm(
            product(range(start_date.year, end_date.year + 1), range(1, 13)),
            desc=f"获取{start_date.year}年交易日历...",
        ):
            url = SSE_CALENDAR_LIST.format(
                year=year, month=month, timestamp=random.randint(100000, 10000000)
            )
            resp = requests.get(url, timeout=1)
            resp.raise_for_status()
            reply = resp.json()
            if "data" in reply and reply["data"]:
                try:
                    cals.extend(
                        [
                            trade_date["jyrq"]
                            for trade_date in reply["data"]
                            if trade_date["jybz"] == "1"
                        ]
                    )
                except Exception as e:
                    logger.error(f"{year}-{month} get calendar {reply} error: {e}")
                vxtime.sleep(0.1)
        return sorted(cals)
