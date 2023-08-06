"""baostock数据接口"""

import baostock as bs
import polars as pl
import pandas as pd
from typing import List
from vxquant.model.nomalize import to_symbol
from vxquant.model.typehint import InstrumentType
from vxquant.model.instruments import vxInstruments
from vxquant.providers.base import vxCalendarProvider, vxDownloadInstrumentsProvider
from vxutils import vxtime, to_timestring

# 生成器


def bs_gen(resultdata):
    while (resultdata.error_code == "0") & resultdata.next():
        yield resultdata.get_row_data()


class vxBaoStockCalenderProvider(vxCalendarProvider):
    """baostock 日历接口"""

    def get_trade_dates(self, market: str = "cn") -> List[InstrumentType]:
        try:
            lg = bs.login()
            if lg.error_code != "0":
                raise ConnectionRefusedError(f"登录失败: {lg.error_msg}")

            rs = bs.query_trade_dates(start_date="2005-01-01", end_date="2023-12-31")
            if rs.error_code != "0":
                raise ConnectionError(f"获取交易日历失败: {rs.error_msg}")

            df = pl.DataFrame(list(bs_gen(rs))).transpose()
            df.columns = rs.fields
            return df.filter(pl.col("is_trading_day") == "1").select(
                pl.col("calendar_date").alias("trade_date")
            )["trade_date"]
        finally:
            bs.logout()


class vxBaoStockDownloadInstrumentsProvider(vxDownloadInstrumentsProvider):
    def __call__(self):
        pass

    def get_instruments(self) -> List[vxInstruments]:
        with vxtime.timeit("query_stock_basic"):
            rs = bs.query_stock_basic()
            if rs.error_code != "0":
                raise ConnectionError(f"获取股票基本信息失败: {rs.error_msg}")

            datas = list(bs_gen(rs))
            df = pl.DataFrame(datas).transpose()
            df.columns = rs.fields
        df = df.with_columns(
            [
                pl.col("code").apply(to_symbol).alias("symbol"),
                pl.col("ipoDate").alias("start_date"),
                pl.when(pl.col("outDate") == "")
                .then(to_timestring(vxtime.today(), "%Y-%m-%d"))
                .otherwise(pl.col("outDate"))
                .alias("end_date"),
                pl.lit(1).alias("weight"),
            ]
        ).select(["symbol", "start_date", "end_date", "weight", "type"])

        cnstocks = vxInstruments(
            "cnstocks",
            df.filter(pl.col("type") == "1").select(
                [
                    "symbol",
                    "start_date",
                    "end_date",
                    "weight",
                ]
            ),
        )
        cncbonds = vxInstruments(
            "cncbonds",
            df.filter(pl.col("type") == "4").select(
                [
                    "symbol",
                    "start_date",
                    "end_date",
                    "weight",
                ]
            ),
        )
        cnindexes = vxInstruments(
            "cnindexes",
            df.filter(pl.col("type") == "2").select(
                ["symbol", "start_date", "end_date", "weight"]
            ),
        )
        cnetflofs = vxInstruments(
            "cnetflofs",
            df.filter(pl.col("type") == "5").select(
                ["symbol", "start_date", "end_date", "weight"]
            ),
        )
        return [cncbonds, cnstocks, cnindexes, cnetflofs]


if __name__ == "__main__":
    c = vxBaoStockCalenderProvider()

    # with vxtime.timeit():
    # d = c.get_trade_dates()
    # print(d)
    bs.login()
    with vxtime.timeit():
        rs = bs.query_stock_basic()
    # rs = bs.query_all_stock(day="2021-01-04")
    datas = list(bs_gen(rs))
    df = pl.DataFrame(datas).transpose()
    df.columns = rs.fields
    df = df.with_columns(
        [
            pl.col("code").apply(to_symbol).alias("symbol"),
            pl.col("ipoDate").alias("start_date"),
            pl.when(pl.col("outDate") == "")
            .then(to_timestring(vxtime.today(), "%Y-%m-%d"))
            .otherwise(pl.col("outDate"))
            .alias("end_date"),
            pl.lit(1).alias("weights"),
        ]
    ).select(["symbol", "start_date", "end_date", "weights", "type"])
    cnstocks = vxInstruments(
        "cnstocks",
        df.filter(pl.col("type") == "4").select(
            [
                "symbol",
                "start_date",
                "end_date",
                "weights",
            ]
        ),
    )
    all_cnbonds = cnstocks.list_instruments()
    print(len(all_cnbonds))
    #

    bs.logout()
