""" QMT量化数据转换至vxFinDataModel数据的转换器 """

import uuid
from vxutils import combine_datetime, to_timestring, vxtime, vxDataConvertor, to_text

from vxquant.model.exchange import (
    vxCashPosition,
    vxTick,
    vxBar,
    vxPosition,
    vxOrder,
    vxTrade,
    vxAccountInfo,
)
from vxquant.model.preset import vxMarketPreset
from vxquant.model.nomalize import to_symbol

__all__ = [
    "qmtTickConvter",
    # "qmtBarConvter",
    "qmtAccountInfoConvter",
    "qmtCashPositionConvter",
    "qmtPositionConvter",
    "qmtOrderConvter",
    "qmtTradeConvter",
]


TICK_CONVERTORS = {
    # 证券标的
    "symbol": "symbol",
    # 开盘价
    "open": "open",
    # 最高价
    "high": "high",
    # 最低价
    "low": "low",
    # 最近成交价
    "lasttrade": "lastPrice",
    # 昨日收盘价
    "yclose": "lastClose",
    # 成交量
    "volume": "volume",
    # 成交金额
    "amount": "amount",
    # 换手率
    "turnoverratio": lambda x: 0.0,
    # 卖1量
    "bid1_v": lambda x: x["bidVol"][0],
    # 卖1价
    "bid1_p": lambda x: x["bidPrice"][0],
    # 卖2量
    "bid2_v": lambda x: x["bidVol"][1],
    # 卖2价
    "bid2_p": lambda x: x["bidPrice"][1],
    # 卖3量
    "bid3_v": lambda x: x["bidVol"][2],
    # 卖3价
    "bid3_p": lambda x: x["bidPrice"][2],
    # 卖4量
    "bid4_v": lambda x: x["bidVol"][3],
    # 卖4价
    "bid4_p": lambda x: x["bidPrice"][3],
    # 卖5量
    "bid5_v": lambda x: x["bidVol"][4],
    # 卖5价
    "bid5_p": lambda x: x["bidPrice"][4],
    # 买1量
    "ask1_v": lambda x: x["askVol"][0],
    # 买1价
    "ask1_p": lambda x: x["askPrice"][0],
    # 买2量
    "ask2_v": lambda x: x["askVol"][1],
    # 买2价
    "ask2_p": lambda x: x["askPrice"][1],
    # 买3量
    "ask3_v": lambda x: x["askVol"][2],
    # 买3价
    "ask3_p": lambda x: x["askPrice"][2],
    # 买4量
    "ask4_v": lambda x: x["askVol"][3],
    # 买4价
    "ask4_p": lambda x: x["askPrice"][3],
    # 买5量
    "ask5_v": lambda x: x["askVol"][4],
    # 买5价
    "ask5_p": lambda x: x["askPrice"][4],
    # 持仓量
    "interest": "openInt",
    # 停牌状态
    "status": lambda x: "NORMAL",
    # 创建时间
    "created_dt": "timetag",
    # 更新时间
    "updated_dt": "timetag",
}

qmtTickConvter = vxDataConvertor(vxTick, TICK_CONVERTORS)


def _to_order_direction(other_data):
    return "Buy" if other_data.order_type in (23, 27, 40) else "Sell"


def _to_order_offset(other_data):
    return "Open" if other_data.order_type in (23, 27, 40) else "Close"


def _to_order_type(other_data):
    return "Limit" if other_data.price_type in (11,) else "Market"


def _to_order_status(other_data):
    order_code = other_data.order_status
    if order_code in (48, 49):
        return "PendingNew"
    elif order_code in (50, 51):
        return "New"
    elif order_code in (52, 55):
        return "PartiallyFilled"
    elif order_code in (53, 54):
        return "Canceled"
    elif order_code in (56,):
        return "Filled"
    elif order_code in (57,):
        return "Rejected"
    else:
        return "Unknown"


ORDER_CONVERTORS = {
    # 账号id
    "account_id": "account_id",
    # 委托id
    "order_id": lambda x: x.order_remark + x.strategy_name,
    # 算法委托id
    "algo_order_id": "",
    # 交易所委托id
    "exchange_order_id": lambda x: f"qmt_{x.order_id}",
    # 冻结持仓id
    "frozen_position_id": lambda x: "",
    # 证券代码
    "symbol": "stock_code",
    # 买卖方向
    "order_direction": _to_order_direction,
    # 开平仓标志
    "order_offset": _to_order_offset,
    # 订单类型
    "order_type": _to_order_type,
    # 委托数量
    "volume": "order_volume",
    # 委托价格
    "price": "price",
    # 成交数量
    "filled_volume": "traded_volume",
    # 成交均价
    "filled_vwap": "trade_price",
    # 成交总额（含手续费）
    "filled_amount": lambda x: x.traded_volume * x.traded_price,
    # 订单状态
    "status": _to_order_status,
    # 订单超时时间
    "due_dt": lambda x: combine_datetime(x.order_time, "15:00:00"),
    # 拒绝代码
    "reject_code": "status_msg",
    # 拒绝原因
    "reject_reason": "status_msg",
    # 创建时间
    "created_dt": "order_time",
    # 更新时间
    "updated_dt": "order_time",
}


qmtOrderConvter = vxDataConvertor(vxOrder, ORDER_CONVERTORS)


TRADE_CONVERTORS = {
    # 账户id
    "account_id": "account_id",
    # 委托id
    "order_id": lambda x: x.order_remark + x.strategy_name,
    # 交易所委托id
    "exchange_order_id": lambda x: f"qmt_{x.order_id}",
    # 成交id
    "trade_id": "traded_id",
    # 证券代码
    "symbol": "stock_code",
    # 买卖方向
    "order_direction": _to_order_direction,
    # 开平仓标志
    "order_offset": _to_order_offset,
    # 成交价格
    "price": "traded_price",
    # 成交数量
    "volume": "traded_volume",
    # 交易佣金
    "commission": lambda x: x.traded_amount - x.traded_price * x.traded_volume,
    # 成交状态
    "status": lambda x: "Trade" if x.traded_volume > 0 else "Unknown",
    # 拒绝代码
    "reject_code": lambda x: "Unkown",
    # 拒绝原因
    "reject_reason": lambda x: "",
    # 成交时间
    "created_dt": "trade_time",
    # 更新时间
    "updated_dt": "trade_time",
}

qmtTradeConvter = vxDataConvertor(vxTrade, TRADE_CONVERTORS)


POSITION_CONVERTORS = {
    # 组合ID
    "portfolio_id": lambda x: "",
    # 账户id
    "account_id": "account_id",
    # 仓位id
    "position_id": lambda x: str(uuid.uuid4()),
    # 证券类型
    "security_type": lambda x: vxMarketPreset(to_symbol(x.stock_code)).security_type,
    # 证券代码
    "symbol": "stock_code",
    # 持仓方向
    "position_side": lambda x: "Long",
    # 今日持仓数量
    "volume_today": lambda x: x.volume - x.frozen_volume - x.can_use_volume,
    # 昨日持仓数量
    "volume_his": lambda x: x.frozen_volume + x.can_use_volume,
    # 持仓数量 --- 自动计算字段，由 volume_today + volume_his 计算所得
    "volume": "volume",
    # 冻结数量
    "frozen": lambda x: x.volume - x.can_use_volume,
    # 可用数量  --- 自动计算字段，由 volume - frozen计算
    "available": "can_use_volume",
    # 持仓市值
    "marketvalue": "market_value",
    # 持仓成本
    "cost": lambda x: x.open_price * x.volume,
    # 浮动盈利
    "fnl": lambda x: x.market_value - x.open_price * x.volume,
    # 持仓成本均价
    "vwap": "open_price",
    # 最近成交价
    "lasttrade": lambda x: x.market_value / x.volume,
    # 是否T0
    "allow_t0": lambda x: vxMarketPreset(to_symbol(x.stock_code)).allow_t0,
}

qmtPositionConvter = vxDataConvertor(vxPosition, POSITION_CONVERTORS)

CASHPOSITION_CONVERTORS = {
    # 组合ID
    "portfolio_id": lambda x: "",
    # 账户id
    "account_id": "account_id",
    # 仓位id
    "position_id": lambda x: str(uuid.uuid4()),
    # 证券类型
    "security_type": lambda x: "CASH",
    # 证券代码
    "symbol": lambda x: "CNY",
    # 持仓方向
    "position_side": lambda x: "Long",
    # 今日持仓数量
    "volume_today": "frozen_cash",
    # 昨日持仓数量
    "volume_his": "cash",
    # 持仓数量
    "volume": lambda x: x.frozen_cash + x.cash,
    # 冻结数量
    "frozen": "frozen_cash",
    # 可用数量
    "available": "cash",
    # 持仓市值
    "marketvalue": lambda x: x.frozen_cash + x.cash,
    # 持仓成本
    "cost": lambda x: x.frozen_cash + x.cash,
    # 浮动盈利
    "fnl": lambda x: 0.0,
    # 持仓成本均价
    "vwap": lambda x: 1.0,
    # 最近成交价
    "lasttrade": lambda x: 1.0,
    # 是否T0
    "allow_t0": lambda x: True,
}

qmtCashPositionConvter = vxDataConvertor(vxCashPosition, CASHPOSITION_CONVERTORS)

ACCOUNTINFO_CONVERTORS = {
    # 组合ID
    "portfolio_id": lambda x: "",
    # 账户id
    "account_id": "account_id",
    # 账户币种
    "currency": lambda x: "CNY",
    # 今日转入金额
    "deposit": lambda x: 0.0,
    # 今日转出金额
    "withdraw": lambda x: 0.0,
    # 总资产
    "asset": "total_asset",
    # 净资产
    "nav": "total_asset",
    # 总负债
    "debt": lambda x: 0.0,
    # 资金余额
    "balance": lambda x: x.cash + x.frozen_cash,
    # 冻结金额
    "frozen": "frozen_cash",
    # 可用金额
    "available": "cash",
    # 融资融券可用
    "margin_available": lambda x: 0.0,
    # 总市值
    "marketvalue": "market_value",
    # 今日盈利
    "today_profit": lambda x: 0.0,
    # 浮动盈亏
    "fnl": lambda x: 0.0,
    # 基金份额
    "fund_shares": "total_asset",
    # 基金净值估算
    "fund_nav": lambda x: 1.0,
    # 昨日总资产
    "asset_yd": "total_asset",
    # 昨日净资产
    "nav_yd": "total_asset",
    # 昨日基金金额
    "fund_nav_yd": lambda x: 1.0,
    # 最近结算日
    "settle_day": lambda: vxtime.today("23:59:59") - 24 * 60 * 60,
    # 下单channel
    "channel": lambda x: "",
}

qmtAccountInfoConvter = vxDataConvertor(vxAccountInfo, ACCOUNTINFO_CONVERTORS)


CREDIT_ACCOUNTINFO_CONVERTORS = {
    # 组合ID
    "portfolio_id": lambda x: "",
    # 账户id
    "account_id": "m_strAccountID",
    # 账户币种
    "currency": lambda x: "CNY",
    # 今日转入金额
    "deposit": lambda x: 0.0,
    # 今日转出金额
    "withdraw": lambda x: 0.0,
    # 总资产
    "asset": "m_dBalance",
    # 净资产
    "nav": "m_dAssureAsset",
    # 总负债
    "debt": "m_dTotalDebt",
    # 资金余额
    "balance": lambda x: x.cash + x.frozen_cash,
    # 冻结金额
    "frozen": "m_dFrozenCash",
    # 可用金额
    "available": "m_dAvailable",
    # 融资融券可用
    "margin_available": "m_dEnableBailBalance",
    # 总市值
    "marketvalue": "m_dMarketValue",
    # 今日盈利
    "today_profit": lambda x: 0.0,
    # 浮动盈亏
    "fnl": "m_dPositionProfit",
    # 基金份额
    "fund_shares": "m_dBalance",
    # 基金净值估算
    "fund_nav": lambda x: 1.0,
    # 昨日总资产
    "asset_yd": "m_dBalance",
    # 昨日净资产
    "nav_yd": "m_dBalance",
    # 昨日基金金额
    "fund_nav_yd": lambda x: 1.0,
    # 最近结算日
    "settle_day": lambda: vxtime.today("23:59:59") - 24 * 60 * 60,
    # 下单channel
    "channel": lambda x: "",
}

qmtCreditAccountInfoConvter = vxDataConvertor(
    vxAccountInfo, CREDIT_ACCOUNTINFO_CONVERTORS
)
