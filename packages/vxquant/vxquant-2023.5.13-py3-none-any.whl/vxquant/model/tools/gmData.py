""" 掘金量化数据转换至vxFinDataModel数据的转换器 """


from vxutils import combine_datetime, to_timestring, vxtime, vxDataConvertor, to_text
from vxquant.model.contants import PositionSide
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

__all__ = [
    "gmTickConvter",
    "gmBarConvter",
    "gmAccountinfoConvter",
    "update_gmcredit_cash",
    "gmCashPositionConvter",
    "gmPositionConvter",
    "gmOrderConvter",
    "gmTradeConvter",
]

# * #####################################################################
# * gmTick的转换器
# * #####################################################################

GM_TICK_CONVERTORS = {
    # 证券标的
    "symbol": "symbol",
    # 开盘价
    "open": "open",
    # 最高价
    "high": "high",
    # 最低价
    "low": "low",
    # 最近成交价
    "lasttrade": "price",
    # 昨日收盘价
    "yclose": lambda x: 0,
    # 成交量
    "volume": "cum_volume",
    # 成交金额
    "amount": "cum_amount",
    # 换手率
    "turnoverratio": lambda x: 0,
    # 卖1量
    "bid1_v": lambda x: x["quotes"][0]["bid_v"],
    # 卖1价
    "bid1_p": lambda x: x["quotes"][0]["bid_p"],
    # 卖2量
    "bid2_v": lambda x: x["quotes"][1]["bid_v"],
    # 卖2价
    "bid2_p": lambda x: x["quotes"][1]["bid_p"],
    # 卖3量
    "bid3_v": lambda x: x["quotes"][2]["bid_v"],
    # 卖3价
    "bid3_p": lambda x: x["quotes"][2]["bid_p"],
    # 卖4量
    "bid4_v": lambda x: x["quotes"][3]["bid_v"],
    # 卖4价
    "bid4_p": lambda x: x["quotes"][3]["bid_p"],
    # 卖5量
    "bid5_v": lambda x: x["quotes"][4]["bid_v"],
    # 卖5价
    "bid5_p": lambda x: x["quotes"][4]["bid_p"],
    # 买1量
    "ask1_v": lambda x: x["quotes"][0]["ask_v"],
    # 买1价
    "ask1_p": lambda x: x["quotes"][0]["ask_p"],
    # 买2量
    "ask2_v": lambda x: x["quotes"][1]["ask_v"],
    # 买2价
    "ask2_p": lambda x: x["quotes"][1]["ask_p"],
    # 买3量
    "ask3_v": lambda x: x["quotes"][2]["ask_v"],
    # 买3价
    "ask3_p": lambda x: x["quotes"][2]["ask_p"],
    # 买4量
    "ask4_v": lambda x: x["quotes"][3]["ask_v"],
    # 买4价
    "ask4_p": lambda x: x["quotes"][3]["ask_p"],
    # 买5量
    "ask5_v": lambda x: x["quotes"][4]["ask_v"],
    # 买5价
    "ask5_p": lambda x: x["quotes"][4]["ask_p"],
    # 持仓量
    "interest": lambda x: 0,
    # 停牌状态
    "status": lambda x: "NORMAL",
    # 发生事件
    "created_dt": "created_at",
    # 更新时间
    "updated_dt": "created_at",
}

gmTickConvter = vxDataConvertor(vxTick, GM_TICK_CONVERTORS)


# * #####################################################################
# * gmBar的转换器
# * #####################################################################
BAR_TRANS = {"yclose": "pre_close", "created_dt": "eob"}
gmBarConvter = vxDataConvertor(vxBar, BAR_TRANS)

# * #####################################################################
# * vxAccountInfo 的转换器
# * #####################################################################

GM_ACCOUNTINFO_CONVERTORS = {
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
    "asset": "nav",
    # 净资产
    "nav": "nav",
    # 总负债
    "debt": lambda x: 0.0,
    # 资金余额
    "balance": lambda x: x.order_frozen + x.available,
    # 冻结金额
    "frozen": "order_frozen",
    # 可用金额
    "available": lambda x: 0.0,
    # 融资融券可用
    "margin_available": lambda x: 0.0,
    # 总市值
    "marketvalue": "market_value",
    # 今日盈利
    "today_profit": lambda x: 0.0,
    # 浮动盈亏
    "fnl": "fpnl",
}


gmAccountinfoConvter = vxDataConvertor(vxAccountInfo, GM_ACCOUNTINFO_CONVERTORS)


def update_gmcredit_cash(vxdatadict, gmCreditCash):
    """更新负债信息"""
    vxdatadict["marketvalue_short"] = gmCreditCash["dealfmktavl"]
    vxdatadict["debt_long"] = gmCreditCash["ftotaldebts"]
    vxdatadict["debt_short"] = gmCreditCash["dtotaldebts"]
    vxdatadict["margin_available"] = gmCreditCash["marginavl"]
    vxdatadict["balance"] = (
        vxdatadict["asset"] - gmCreditCash["ftotaldebts"] - gmCreditCash["dtotaldebts"]
    )
    return vxdatadict


# * #####################################################################
# * gmPosition的转换器
# * #####################################################################
GM_POSITIONS_CONVERTORS = {
    # 账户id
    "account_id": "account_id",
    # 证券类型
    "security_type": lambda x: vxMarketPreset(x["symbol"]).security_type,
    # 持仓方向
    "position_side": lambda x: PositionSide.Long,
    # 昨日持仓数量
    "volume_his": lambda x: x["volume"] - x["volume_today"],
    # 冻结数量
    "frozen": "frozen",
    # 持仓市值
    "marketvalue": "market_value",
    # 持仓成本
    "cost": "amount",
    # 浮动盈利
    "fnl": "fnl",
    # 最近成交价
    "lasttrade": "price",
    # 是否T0
    "allow_t0": lambda x: vxMarketPreset(x["symbol"]).allow_t0,
}

gmPositionConvter = vxDataConvertor(vxPosition, GM_POSITIONS_CONVERTORS)


# * #####################################################################
# * gmCashPosition的转换器
# * #####################################################################

CASH_POSITION_CONVERTORS = {
    "frozen": "order_frozen",
    "volume_his": lambda x: x["order_frozen"] + x["available"],
    "created_dt": "created_at",
    "updated_dt": "updated_at",
    "allow_t0": lambda x: True,
}
gmCashPositionConvter = vxDataConvertor(vxCashPosition, CASH_POSITION_CONVERTORS)

# * #####################################################################
# * gmOrder的转化器
# * #####################################################################


def _make_due_dt(obj):
    created_date = to_timestring(obj["created_at"] or vxtime.now(), "%Y-%m-%d")
    return combine_datetime(created_date, "15:00:00")


GM_ORDER_CONVERTORS = {
    "exchange_order_id": "cl_ord_id",
    "order_id": "cl_ord_id",
    "order_direction": "side",
    "order_offset": "position_effect",
    "reject_code": "ord_rej_reason",
    "rej_reason_detail": lambda x: to_text(x["ord_rej_reason_detail"]),
    "due_dt": _make_due_dt,
    "created_dt": "created_at",
    "updated_dt": "created_at",
}
gmOrderConvter = vxDataConvertor(vxOrder, GM_ORDER_CONVERTORS)

# * #####################################################################
# * gmTrade的转化器
# * #####################################################################

GM_TRADE_CONVERTORS = {
    "trade_id": "exec_id",
    "exchange_order_id": "cl_ord_id",
    "order_id": "cl_ord_id",
    "reject_code": "ord_rej_reason",
    "reject_reason": lambda x: to_text(x["ord_rej_reason_detail"]),
    "created_dt": "created_at",
    "updated_dt": "created_at",
    "status": "exec_type",
    "order_direction": "side",
    "order_offset": "position_effect",
}

gmTradeConvter = vxDataConvertor(vxTrade, GM_TRADE_CONVERTORS)
