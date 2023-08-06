"""MINI QMT Providers"""

from pathlib import Path
from typing import List, Dict, Union
from enum import Enum
from vxquant.accountdb.sqlitedb import vxSQLiteAccountDB
from vxquant.model.contants import OrderStatus, TradeStatus, OrderRejectReason
from vxquant.model.typehint import InstrumentType, DateTimeType
from vxquant.model.exchange import (
    vxCashPosition,
    vxPosition,
    vxTick,
    vxOrder,
    vxTrade,
    vxAccountInfo,
)

from vxquant.model.tools.qmtData import (
    qmtTickConvter,
    qmtOrderConvter,
    qmtPositionConvter,
    qmtTradeConvter,
    qmtCashPositionConvter,
    qmtAccountInfoConvter,
    qmtCreditAccountInfoConvter,
)
from vxquant.model.preset import vxMarketPreset
from vxquant.providers.base import (
    vxInitProviderContext,
    vxHQProvider,
    vxCalendarProvider,
    vxFeaturesProvider,
    vxGetAccountProvider,
    vxGetPositionsProvider,
    vxOrderBatchProvider,
    vxOrderCancelProvider,
    vxGetExecutionReportsProvider,
    vxGetOrdersProvider,
    ProviderContext,
)
from vxsched import vxScheduler, vxContext, vxscheduler
from vxutils import vxtime, logger, to_timestring, to_text

try:
    from xtquant import xtdata
    from xtquant.xttype import StockAccount
    from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
    from xtquant import xtconstant
except ImportError as e:
    raise ImportError("xtquant未安装，请将QMT安装目录")


class QMTAccountType(Enum):
    """QMT账户类型"""

    NORMAL = xtconstant.SECURITY_ACCOUNT
    CREDIT = xtconstant.CREDIT_ACCOUNT
    FUTURE_OPTION = xtconstant.FUTURE_OPTION_ACCOUNT
    STOCK_OPTION = xtconstant.STOCK_OPTION_ACCOUNT
    HUGANGTONG = xtconstant.HUGANGTONG_ACCOUNT
    SHENGANGTONG = xtconstant.SHENGANGTONG_ACCOUNT


def to_qmt_symbol(symbol: InstrumentType):
    """将symbol(SHSE.600000) --> QMT的symbol格式(600000.SH)"""
    return f"{symbol[-6:]}.{symbol[:2]}"


class vxMiniQMTHQProvider(vxHQProvider):
    """Mini QMT行情接口"""

    def _hq(self, *symbols: List[InstrumentType]) -> Dict[InstrumentType, vxTick]:
        if len(symbols) == 1 and isinstance(symbols[0], list):
            symbols = symbols[0]

        qmt_symbols = [to_qmt_symbol(symbol) for symbol in symbols]
        qmt_ticks = xtdata.get_full_tick(qmt_symbols)
        for k, v in qmt_ticks.items():
            v["symbol"] = k
        return dict(map(lambda x: qmtTickConvter(x, "symbol"), qmt_ticks.values()))


class vxMiniQMTGetAccountProvider(vxGetAccountProvider):
    """Mini QMT普通账户接口"""

    def __call__(self, account_id: str = None) -> vxAccountInfo:
        account = self.context.qmt_accounts.get("NORMAL", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联普通账户. {account}")

        acc_info = self.context.trader.query_stock_asset(account)
        if not acc_info:
            raise ConnectionError(f"无法获取账户信息，请检查连接. {acc_info}")

        qmt_positions = self.context.trader.query_stock_positions(account)
        fnl = sum(p.market_value - p.open_price * p.volume for p in qmt_positions)
        return qmtAccountInfoConvter(acc_info, fnl=fnl)


class vxMiniQMTGetCreditAccountProvider(vxGetAccountProvider):
    """Mini QMT信用账户接口"""

    def __call__(self, account_id: str = None) -> vxAccountInfo:
        account = self.context.qmt_accounts.get("CREDIT", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联信用账户. {account}")

        acc_info = self.context.trader.query_credit_detail(account)
        if not acc_info:
            raise ConnectionError(f"无法获取账户信息，请检查连接. {acc_info}")
        acc_info = acc_info[0]
        return qmtCreditAccountInfoConvter(acc_info)


class vxMiniQMTGetPositionsProvider(vxGetPositionsProvider):
    """Mini QMT持仓接口"""

    def __call__(
        self, symbol: InstrumentType = None, account_id: str = None
    ) -> Dict[InstrumentType, Union[vxPosition, vxCashPosition]]:
        account = self.context.qmt_accounts.get("NORMAL", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联普通账户. {account}")
        qmt_positions = self.context.trader.query_stock_positions(account)
        positions = dict(map(lambda x: qmtPositionConvter(x, "symbol"), qmt_positions))
        if symbol:
            return positions.pop(symbol, {})

        acc_info = self.context.trader.query_stock_asset(account)
        if not acc_info:
            raise ConnectionError(f"无法获取账户信息，请检查连接. {acc_info}")
        cash_position = qmtCashPositionConvter(acc_info)
        positions["CNY"] = cash_position
        return positions


class vxMiniQMTGetOrdersProvider(vxGetOrdersProvider):
    def __call__(
        self, account_id: str = None, filter_finished: bool = False
    ) -> Dict[str, vxOrder]:
        account = self.context.qmt_accounts.get("NORMAL", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联普通账户. {account}")
        qmt_orders = self.context.trader.query_stock_orders(account, filter_finished)
        return dict(
            map(lambda order: qmtOrderConvter(order, "exchange_order_id"), qmt_orders)
        )


class vxMiniQMTGetExecutionReportsProvider(vxGetExecutionReportsProvider):
    def __call__(
        self, account_id: str = None, order_id: str = None, trade_id: str = None
    ) -> Dict[str, vxTrade]:
        account = self.context.qmt_accounts.get("NORMAL", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联普通账户. {account}")
        qmt_trades = self.context.trader.query_stock_trades(account)
        return dict(map(lambda x: qmtTradeConvter(x, "trade_id"), qmt_trades))


class vxMiniQMTOrderBatchProvider(vxOrderBatchProvider):
    def __call__(self, *vxorders) -> List[vxOrder]:
        account = self.context.qmt_accounts.get("NORMAL", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联普通账户. {account}")

        if len(vxorders) == 1 and isinstance(vxorders[0], (list, tuple, set)):
            vxorders = vxorders[0]

        for vxorder in vxorders:
            price_type = (
                xtconstant.FIX_PRICE
                if vxorder.order_type.name == "Limit"
                else (
                    xtconstant.MARKET_SH_CONVERT_5_CANCEL
                    if vxorder.symbol[:2] == "SH"
                    else xtconstant.MARKET_SZ_CONVERT_5_CANCEL
                )
            )

            order_type = (
                xtconstant.STOCK_BUY
                if vxorder.order_direction.name == "Buy"
                else xtconstant.STOCK_SELL
            )

            seq_no = self.context.trader.order_stock(
                account=account,
                stock_code=to_qmt_symbol(vxorder.symbol),
                order_type=order_type,
                order_volume=vxorder.volume,
                price_type=price_type,
                price=vxorder.price,
                strategy_name=vxorder.order_id[16:],
                order_remark=vxorder.order_id[:16],
            )
            exchange_order_id = f"qmt_{seq_no}"

            if seq_no <= 0:
                vxorder.status = "Rejected"
                vxorder.reject_code = OrderRejectReason.UnknownOrder
                vxorder.reject_reason = f"错误代码: {exchange_order_id}"
            else:
                vxorder.exchange_order_id = str(exchange_order_id)
                vxorder.status = "New"

            # self.context.broker_orders[vxorder.exchange_order_id] = vxorder

        return vxorders


class vxMiniQMTOrderCancelProvider(vxOrderCancelProvider):
    def __call__(self, *vxorders) -> None:
        if len(vxorders) == 1 and isinstance(vxorders[0], list):
            vxorders = vxorders[0]

        account = self.context.qmt_accounts.get("NORMAL", None)
        if not account:
            raise ValueError(f"无法获取账户信息，请QMT是否已关联普通账户. {account}")

        for vxorder in vxorders:
            if not vxorder.exchange_order_id:
                continue

            seq = self.context.trader.cancel_order_stock_async(
                account, int(vxorder.exchange_order_id.replace("qmt_", ""))
            )
            if seq <= 0:
                logger.error(
                    f"委托订单:{vxorder.order_id} 撤单失败{vxorder.symbol} {vxorder.order_direction} {vxorder.volume}"
                )
        return


class vxMiniQMTCalendarProvider(vxCalendarProvider):
    def get_trade_dates(
        self,
        market: str = "cn",
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
    ):
        start_date = to_timestring(start_date, "%Y%m%d") if start_date else "19900101"
        end_date = to_timestring(end_date, "%Y%m%d") if end_date else "20991231"
        return xtdata.get_trading_calendar("SH", start_date, end_date)


class QMTAccountStatus(Enum):
    INVALID = -1
    OK = 0
    WAITING_LOGIN = 1
    STATUSING = 2
    FAIL = 3
    INITING = 4
    CORRECTING = 5
    CLOSED = 6
    ASSIS_FAIL = 7
    DISABLEBYSYS = 8
    DISABLEBYUSER = 9


class vxQMTTraderCallback(XtQuantTraderCallback):
    def __init__(
        self,
        context: vxContext,
    ) -> None:
        self._context = context
        if "sched" not in self._context:
            self._context.sched = vxscheduler

        # if "accountdb" not in self._context:
        #    self._context.accountdb = vxSQLiteAccountDB()

    def on_connected(self):
        """
        连接成功推送
        """
        logger.info("QMT连接成功")
        self._context.sched.submit_events("on_connected")

    def on_disconnected(self):
        """
        连接状态回调
        :return:
        """
        logger.warning("QMT连接断开")
        self._context.sched.submit_events("on_disconnected")

    def on_account_status(self, status):
        """
        账号状态信息推送
        :param response: XtAccountStatus 对象
        :return:
        """
        logger.info(
            "账户状态变更为:"
            f" {status.account_id} {status.account_type} {QMTAccountStatus(status.status)}"
        )
        self._context.sched.submit_event(
            "on_account_status",
            (status.account_id, status.account_type, QMTAccountStatus(status.status)),
        )

    def on_stock_asset(self, asset):
        """
        资金信息推送
        :param asset: XtAsset对象
        :return:
        """
        logger.info(
            f"on asset callback {asset.account_id}, {asset.cash}, {asset.total_asset}"
        )

    def on_stock_order(self, order):
        """
        委托信息推送
        :param order: XtOrder对象
        :return:
        """
        broker_order = qmtOrderConvter(order)
        logger.info(
            f"收到来自broker委托订单 {broker_order.exchange_order_id} 更新为: {broker_order}"
        )
        self._context.sched.submit_event("on_broker_order_status", broker_order)

    def on_stock_trade(self, trade):
        """
        成交信息推送
        :param trade: XtTrade对象
        :return:
        """
        logger.info(f"收到成交信息: {trade.account_id}, {trade.stock_code}, {trade.order_id}")

        broker_trade = qmtTradeConvter(trade)

        if broker_trade.status != TradeStatus.Trade:
            logger.warning(f"收到非成交的回报信息: {broker_trade}")
            return

        # 调整当日手续费
        if broker_trade.commission == 0:
            _preset = vxMarketPreset(broker_trade.symbol)
            broker_trade.commission = max(
                (
                    broker_trade.price
                    * broker_trade.volume
                    * (
                        _preset.commission_coeff_peramount
                        if broker_trade.order_direction.name == "Buy"
                        else (
                            _preset.commission_coeff_peramount
                            + _preset.tax_coeff_peramount
                        )
                    )
                ),
                0.5,
            )

        self._context.sched.submit_event("on_broker_execution_report", broker_trade)
        logger.info(
            f"收到来自broker成交回报信息 {broker_trade.exchange_order_id}: {broker_trade}"
        )

    def on_stock_position(self, xtposition):
        """
        持仓信息推送
        :param position: XtPosition对象
        :return:
        """
        logger.info(f"持仓信息推送: {xtposition.stock_code}, {xtposition.volume}")
        position = qmtPositionConvter(xtposition)
        self._context.sched.submit_event("on_position_update", data=position)

    def on_order_error(self, order_error):
        # sourcery skip: use-named-expression
        """
        下单失败信息推送
        :param order_error:XtOrderError 对象
        :return:
        """
        # order_error.order_id = f"qmt_{order_error.order_id}"
        logger.warning(
            "收到委托订单错误反馈:"
            f" {order_error.order_id},"
            f" {order_error.error_id}, {order_error.error_msg}"
        )
        try:
            exchange_order_id = f"qmt_{order_error.order_id}"
            orders = self._context.teller.get_orders(
                exchange_order_id=exchange_order_id
            )
            if exchange_order_id not in orders:
                logger.warning(f"收到来自broker委托订单 qmt_{order_error.order_id} 未找到")
                return
            vxorder = orders[exchange_order_id]
            vxorder.status = OrderStatus.Rejected
            vxorder.reject_code = OrderRejectReason.UnknownOrder
            vxorder.reject_reason = f"{order_error.error_msg}"
            self._context.sched.submit_event("on_broker_order_status", vxorder)
            logger.debug(f"收到来自broker委托订单 {vxorder.exchange_order_id} 更新为: {vxorder}")
        except Exception as e:
            logger.error(e, exc_info=True)

    def on_order_stock_async_response(self, response):
        """
        :param response: XtOrderResponse 对象
        :return:
        """
        # with self.lock:
        #    vxorder = self.seq_mapping.get(response.seq, None)
        #    vxorder.exchange_order_id = response.order_id
        #    self.broker_orders[vxorder.exchange_order_id] = vxorder

    def on_smt_appointment_async_response(self, response):
        """
        :param response: XtAppointmentResponse 对象
        :return:
        """


class vxInitMinitQMTProviderContext(vxInitProviderContext):
    def __init__(self, miniqmt_path: Union[str, Path]):
        self._miniqmt_path = str(miniqmt_path)
        super().__init__()

    def set_context(self, context: vxContext, **kwargs):
        if (
            self._context
            and "trader" in self._context
            and "qmt_accounts" in self._context
        ):
            return

        context.trader = XtQuantTrader(self._miniqmt_path, int(vxtime.now()))
        context.trader.start()
        connect_result = context.trader.connect()
        if connect_result != 0:
            raise ConnectionError(f"连接失败: {connect_result}")
        logger.info(f"trader 连接成功. {context.trader}")

        callback = vxQMTTraderCallback(context)
        context.trader.register_callback(callback)
        accounts = context.trader.query_account_infos()
        context.qmt_accounts = {}

        for account in accounts:
            subscribe_result = context.trader.subscribe(account)
            if subscribe_result != 0:
                raise ConnectionError(f"订阅失败: {subscribe_result}")
            logger.info(f"订阅账号回调信息: {account}")
            context.qmt_accounts[QMTAccountType(account.account_type).name] = account
        return
