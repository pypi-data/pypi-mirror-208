# encoding=utf8
""" 通达信数据转换 """
import datetime
from enum import Enum
from pytdx.hq import TDXParams
from vxutils.dataclass import vxDataConvertor
from vxquant.model.exchange import vxTick, vxBar
from vxquant.model.preset import vxMarketPreset
from vxquant.model.contants import SecType


class TdxExchange(Enum):
    """通达信交易所代码"""

    SHSE = TDXParams.MARKET_SH
    SZSE = TDXParams.MARKET_SZ
    BJSE = 2


# * #####################################################################
# * tdxTick的转换器
# * #####################################################################
TICK_TRANS = {
    "volume": "vol",
}


def tdx_to_timestamp(tdx_timestamp, trade_day=None):
    """通达信时间戳转换为时间戳"""
    if trade_day is None:
        trade_day = datetime.datetime.now()

    tdx_timestamp = f"{tdx_timestamp:0>8}"
    hour = int(tdx_timestamp[:2])
    if hour < 0 or hour > 23:
        tdx_timestamp = f"0{tdx_timestamp}"
        hour = int(tdx_timestamp[:2])

    minute = int(tdx_timestamp[2:4])
    percent = float(f"0.{tdx_timestamp[2:]}")
    if minute < 60:
        second = int(percent * 60)
        microsecond = int((percent * 60 - second) * 1000)
    else:
        minute = int(percent * 60)
        second = int((percent * 60 - minute) * 60)
        microsecond = int(((percent * 60 - minute) * 60 - second) * 1000)
    return datetime.datetime(
        trade_day.year,
        trade_day.month,
        trade_day.day,
        hour,
        minute,
        second,
        microsecond,
    ).timestamp()


def _quote_convter(cnt, volunit, price_unit=None):
    if price_unit is None:
        price_unit = volunit
    return {
        f"bid{cnt}_v": lambda x: x[f"bid_vol{cnt}"] * volunit,
        f"bid{cnt}_p": lambda x: x[f"bid{cnt}"] / 100 * price_unit,
        f"ask{cnt}_v": lambda x: x[f"ask_vol{cnt}"] * volunit,
        f"ask{cnt}_p": lambda x: x[f"ask{cnt}"] / 100 * price_unit,
    }


# 非可转债转化
TDX_STOCK_TICK_CONVERTORS = {
    "volume": lambda x: x["vol"] * 100,
    "symbol": lambda x: f"{TdxExchange(x['market']).name}.{x['code']}",
    "yclose": lambda x: round(x["last_close"], 4),
    "open": lambda x: round(x["open"], 4),
    "high": lambda x: round(x["high"], 4),
    "low": lambda x: round(x["low"], 4),
    "lasttrade": lambda x: round(x["price"], 4) or round(x["last_close"], 4),
    "created_dt": lambda x: tdx_to_timestamp(x["reversed_bytes0"]),
}

tdxStockTickConvter = vxDataConvertor(vxTick, TDX_STOCK_TICK_CONVERTORS)


for i in range(1, 6):
    for k, v in _quote_convter(i, 100).items():
        tdxStockTickConvter.add_convertors(k, v)


# 可转债转化
TDX_CBOND_TICK_CONVERTORS = {
    "volume": lambda x: x["vol"] * 100,
    "symbol": lambda x: f"{TdxExchange(x['market']).name}.{x['code']}",
    "yclose": lambda x: round(x["last_close"] / 100, 4),
    "open": lambda x: round(x["open"] / 100, 4),
    "high": lambda x: round(x["high"] / 100, 4),
    "low": lambda x: round(x["low"] / 100, 4),
    "lasttrade": lambda x: round(x["price"] / 100, 4) or round(
        x["last_close"] / 100, 4
    ),
    "created_dt": lambda x: tdx_to_timestamp(x["reversed_bytes0"]),
}

tdxConBondTickConvter = vxDataConvertor(vxTick, TDX_CBOND_TICK_CONVERTORS)

for i in range(1, 6):
    for k, v in _quote_convter(i, 1).items():
        tdxConBondTickConvter.add_convertors(k, v)


# ETFLOF
TDX_ETFLOF_TICK_CONVERTORS = {
    "volume": lambda x: x["vol"] * 100,
    "symbol": lambda x: f"{TdxExchange(x['market']).name}.{x['code']}",
    "yclose": lambda x: round(x["last_close"] / 10, 4),
    "open": lambda x: round(x["open"] / 10, 4),
    "high": lambda x: round(x["high"] / 10, 4),
    "low": lambda x: round(x["low"] / 10, 4),
    "lasttrade": lambda x: round(x["price"] / 10, 4) or round(x["last_close"] / 100, 4),
    "created_dt": lambda x: tdx_to_timestamp(x["reversed_bytes0"]),
}
tdxETFLOFTickConvter = vxDataConvertor(vxTick, TDX_ETFLOF_TICK_CONVERTORS)

for i in range(1, 6):
    for k, v in _quote_convter(i, 100, 10).items():
        tdxETFLOFTickConvter.add_convertors(k, v)


def tdxTickConvter(tdxtick, key=""):
    """转化为vxtick格式

    Arguments:
        tdxtick {_type_} -- tdx tick格式
    """

    symbol = f"{TdxExchange(tdxtick['market']).name}.{tdxtick['code']}"
    _preset = vxMarketPreset(symbol)

    if _preset.security_type in (
        SecType.BOND_CONVERTIBLE,
        SecType.BOND,
        SecType.REPO,
    ):
        return tdxConBondTickConvter(tdxtick, key="symbol")
    elif _preset.security_type in (SecType.ETFLOF, SecType.CASH):
        return tdxETFLOFTickConvter(tdxtick, key="symbol")
    else:
        return tdxStockTickConvter(tdxtick, key="symbol")


# * #####################################################################
# * tdxBar的转换器
# * #####################################################################
BAR_TRANS = {
    "close": "price",
    "volume": "vol",
    "created_dt": "created_at",
}


# TDXParams.KLINE_TYPE_1MIN
# TDXParams.KLINE_TYPE_DAILY

tdxBarConvter = vxDataConvertor(vxBar, BAR_TRANS)
# tdxBarConvter.add_convertors('created_at', lambda x: time.strptime(x['datetime'],'%Y-%m-%d %H:%M:%S')
# tdxBarConvter.add_convertors('created_at', conveter_func)
