"""接口基础类"""

from typing import Optional, Union, Dict, List
from vxquant.model.preset import vxMarketPreset
from vxquant.model.typehint import DateTimeType
from vxquant.model.exchange import (
    vxOrder,
    vxAccountInfo,
    vxPosition,
    vxCashPosition,
    vxTrade,
    vxTransferInfo,
    vxPortfolioInfo,
)
from vxquant.model.contants import (
    OrderDirection,
    OrderStatus,
    OrderType,
    SecType,
    TradeStatus,
)
from vxquant.accountdb.base import vxAccountDB
from vxquant.exceptions import NoEnoughCash, NoEnoughPosition
from vxsched.triggers import vxIntervalTrigger, vxOnceTrigger, vxDailyTrigger
from vxsched import vxContext, vxEvent, vxScheduler
from vxutils import (
    vxWrapper,
    vxAPIWrappers,
    logger,
    to_timestamp,
    to_timestring,
    vxtime,
    to_datetime,
    combine_datetime,
)
from vxutils.dataorm import vxDataBase, vxDBSession

vxPositionType = Union[vxPosition, vxCashPosition]


def sub_volume(
    position: Union[vxCashPosition, vxPosition], volume: Union[float, int]
) -> Union[vxCashPosition, vxPosition]:
    """扣减持仓量

    Arguments:
        position {Union[vxCashPosition, vxPosition]} -- 需要扣减的持仓
        volume {Union[float, int]} -- 扣减量

    Raises:
        NoEnoughPosition: 扣减持仓不足

    Returns:
        Union[vxCashPosition, vxPosition] -- 扣减后的持仓
    """
    if volume > position.available:
        raise NoEnoughPosition(
            f"{position.symbol}可用余额({position.available:,.2f}) 小于需扣减{volume:,.2f}"
        )

    delta = position.volume_his - volume
    position.volume_his = max(delta, 0)
    position.volume_today += min(delta, 0)
    return position


class vxMdAPI(vxAPIWrappers):
    """行情接口类"""

    __defaults__ = {
        "current": {"class": "vxquant.providers.tdx.MultiTdxHQProvider", "params": {}},
        "calendar": {
            "class": "vxquant.providers.spiders.calendar_sse.CNCalenderProvider",
            "params": {},
        },
        "instruments": {
            "class": "vxquant.providers.local.vxLocalInstrumentsProvider",
            "params": {},
        },
        "features": {
            "class": "vxquant.providers.local.vxLocalFeaturesProvider",
            "params": {},
        },
    }

    def set_context(self, context: vxContext):
        """设置上下文

        Arguments:
            context {vxContext} -- 上下文
        """

        for provider in self.__dict__.values():
            if hasattr(provider, "set_context"):
                provider.set_context(context)


class vxTdAPI(vxAPIWrappers):
    """交易接口类"""

    __defaults__ = {
        "current": {"class": "vxquant.providers.tdx.MultiTdxHQProvider", "params": {}},
        "get_account": {},
        "get_positions": {},
        "get_orders": {},
        "get_execution_reports": {},
        "order_batch": {},
        "order_cancel": {},
    }

    def set_context(self, context: vxContext):
        """设置上下文

        Arguments:
            context {vxContext} -- 上下文
        """
        for provider in self.__dict__.values():
            if hasattr(provider, "set_context"):
                provider.set_context(context)

    def order_volume(
        self,
        symbol: str,
        volume: int,
        price: Optional[float] = 0,
        account_id: str = None,
    ) -> vxOrder:
        """下单

        Arguments:
            account_id {str} -- 账户ID
            symbol {str} -- 证券代码
            volume {int} -- 委托数量
            price {Optional[float]} -- 委托价格,若price为None,则使用市价委托 (default: {None})

        Returns:
            vxorder {vxOrder} -- 下单委托订单号
        """
        if volume == 0:
            raise ValueError("volume can't be 0.")

        order_type = OrderType.Limit
        if not price:
            ticks = self.current(symbol)
            price = ticks[symbol].ask1_p if volume > 0 else ticks[symbol].bid1_p
            order_type = (
                OrderType.Limit
                if vxMarketPreset(symbol).security_type == SecType.BOND_CONVERTIBLE
                else OrderType.Market
            )

        vxorder = vxOrder(
            account_id=account_id,
            symbol=symbol,
            volume=abs(volume),
            price=price,
            order_offset="Open" if volume > 0 else "Close",
            order_direction="Buy" if volume > 0 else "Sell",
            order_type=order_type,
            status="PendingNew",
        )
        ret_orders = self.order_batch(vxorder)
        return ret_orders[0]


class vxTeller:
    """交易员类"""

    def __init__(
        self,
        accountdb: Union[vxAccountDB, Dict],
        mdapi: Union[vxMdAPI, Dict] = None,
        channels: Dict = None,
    ):
        self._db: vxAccountDB = vxWrapper.init_by_config(accountdb)

        if isinstance(mdapi, dict):
            mdapi = vxWrapper.init_by_config(mdapi)

        self._mdapi = mdapi or vxMdAPI()

        self._channels = {}
        if channels:
            for channel_name, tdapi in channels.items():
                if isinstance(tdapi, dict):
                    tdapi = vxWrapper.init_by_config(tdapi)

                self.add_channel(channel_name, tdapi)

        self._sched: vxScheduler = None
        self._has_before_day_event = False

    def create_account(
        self,
        portfolio_id: str,
        account_id: str,
        init_balance=1_000_000.0,
        created_dt: DateTimeType = None,
        if_exists: str = "ignore",
        channel: str = "sim",
    ) -> vxAccountInfo:
        """创建账户

        Arguments:
            portfolio_id {str} -- 组合ID
            account_id {str} -- 账户ID

        Keyword Arguments:
            init_balance {float} -- 初始资金 (default: {1,000,000.0})
            created_dt {DateTimeType} -- 创建时间 (default: {None})
            if_exists {str} -- 若已存在,则delete || ignore  (default: {"ignore"})
            channel {str} -- 委托下单通道 (default: {"sim"})

        Returns:
            vxAccountInfo -- 已创建的账户信息
        """
        with self._db.start_session() as session:
            accountinfo = session.create_account(
                portfolio_id, account_id, init_balance, created_dt, if_exists, channel
            )
            if channel not in self._channels:
                logger.warning(
                    f"channel {channel} not found, please add it before place an order."
                )
            return accountinfo

    def add_channel(self, channel: str, tdapi: vxTdAPI) -> None:
        """增加交易通道

        Arguments:
            channel {str} -- 交易通道名称
            tdapi {vxTdAPI} -- 交易接口
        """
        broker_account = tdapi.get_account()
        broker_positions = tdapi.get_positions()
        broker_orders = tdapi.get_orders()
        broker_trades = tdapi.get_execution_reports()
        with self._db.start_session() as session:
            try:
                session.sync_with_broker(
                    broker_account, broker_positions, broker_orders, broker_trades
                )
            except Exception as e:
                logger.warning(f"同步账户信息失败: {e}")

        self._channels[channel] = tdapi
        logger.info(f"channel {channel} added.")
        return

    def deposit(
        self, account_id: str, amount: float, transfer_dt: DateTimeType = None
    ) -> vxTransferInfo:
        """转入资金

        Arguments:
            account_id {str} -- 账户ID
            amount {float} -- 转入金额
            transfer_dt {DateTimeType} -- 转入时间 (default: {None})

        Returns:
            vxTransferInfo -- 转账信息
        """
        if amount < 0:
            raise ValueError(f"转入金额({amount})应大于0 .")

        with self._db.start_session() as session:
            transfer_dt = to_timestamp(transfer_dt or vxtime.now())

            # 转账交易记录
            transferinfo = vxTransferInfo(
                account_id=account_id,
                amount=amount,
                transfer_direction="In",
                created_dt=transfer_dt,
            )

            cash = session.findone("positions", account_id=account_id, symbol="CNY")
            cash = vxCashPosition(**cash.message)
            cash.volume_today += amount

            accountinfo = session.findone("accounts", account_id=account_id)
            accountinfo.deposit += amount
            accountinfo.fund_shares += amount / accountinfo.fund_nav_yd
            accountinfo.balance = cash.marketvalue
            accountinfo.frozen = cash.frozen

            session.save("transferinfos", transferinfo)
            session.save("positions", cash)
            session.save("accounts", accountinfo)

        return transferinfo

    def withdraw(
        self, account_id: str, amount: float, transfer_dt: DateTimeType = None
    ) -> vxTransferInfo:
        """转出资金

        Arguments:
            account_id {str} -- 账户ID
            amount {float} -- 转出金额
            transfer_dt {DateTimeType} -- 转出时间 (default: {None})

        Returns:
            vxTransferInfo -- 转账信息
        """
        if amount < 0:
            raise ValueError(f"转出金额({amount})应大于0 .")

        with self._db.start_session() as session:
            cash = session.findone(
                "positions",
                account_id=account_id,
                symbol="CNY",
            )
            if cash.available < amount:
                raise NoEnoughCash("可用资金不足")

            cash = vxCashPosition(**cash.message)
            cash = sub_volume(cash, amount)

            # 转账交易记录
            transfer_dt = to_timestamp(transfer_dt or vxtime.now())
            transferinfo = vxTransferInfo(
                account_id=account_id,
                amount=amount,
                transfer_direction="Out",
                created_dt=transfer_dt,
            )

            accountinfo = session.findone("accounts", account_id=account_id)
            accountinfo.withdraw += amount
            accountinfo.fund_shares -= amount / accountinfo.fund_nav_yd
            accountinfo.balance = cash.marketvalue
            accountinfo.frozen = cash.frozen

            session.save("transferinfos", transferinfo)
            session.save("positions", cash)
            session.save("accounts", accountinfo)

        return transferinfo

    def get_accounts(
        self, account_id: str = None, portfolio_id: str = None
    ) -> Union[vxAccountInfo, Dict[str, vxAccountInfo]]:
        """查询子账户信息

        Arguments:
            account_id {str} -- 账户ID,如果为None则返回所有账户信息

        Returns:
            Union[vxAccountInfo, Dict[str, vxAccountInfo]] -- 账户信息
        """
        with self._db.start_session() as session:
            query = {}
            if account_id:
                query["account_id"] = account_id
            if portfolio_id:
                query["portfolio_id"] = portfolio_id

            return (
                session.findone("accounts", **query)
                if account_id
                else list(session.find("accounts", **query))
            )

    def get_positions(
        self, account_id: str, symbol: str = None
    ) -> Dict[str, vxPositionType]:
        """获取账户持仓

        Arguments:
            account_id {str} -- 账户ID
            symbol {str} -- 持仓证券symbol，若为None，则返回全部持仓 (default: {None})

        Returns:
            Dict[str, vxPositionType] -- 持仓信息
        """
        with self._db.start_session() as session:
            if symbol:
                pos = session.findone(
                    "positions",
                    account_id=account_id,
                    symbol=symbol,
                    settle_date=self._db.settle_date,
                )
                return vxCashPosition(pos.message) if symbol == "CNY" else pos

            _positions = {
                p.symbol: p for p in session.find("positions", account_id=account_id)
            }
            _positions["CNY"] = vxCashPosition(_positions["CNY"].message)

            return _positions

    def get_orders(
        self,
        account_id: str,
        order_id: str = None,
        exchange_order_id: str = None,
        filter_finished=False,
    ) -> Dict[str, vxOrder]:
        """查询订单信息

        Arguments:
            account_id {str} -- 账户ID
            order_id {str} -- 委托订单号 (default: {None})
            exchange_order_id {str} -- 交易所委托订单号 (default: {None})
            filter_finished {bool} -- 是否过滤已完成的订单 (default: {False})

        Returns:
            Dict[str, vxOrder] -- 委托订单
        """
        query = {"account_id": account_id}
        if order_id:
            query["order_id"] = order_id

        if exchange_order_id:
            query["exchange_order_id"] = exchange_order_id

        condisiotns = [
            f"""created_dt > {vxtime.today()}""",
            f"""created_dt < {self._db.settle_date} """,
        ]
        if filter_finished:
            condisiotns.append("""status in ("New", "PendingNew", "PartiallyFilled")""")

        with self._db.start_session(True) as session:
            cur = session.find("orders", *condisiotns, **query)
            return {o.exchange_order_id: o for o in cur}

    def get_execution_reports(
        self,
        account_id: str,
        trade_id: str = None,
        order_id: str = None,
        exchange_order_id: str = None,
    ) -> Dict[str, vxTrade]:
        """查询成交信息

        Arguments:
            account_id {str} -- 账户ID

        Returns:
            Dict[str, vxTrade] -- 成交回报
        """
        query = {"account_id": account_id}
        conditions = [
            f"""created_dt > {vxtime.today()}""",
            f"""created_dt < {self._db.settle_date} """,
        ]
        if trade_id:
            query["trade_id"] = trade_id
        if order_id:
            query["order_id"] = order_id
        if exchange_order_id:
            query["exchange_order_id"] = exchange_order_id
        with self._db.start_session() as session:
            cur = session.find("trades", *conditions, **query)
            return {t.trade_id: t for t in cur}

    def get_transferinfos(
        self,
        account_id: str,
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
    ) -> Dict[str, vxTransferInfo]:
        """查询资金流水

        Arguments:
            account_id {str} -- 账户ID

        Returns:
            Dict[str, vxTransferInfo] -- 资金流水
        """
        start_date = (
            combine_datetime(start_date, "00:00:00") if start_date else vxtime.today()
        )
        end_date = (
            combine_datetime(end_date, "23:59:59") if end_date else self._db.settle_date
        )

        with self._db.start_session() as session:
            cur = session.find(
                "transferinfos",
                f"created_dt > {start_date}",
                f"created_dt < {end_date}",
                account_id=account_id,
            )
            return {t.transfer_id: t for t in cur}

    def order_volume(
        self,
        account_id: str,
        symbol: str,
        volume: float,
        price: float = None,
        check_channel: bool = True,
    ) -> vxOrder:
        """委托下单

        Arguments:
            account_id {str} -- 账户ID
            symbol {str} -- 证券代码
            volume {float} -- 委托数量，正数为买入，负数为卖出
            price {float} -- 委托价格,若price为None，则通过市价委托下单 (default: {None})
            check_channel {bool} -- 是否检查通道 (default: {True})

        Returns:
            vxOrder -- 下单的信息
        """
        if volume == 0:
            raise ValueError("volume can't be 0.")

        accountinfo = self._db.findone("accounts", account_id=account_id)

        if accountinfo is None:
            raise ValueError(f"account {account_id} not found.")

        if accountinfo.channel not in self._channels and check_channel:
            raise ValueError(f"channel {accountinfo.channel} not found.")

        tradeapi = self._channels.get(accountinfo.channel, None)

        order_type = OrderType.Limit
        if not price:
            ticks = tradeapi.current(symbol)
            price = ticks[symbol].ask1_p if volume > 0 else ticks[symbol].bid1_p
            order_type = (
                OrderType.Limit
                if vxMarketPreset(symbol).security_type == SecType.BOND_CONVERTIBLE
                else OrderType.Market
            )

        vxorder = vxOrder(
            account_id=account_id,
            symbol=symbol,
            volume=abs(volume),
            price=price,
            order_offset="Open" if volume > 0 else "Close",
            order_direction="Buy" if volume > 0 else "Sell",
            order_type=order_type,
            status="PendingNew",
        )
        with self._db.start_session() as session:
            frozen_symbol = symbol if volume < 0 else "CNY"
            frozen_volume = abs(volume) if volume < 0 else price * volume * 1.003
            position = session.findone(
                "positions",
                f"available >= {frozen_volume}",
                account_id=vxorder.account_id,
                symbol=frozen_symbol,
            )
            if not position:
                raise (
                    NoEnoughCash(f"可用资金不足，需要冻结资金{frozen_volume:,.2f}元")
                    if frozen_symbol == "CNY"
                    else NoEnoughPosition(f"{symbol}持仓可用持仓不足,冻结仓位{frozen_volume:,.2f}")
                )

            if check_channel:
                ret_orders = tradeapi.order_batch(vxorder)
            else:
                vxorder.exchange_order_id = vxorder.order_id
                ret_orders = [vxorder]

            session.save("orders", ret_orders[0])
            if ret_orders[0].order_direction == OrderDirection.Buy:
                session.update_cash_position_frozens(account_ids=[account_id])
            else:
                session.update_symbol_position_frozens(account_ids=[account_id])
            session.update_accountinfos([account_id])
            logger.info(
                f"[新增] 委托订单: {ret_orders[0].exchange_order_id} : {ret_orders[0]}"
            )

        return ret_orders[0]

    def order_cancel(self, order: vxOrder) -> None:
        """撤单

        Arguments:
            *orders {List[str]} -- 订单号
        """
        order = self._db.findone("orders", exchange_order_id=order.exchange_order_id)
        if order is None:
            raise ValueError(f"order {order.exchange_order_id} not found.")

        accountinfo = self._db.findone("accounts", account_id=order.account_id)

        if accountinfo is None:
            raise ValueError(f"account {order.account_id} not found.")

        if accountinfo.channel not in self._channels:
            raise ValueError(f"channel {accountinfo.channel} not found.")

        tradeapi = self._channels[accountinfo.channel]
        tradeapi.order_cancel(order)

    def on_tick(self, context: vxContext, event: vxEvent) -> None:
        "更新行情事件"
        symbols = self._db.distinct("positions", "symbol", "symbol != 'CNY'")
        vxticks = self._mdapi.current(*symbols)
        with self._db.start_session() as session:
            session.update_position_lasttrades(list(vxticks.values()))

    def on_broker_order_status(self, context: vxContext, event: vxEvent) -> None:
        "更新订单状态事件"
        broker_order = event.data
        if not isinstance(broker_order, vxOrder):
            logger.error(f"broker_order {broker_order} is not a vxOrder instance.")
            return

        with self._db.start_session() as session:
            vxorder = session.update_order(broker_order)

        if self._sched and vxorder:
            self._sched.submit_event("on_order_status", vxorder)

    def on_broker_execution_report(self, context: vxContext, event: vxEvent) -> None:
        "更新成交回报事件"
        broker_trade = event.data
        if not isinstance(broker_trade, vxTrade):
            logger.error(f"broker_trade {broker_trade} is not a vxTrade instance.")
            return

        with self._db.start_session() as session:
            vxtrade, vxorder = session.update_trade(broker_trade)

        if self._sched and vxtrade:
            self._sched.submit_event("on_execution_report", vxtrade)

        if self._sched and vxorder:
            self._sched.submit_event("on_order_status", vxorder)

    def after_close(self, context: vxContext, event: vxEvent) -> None:
        "收盘后事件"
        with self._db.start_session() as session:
            for channel_name, tdapi in self._channels.items():
                broker_account = tdapi.get_account()
                broker_positions = tdapi.get_positions()
                broker_orders = tdapi.get_orders()
                broker_trades = tdapi.get_execution_reports()
                try:
                    session.sync_with_broker(
                        broker_account, broker_positions, broker_orders, broker_trades
                    )
                    logger.info(f"channel({channel_name})同步账户信息成功")
                except Exception as e:
                    logger.warning(f"channel({channel_name})同步账户信息失败: {e}")

            session.update_after_close()
        self._sched.stop()

    def day_begin(self, context: vxContext, event: vxEvent) -> None:
        """开盘前准备事件"""

        if vxtime.is_holiday():
            logger.info("今天是节假日，不进行交易")
            return

        with self._db.start_session() as session:
            session.update_settle_date(vxtime.today("23:59:59"))

        if vxtime.now() > vxtime.today("15:00:00"):
            logger.info("已经收盘，不进行交易")
            return

        # self._sched.submit_event("before_day", trigger=vx("09:10:00"))
        self._sched.submit_event(
            "before_trade", trigger=vxOnceTrigger(vxtime.today("09:15:00"))
        )
        self._sched.submit_event(
            "on_trade", trigger=vxOnceTrigger(vxtime.today("09:30:00"))
        )
        self._sched.submit_event(
            "noon_break_start", trigger=vxOnceTrigger(vxtime.today("11:30:00"))
        )
        self._sched.submit_event(
            "noon_break_end", trigger=vxOnceTrigger(vxtime.today("13:00:00"))
        )
        self._sched.submit_event(
            "before_close", trigger=vxOnceTrigger(vxtime.today("14:45:00"))
        )
        self._sched.submit_event(
            "on_close", trigger=vxOnceTrigger(vxtime.today("14:55:00"))
        )
        self._sched.submit_event(
            "after_close", trigger=vxOnceTrigger(vxtime.today("15:30:00"))
        )
        self._sched.submit_event(
            "on_tick",
            trigger=vxIntervalTrigger(
                1,
                start_dt=vxtime.today("09:30:00"),
                end_dt=vxtime.today("11:30:00"),
            ),
        )
        self._sched.submit_event(
            "on_tick",
            trigger=vxIntervalTrigger(
                1,
                start_dt=vxtime.today("13:00:00"),
                end_dt=vxtime.today("15:00:00"),
            ),
        )

        if vxtime.today("09:15:00") < vxtime.now() < vxtime.today("15:00:00"):
            self._sched.submit_event("before_trade")

    def register_scheduler(self, sched: vxScheduler):
        """注册事件处理器

        Arguments:
            sched {vxScheduler} -- _description_
        """
        sched.register("on_tick", handler=self.on_tick)
        sched.register("on_broker_order_status", handler=self.on_broker_order_status)
        sched.register(
            "on_broker_execution_report", handler=self.on_broker_execution_report
        )
        sched.register("after_close", handler=self.after_close)
        sched.register("before_day", handler=self.day_begin)

        if not self._has_before_day_event:
            sched.submit_event("before_day", trigger=vxDailyTrigger("09:10:00"))
            self._has_before_day_event = True

            if vxtime.today("09:10:00") < vxtime.now() < vxtime.today("15:00:00"):
                sched.submit_event("before_day")

        self._sched = sched


class vxTellerAPI:
    """交易员类"""

    def __init__(
        self,
        db_uri: str = None,
        mdapi: Union[vxMdAPI, Dict] = None,
        channels: Dict = None,
        **kwargs,
    ):
        self._db = self.init_accountdb(db_uri, **kwargs)
        self._settle_date = self._db.get_dbsession().max(
            "accounts", "settle_date"
        ) or vxtime.today("23:59:59")
        logger.info(f"账户数据库初始化完成: {to_timestring(self._settle_date,'%Y-%m-%d')}")

        self._mdapi = vxWrapper.init_by_config(mdapi) if mdapi else vxMdAPI()
        self._sched: vxScheduler = None
        self._channels = {}
        # if channels:
        #    for channel_name, tdapi in channels.items():
        #        if isinstance(tdapi, dict):
        #            tdapi = vxWrapper.init_by_config(tdapi)

        #        self.add_channel(channel_name, tdapi)

    def init_accountdb(self, db_uri: str = None, **kwargs) -> vxDataBase:
        db = vxDataBase(db_uri, **kwargs)

        # 账户信息
        db.create_table("accounts", ["account_id"], vxAccountInfo)
        db.create_table(
            "history_accounts", ["account_id", "settle_date"], vxAccountInfo
        )

        db.create_table("broker_accounts", ["account_id", "settle_date"], vxAccountInfo)
        # 账号持仓
        db.create_table(
            "positions",
            ["account_id", "symbol", "position_side"],
            vxPosition,
        )
        db.create_table(
            "history_positions",
            ["account_id", "symbol", "settle_date", "position_side"],
            vxPosition,
        )
        db.create_table(
            "broker_positions",
            ["account_id", "symbol", "settle_date", "position_side"],
            vxPosition,
        )
        # 账户交易委托
        db.create_table("orders", ["order_id"], vxOrder)
        db.create_table("broker_orders", ["exchange_order_id"], vxOrder)
        # 账户成交回报
        db.create_table("trades", ["trade_id"], vxTrade)
        db.create_table("broker_trades", ["trade_id"], vxTrade)
        # 账户转账记录
        db.create_table("transferinfos", ["transfer_id"], vxTransferInfo)
        # 账户组合信息
        db.create_table("portfolios", ["portfolio_id", "settle_date"], vxPortfolioInfo)
        return db

    def create_account(
        self,
        portfolio_id: str,
        account_id: str,
        init_balance=1_000_000.0,
        created_dt: DateTimeType = None,
        if_exists: str = "ignore",
        channel: str = "sim",
    ) -> vxAccountInfo:
        """创建账户

        Arguments:
            portfolio_id {str} -- 组合ID
            account_id {str} -- 账户ID

        Keyword Arguments:
            init_balance {float} -- 初始资金 (default: {1,000,000.0})
            created_dt {DateTimeType} -- 创建时间 (default: {None})
            if_exists {str} -- 若已存在,则delete || ignore  (default: {"ignore"})
            channel {str} -- 委托下单通道 (default: {"sim"})

        Returns:
            vxAccountInfo -- 已创建的账户信息
        """
        if_exists = if_exists.lower()
        created_dt = to_timestamp(created_dt or vxtime.today())
        settle_date = self._settle_date
        with self._db.start_session() as session:
            accountinfo = session.findone("accounts", account_id=account_id)

            if accountinfo:
                if if_exists == "delete":
                    session.delete("accounts", account_id=account_id)
                    session.delete("history_accounts", account_id=account_id)
                    session.delete("positions", account_id=account_id)
                    session.delete("history_positions", account_id=account_id)
                    session.delete("orders", account_id=account_id)
                    session.delete("trades", account_id=account_id)
                    session.delete("transferinfos", account_id=account_id)
                else:
                    return accountinfo

            cash = vxCashPosition(
                account_id=account_id,
                portfolio_id=portfolio_id,
                volume_his=init_balance,
                created_dt=created_dt,
                settle_date=settle_date,
            )

            accountinfo = vxAccountInfo(
                account_id=account_id,
                portfolio_id=portfolio_id,
                deposit=0.0,
                balance=init_balance,
                fund_shares=init_balance,
                asset_yd=init_balance,
                nav_yd=init_balance,
                fund_nav_yd=1.0,
                settle_date=settle_date,
                created_dt=created_dt,
                channel=channel,
            )

            transferinfo = vxTransferInfo(
                account_id=account_id,
                amount=init_balance,
                transfer_direction="In",
                created_dt=created_dt,
            )

            session.save("accounts", accountinfo)
            session.save("transferinfos", transferinfo)
            session.save("positions", cash)
            if channel not in self._channels:
                logger.warning(
                    f"channel {channel} not found, please add it before place an order."
                )
            return accountinfo

    def add_channel(self, channel: str, tdapi: vxTdAPI) -> None:
        """增加交易通道

        Arguments:
            channel {str} -- 交易通道名称
            tdapi {vxTdAPI} -- 交易接口
        """
        broker_account = tdapi.get_account()
        broker_positions = tdapi.get_positions()
        broker_orders = tdapi.get_orders()
        broker_trades = tdapi.get_execution_reports()
        self._sched.submit_event(
            "on_sync_brokerinfos",
            (broker_account, broker_positions, broker_orders, broker_trades),
        )
        self._channels[channel] = tdapi
        logger.info(f"channel {channel} added {tdapi}.")

    def deposit(
        self, account_id: str, amount: float, transfer_dt: DateTimeType = None
    ) -> vxTransferInfo:
        """转入资金

        Arguments:
            account_id {str} -- 账户ID
            amount {float} -- 转入金额
            transfer_dt {DateTimeType} -- 转入时间 (default: {None})

        Returns:
            vxTransferInfo -- 转账信息
        """
        if amount < 0:
            raise ValueError(f"转入金额({amount})应大于0 .")

        with self._db.start_session() as session:
            transfer_dt = to_timestamp(transfer_dt or vxtime.now())

            # 转账交易记录
            transferinfo = vxTransferInfo(
                account_id=account_id,
                amount=amount,
                transfer_direction="In",
                created_dt=transfer_dt,
            )

            cash = session.findone("positions", account_id=account_id, symbol="CNY")
            cash = vxCashPosition(**cash.message)
            cash.volume_today += amount

            accountinfo = session.findone("accounts", account_id=account_id)
            accountinfo.deposit += amount
            accountinfo.fund_shares += amount / accountinfo.fund_nav_yd
            accountinfo.balance = cash.marketvalue
            accountinfo.frozen = cash.frozen

            session.save("transferinfos", transferinfo)
            session.save("positions", cash)
            session.save("accounts", accountinfo)

        return transferinfo

    def withdraw(
        self, account_id: str, amount: float, transfer_dt: DateTimeType = None
    ) -> vxTransferInfo:
        """转出资金

        Arguments:
            account_id {str} -- 账户ID
            amount {float} -- 转出金额
            transfer_dt {DateTimeType} -- 转出时间 (default: {None})

        Returns:
            vxTransferInfo -- 转账信息
        """
        if amount < 0:
            raise ValueError(f"转出金额({amount})应大于0 .")

        with self._db.start_session() as session:
            cash = session.findone(
                "positions",
                account_id=account_id,
                symbol="CNY",
            )
            if cash.available < amount:
                raise NoEnoughCash("可用资金不足")

            cash = vxCashPosition(**cash.message)
            cash = sub_volume(cash, amount)

            # 转账交易记录
            transfer_dt = to_timestamp(transfer_dt or vxtime.now())
            transferinfo = vxTransferInfo(
                account_id=account_id,
                amount=amount,
                transfer_direction="Out",
                created_dt=transfer_dt,
            )

            accountinfo = session.findone("accounts", account_id=account_id)
            accountinfo.withdraw += amount
            accountinfo.fund_shares -= amount / accountinfo.fund_nav_yd
            accountinfo.balance = cash.marketvalue
            accountinfo.frozen = cash.frozen

            session.save("transferinfos", transferinfo)
            session.save("positions", cash)
            session.save("accounts", accountinfo)

        return transferinfo

    def get_accounts(
        self, account_id: str = None, portfolio_id: str = None
    ) -> Union[vxAccountInfo, Dict[str, vxAccountInfo]]:
        """查询子账户信息

        Arguments:
            account_id {str} -- 账户ID,如果为None则返回所有账户信息

        Returns:
            Union[vxAccountInfo, Dict[str, vxAccountInfo]] -- 账户信息
        """
        with self._db.start_session() as session:
            query = {}
            if account_id:
                query["account_id"] = account_id
            if portfolio_id:
                query["portfolio_id"] = portfolio_id

            return (
                session.findone("accounts", **query)
                if account_id
                else list(session.find("accounts", **query))
            )

    def get_positions(
        self, account_id: str, symbol: str = None
    ) -> Dict[str, vxPositionType]:
        """获取账户持仓

        Arguments:
            account_id {str} -- 账户ID
            symbol {str} -- 持仓证券symbol，若为None，则返回全部持仓 (default: {None})

        Returns:
            Dict[str, vxPositionType] -- 持仓信息
        """
        with self._db.start_session() as session:
            if symbol:
                pos = session.findone("positions", account_id=account_id, symbol=symbol)
                return vxCashPosition(pos.message) if symbol == "CNY" else pos

            _positions = {
                p.symbol: p for p in session.find("positions", account_id=account_id)
            }
            _positions["CNY"] = vxCashPosition(_positions["CNY"].message)

            return _positions

    def get_orders(
        self,
        account_id: str = None,
        order_id: str = None,
        exchange_order_id: str = None,
        filter_finished=False,
    ) -> Dict[str, vxOrder]:
        """查询订单信息

        Arguments:
            account_id {str} -- 账户ID
            order_id {str} -- 委托订单号 (default: {None})
            exchange_order_id {str} -- 交易所委托订单号 (default: {None})
            filter_finished {bool} -- 是否过滤已完成的订单 (default: {False})

        Returns:
            Dict[str, vxOrder] -- 委托订单
        """
        query = {}
        if account_id:
            query["account_id"] = account_id

        if order_id:
            query["order_id"] = order_id

        if exchange_order_id:
            query["exchange_order_id"] = exchange_order_id

        condisiotns = [
            f"""created_dt > {vxtime.today()}""",
            f"""created_dt < {self._settle_date} """,
        ]
        if filter_finished:
            condisiotns.append("""status in ("New", "PendingNew", "PartiallyFilled")""")

        with self._db.start_session(True) as session:
            cur = session.find("orders", *condisiotns, **query)
            return {o.exchange_order_id: o for o in cur}

    def get_execution_reports(
        self,
        account_id: str,
        trade_id: str = None,
        order_id: str = None,
        exchange_order_id: str = None,
    ) -> Dict[str, vxTrade]:
        """查询成交信息

        Arguments:
            account_id {str} -- 账户ID

        Returns:
            Dict[str, vxTrade] -- 成交回报
        """
        query = {"account_id": account_id}
        conditions = [
            f"""created_dt > {vxtime.today()}""",
            f"""created_dt < {self._settle_date} """,
        ]
        if trade_id:
            query["trade_id"] = trade_id
        if order_id:
            query["order_id"] = order_id
        if exchange_order_id:
            query["exchange_order_id"] = exchange_order_id
        with self._db.start_session(True) as session:
            cur = session.find("trades", *conditions, **query)
            return {t.trade_id: t for t in cur}

    def get_transferinfos(
        self,
        account_id: str,
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
    ) -> Dict[str, vxTransferInfo]:
        """查询资金流水

        Arguments:
            account_id {str} -- 账户ID

        Returns:
            Dict[str, vxTransferInfo] -- 资金流水
        """
        start_date = (
            combine_datetime(start_date, "00:00:00") if start_date else vxtime.today()
        )
        end_date = (
            combine_datetime(end_date, "23:59:59") if end_date else self._settle_date
        )

        with self._db.start_session() as session:
            cur = session.find(
                "transferinfos",
                f"created_dt > {start_date}",
                f"created_dt < {end_date}",
                account_id=account_id,
            )
            return {t.transfer_id: t for t in cur}

    def _update_position_frozens(
        self, session: vxDBSession, account_ids: List[str] = None
    ) -> None:
        """更新冻结仓位"""
        if not account_ids:
            account_ids = session.distinct("accounts", "account_id")

        # 将冻结仓位设置为0，可用资金恢复
        session.execute(
            f"""
                UPDATE positions
                SET frozen=0.0,
                    available=ROUND(volume,2)
                WHERE account_id in ('{"','".join(account_ids)}')
                
            """
        )
        session.execute(
            f"""
                UPDATE accounts
                SET frozen=0.0,
                    available=ROUND(balance,2)
                WHERE account_id in ('{"','".join(account_ids)}')
                
            """
        )

        conditions = [
            """
            status in (
                'PendingNew',
                'New',
                'PartiallyFilled'
            )
            """,
            f"""account_id in ('{"','".join(account_ids)}')""",
        ]

        cur = session.execute(
            f"""
            SELECT account_id, 
                   sum((volume-filled_volume)*price*1.003) as frozen 
            FROM orders
            WHERE {' AND '.join(conditions)}
            AND order_direction='Buy'
            GROUP BY account_id ;
            """
        )
        cash_frozens = [row._mapping for row in cur]
        if cash_frozens:
            session.execute(
                """ UPDATE positions
                    SET frozen=ROUND(:frozen,2) ,
                        available=ROUND(volume-:frozen,2)
                    WHERE account_id=:account_id
                    AND symbol='CNY' ;
                """,
                cash_frozens,
            )
            session.execute(
                """ UPDATE accounts
                    SET frozen=ROUND(:frozen,2) ,
                        available=ROUND(balance-:frozen,2)
                    WHERE account_id=:account_id ;
                """,
                cash_frozens,
            )

        cur = session.execute(
            f"""
                SELECT account_id, symbol, sum(volume-filled_volume) as frozen
                FROM orders
                WHERE {' AND '.join(conditions)}
                AND order_direction='Sell' 
                GROUP BY account_id, symbol ;
            """
        )
        symbol_frozens = [row._mapping for row in cur]
        if symbol_frozens:
            session.execute(
                """
                    UPDATE positions
                    SET frozen=ROUND(:frozen,2),
                        available=ROUND(volume-:frozen,2)
                    WHERE account_id=:account_id
                    AND symbol=:symbol
                    AND allow_t0 = true
                """,
                symbol_frozens,
            )
            session.execute(
                """
                    UPDATE positions
                    SET frozen=ROUND(:frozen,2),
                        available=ROUND(volume_his-:frozen,2)
                    WHERE account_id=:account_id
                    AND symbol=:symbol
                    AND allow_t0 = false
                """,
                symbol_frozens,
            )

    def order_volume(
        self,
        account_id: str,
        symbol: str,
        volume: float,
        price: float = None,
        check_channel: bool = True,
    ) -> vxOrder:
        """委托下单

        Arguments:
            account_id {str} -- 账户ID
            symbol {str} -- 证券代码
            volume {float} -- 委托数量，正数为买入，负数为卖出
            price {float} -- 委托价格,若price为None，则通过市价委托下单 (default: {None})
            check_channel {bool} -- 是否检查通道 (default: {True})

        Returns:
            vxOrder -- 下单的信息
        """
        if volume == 0:
            raise ValueError("volume can't be 0.")

        with self._db.start_session(True) as session:
            accountinfo = session.findone("accounts", account_id=account_id)

            if accountinfo is None:
                raise ValueError(f"account {account_id} not found.")

            if accountinfo.channel not in self._channels and check_channel:
                raise ValueError(f"channel {accountinfo.channel} not found.")

            tradeapi = self._channels.get(accountinfo.channel, None)

            order_type = OrderType.Limit
            if not price:
                ticks = tradeapi.current(symbol)
                price = ticks[symbol].ask1_p if volume > 0 else ticks[symbol].bid1_p

                order_type = (
                    OrderType.Limit
                    if vxMarketPreset(symbol).security_type == SecType.BOND_CONVERTIBLE
                    else OrderType.Market
                )

            vxorder = vxOrder(
                account_id=account_id,
                symbol=symbol,
                volume=abs(volume),
                price=price,
                order_offset="Open" if volume > 0 else "Close",
                order_direction="Buy" if volume > 0 else "Sell",
                order_type=order_type,
                status="New",
            )

            frozen_symbol = symbol if volume < 0 else "CNY"
            frozen_volume = abs(volume) if volume < 0 else price * volume * 1.003
            position = session.findone(
                "positions",
                f"available >= {frozen_volume}",
                account_id=vxorder.account_id,
                symbol=frozen_symbol,
            )
            if not position:
                raise (
                    NoEnoughCash(f"{frozen_symbol}可用资金不足，需要冻结资金{frozen_volume:,.2f}元")
                    if frozen_symbol == "CNY"
                    else NoEnoughPosition(f"{symbol}持仓可用持仓不足,冻结仓位{frozen_volume:,.2f}")
                )

            if check_channel:
                ret_orders = tradeapi.order_batch(vxorder)
            else:
                vxorder.exchange_order_id = vxorder.order_id
                ret_orders = [vxorder]

            session.save("orders", ret_orders[0])
            self._update_position_frozens(session=session, account_ids=[account_id])
            logger.info(
                f"[新增] 委托订单: {ret_orders[0].exchange_order_id} : {ret_orders[0]}"
            )
            if self._sched:
                self._sched.submit_event("on_order_status", ret_orders[0])

        return ret_orders[0]

    def order_cancel(self, order: vxOrder, check_channel: bool = True) -> None:
        """撤单

        Arguments:
            *orders {List[str]} -- 订单号
        """
        with self._db.start_session(True) as session:
            order = session.findone("orders", exchange_order_id=order.exchange_order_id)
            if order is None:
                raise ValueError(f"order {order.exchange_order_id} not found.")

            accountinfo = session.findone("accounts", account_id=order.account_id)

            if accountinfo is None:
                raise ValueError(f"account {order.account_id} not found.")

            if check_channel:
                if accountinfo.channel not in self._channels:
                    raise ValueError(f"channel {accountinfo.channel} not found.")
                tradeapi = self._channels[accountinfo.channel]
                tradeapi.order_cancel(order)
            else:
                order.status = "Canceled"
                self._sched.submit_event("on_broker_order_status", order)

    def _save_broker_account(
        self, session: vxDBSession, broker_account: vxAccountInfo
    ) -> str:
        """保存券商账户情况"""
        yesterday = session.max(
            "accounts",
            "settle_date",
            f"settle_date < {self._settle_date}",
            account_id=broker_account.account_id,
        )
        db_accountinfo = session.findone(
            "accounts",
            account_id=broker_account.account_id,
            settle_date=yesterday,
        )
        if not db_accountinfo:
            db_accountinfo = vxAccountInfo(broker_account.message)
            db_accountinfo.portfolio_id = "default"
            db_accountinfo.fund_shares = broker_account.nav
            db_accountinfo.asset_yd = broker_account.asset
            db_accountinfo.nav_yd = broker_account.nav
            db_accountinfo.fund_nav_yd = broker_account.fund_nav
            db_accountinfo.settle_date = self._settle_date
            db_accountinfo.channel = "physical"
        else:
            db_accountinfo.debt = broker_account.debt
            db_accountinfo.balance = broker_account.balance
            db_accountinfo.frozen = broker_account.frozen
            db_accountinfo.margin_available = broker_account.margin_available
            db_accountinfo.marketvalue = broker_account.marketvalue
            db_accountinfo.fnl = broker_account.fnl
            db_accountinfo.fund_shares = broker_account.fund_shares
            db_accountinfo.settle_date = self._settle_date

        session.save("broker_accounts", db_accountinfo)
        return broker_account.account_id

    def _update_order_filleds(
        self, session: vxDBSession, exchange_order_ids: List[str] = None
    ) -> None:
        """更新委托订单成交信息"""
        conditions = (
            [
                f"""exchange_order_id in ({"','".join(exchange_order_ids)})""",
            ]
            if exchange_order_ids
            else [
                f"""created_dt > {vxtime.today()}""",
                f"""created_dt < {self._settle_date}""",
            ]
        )
        cur = session.execute(
            f"""
            SELECT exchange_order_id, 
                order_direction,
                sum(volume) as filled_volume, 
                sum(price*volume) as filled_amount,
                sum(commission) as commission
            FROM trades
            WHERE {' AND '.join(conditions)}
            GROUP BY exchange_order_id,order_direction
        """
        )
        order_filleds = []
        for row in cur:
            if row._mapping["order_direction"] == "Buy":
                filled_amount = (
                    row._mapping["filled_amount"] + row._mapping["commission"]
                )
            else:
                filled_amount = (
                    row._mapping["filled_amount"] - row._mapping["commission"]
                )
            filled_vwap = filled_amount / row._mapping["filled_volume"]
            order_filleds.append(
                {
                    "exchange_order_id": row._mapping["exchange_order_id"],
                    "filled_volume": row._mapping["filled_volume"],
                    "filled_amout": filled_amount,
                    "filled_vwap": filled_vwap,
                }
            )

    def _update_accountinfos(
        self, session: vxDBSession, account_ids: List[str] = None
    ) -> None:
        if not account_ids:
            account_ids = session.distinct("accounts", "account_id")
        accountinfos = []
        cur_acc = session.find(
            "accounts",
            f"""account_id in ('{"','".join(account_ids)}')""",
            settle_date=self._settle_date,
        )
        for accountinfo in cur_acc:
            accountinfo.marketvalue = 0
            accountinfo.fnl = 0
            cur = session.find(
                "positions",
                account_id=accountinfo.account_id,
                settle_date=self._settle_date,
            )
            for p in cur:
                if p.symbol == "CNY":
                    p = vxCashPosition(**p.message)
                    accountinfo.balance = p.marketvalue
                    accountinfo.frozen = p.frozen
                else:
                    accountinfo.marketvalue += p.marketvalue
                    accountinfo.fnl += p.fnl
            accountinfos.append(accountinfo)
        session.save("accounts", accountinfos)

    def on_sync_brokerinfos(self, context: vxContext, event: vxEvent) -> None:
        """收到同步信息"""
        broker_account, broker_positions, broker_orders, broker_trades = event.data

        with self._db.start_session() as session:
            settle_date = self._settle_date
            logger.info(f"日结日期：{to_timestring(settle_date,'%Y-%m-%d')}")
            broker_account.portfolio_id = "default"
            broker_account.settle_date = settle_date

            account_id = self._save_broker_account(session, broker_account)
            logger.info(f"更新broker_accounts: {account_id} 基本信息")

            session.delete(
                "broker_positions", account_id=account_id, settle_date=settle_date
            )
            positions = []
            for p in broker_positions.values():
                p.portfolio_id = "default"
                p.settle_date = settle_date
                positions.append(p)
            session.save("broker_positions", positions)
            logger.info(f"更新broker_positions: {len(positions)}个")

            exchange_order_ids = session.distinct("orders", "exchange_order_id")
            if broker_orders:
                session.save("broker_orders", *broker_orders.values())
                for exchange_order_id in exchange_order_ids:
                    if exchange_order_id not in broker_orders:
                        continue
                    self._sched.submit_event(
                        "on_broker_order_status", broker_orders[exchange_order_id]
                    )

            if broker_trades:
                session.save("broker_trades", list(broker_trades.values()))
                saved_tradeids = session.distinct("trades", "trade_id")

                for broker_trade in broker_trades.values():
                    if broker_trade.exchange_order_id not in exchange_order_ids or (
                        broker_trade.trade_id in saved_tradeids
                    ):
                        continue
                    self._sched.submit_event("on_broker_execution_report", broker_trade)

    def on_price_change(self, context: vxContext, event: vxEvent) -> None:
        "更新行情事件"
        with self._db.start_session(True) as session:
            trade = event.data
            if trade:
                lasttrades = [
                    {
                        "symbol": trade.symbol,
                        "lasttrade": trade.price,
                        "created_dt": trade.created_dt,
                    }
                ]
            else:
                symbols = session.distinct("positions", "symbol", "symbol != 'CNY'")
                vxticks = self._mdapi.current(*symbols)
                lasttrades = [
                    {
                        "symbol": vxtick["symbol"],
                        "lasttrade": vxtick["lasttrade"],
                        "created_dt": vxtick["created_dt"],
                    }
                    for vxtick in vxticks.values()
                    if vxtick["lasttrade"] > 0
                ]
            if not lasttrades:
                return

            session.execute(
                f"""     
                UPDATE `positions` as t
                SET lasttrade=:lasttrade,
                    marketvalue=ROUND(t.volume * :lasttrade,2),
                    fnl = ROUND(t.volume * :lasttrade - t.cost,2),
                    updated_dt = :created_dt
                WHERE t.symbol = :symbol
                AND t.settle_date={self._settle_date};
                """,
                lasttrades,
            )
            cur = session.execute(
                f"""
                    SELECT  account_id,
                            SUM(marketvalue) as marketvalue,
                            SUM(fnl) as fnl
                    FROM positions
                    WHERE symbol !='CNY'
                    AND settle_date = {self._settle_date}
                    GROUP BY account_id;
                """
            )
            session.execute(
                f"""
                    UPDATE accounts
                    SET asset=ROUND(balance+:marketvalue,2),
                        nav=ROUND(balance+:marketvalue - debt,2),
                        marketvalue=ROUND(:marketvalue,2),
                        today_profit = ROUND(balance+:marketvalue-nav_yd-deposit + withdraw,2),
                        fnl=ROUND(:fnl,2),
                        fund_nav=ROUND((balance+:marketvalue - debt)/fund_shares,4)
                    WHERE account_id = :account_id
                    AND settle_date= {self._settle_date};
                """,
                [row._mapping for row in cur],
            )

    def on_broker_order_status(self, context: vxContext, event: vxEvent) -> None:
        # sourcery skip: extract-method
        "更新订单状态事件"
        broker_order = event.data
        if not isinstance(broker_order, vxOrder):
            logger.error(f"broker_order {broker_order} is not a vxOrder instance.")
            return

        if broker_order.status not in [
            OrderStatus.Canceled,
            OrderStatus.Expired,
            OrderStatus.Filled,
            OrderStatus.Rejected,
            OrderStatus.Suspended,
        ]:
            logger.info(
                "[忽略]{broker_order.exchange_order_id}非终态委托更新:"
                f" {broker_order.status} {broker_order.filled_volume}"
            )
            return

        with self._db.start_session(True) as session:
            vxorder = session.findone(
                "orders", exchange_order_id=broker_order.exchange_order_id
            )
            if not vxorder:
                logger.warning(f"未找到委托订单: {broker_order.exchange_order_id}")
                return

            vxorder.filled_volume = broker_order.filled_volume
            vxorder.filled_amount = broker_order.filled_amount
            vxorder.reject_code = broker_order.reject_code
            vxorder.reject_reason = broker_order.reject_reason
            vxorder.status = broker_order.status
            session.save("orders", vxorder)
            self._update_position_frozens(session, [vxorder.account_id])
            logger.info(f"[终结] 委托订单: {vxorder.exchange_order_id} {vxorder}")

            if self._sched:
                self._sched.submit_event("on_order_status", vxorder)

    def on_broker_execution_report(self, context: vxContext, event: vxEvent) -> None:
        "更新成交回报事件"
        broker_trade = event.data
        if not isinstance(broker_trade, vxTrade):
            logger.error(f"broker_trade {broker_trade} is not a vxTrade instance.")
            return

        if broker_trade.status != TradeStatus.Trade:
            return

        with self._db.start_session(True) as session:
            vxorder: vxOrder = session.findone(
                "orders", exchange_order_id=broker_trade.exchange_order_id
            )
            if not vxorder:
                logger.debug(
                    f"收到非委托下单: {broker_trade.exchange_order_id} {broker_trade.volume}"
                )
                return

            broker_trade.account_id = vxorder.account_id
            broker_trade.order_id = vxorder.order_id
            # 插入成交回报信息
            try:
                session.insert("trades", broker_trade)
                logger.info(
                    f"插入成交回报trade_id({broker_trade.trade_id})@exchange_order_id({vxorder.exchange_order_id})"
                    f"{broker_trade}"
                )
            except Exception as e:
                logger.error(f"成交回报信息已经存储,请勿重复插入: {broker_trade.trade_id}")
                return

            # 更新vxorder信息
            accountinfo = session.findone(
                "accounts", account_id=broker_trade.account_id
            )
            cash_position = session.findone(
                "positions", account_id=broker_trade.account_id, symbol="CNY"
            )
            cash_position = vxCashPosition(**cash_position.message)
            symbol_position = session.findone(
                "positions",
                account_id=broker_trade.account_id,
                symbol=broker_trade.symbol,
            )
            if not symbol_position:
                preset = vxMarketPreset(broker_trade.symbol)
                symbol_position = vxPosition(
                    portfolio_id=cash_position.portfolio_id,
                    account_id=cash_position.account_id,
                    security_type=preset.security_type,
                    symbol=broker_trade.symbol,
                    lasttrade=broker_trade.price,
                    allow_t0=preset.allow_t0,
                )
            symbol_position.lasttrade = broker_trade.price

            if broker_trade.order_direction == OrderDirection.Buy:
                filled_amount = (
                    broker_trade.price * broker_trade.volume + broker_trade.commission
                )
                cash_position.frozen -= (
                    broker_trade.price * broker_trade.volume
                ) * 1.003
                sub_volume(cash_position, filled_amount)
                symbol_position.volume_today += broker_trade.volume
                symbol_position.cost += filled_amount
                accountinfo.marketvalue += broker_trade.price * broker_trade.volume

            else:
                filled_amount = (
                    broker_trade.price * broker_trade.volume - broker_trade.commission
                )
                symbol_position.frozen -= broker_trade.volume
                symbol_position.cost -= filled_amount
                sub_volume(symbol_position, broker_trade.volume)

                cash_position.volume_today += filled_amount
                accountinfo.marketvalue -= broker_trade.price * broker_trade.volume

            vxorder.filled_amount += filled_amount
            vxorder.filled_volume += broker_trade.volume
            if 0 < vxorder.filled_volume < vxorder.volume:
                vxorder.status = OrderStatus.PartiallyFilled
            elif vxorder.filled_volume >= vxorder.volume:
                vxorder.filled_volume = vxorder.volume
                vxorder.status = OrderStatus.Filled

            accountinfo.frozen = cash_position.frozen
            accountinfo.balance = cash_position.marketvalue

            accountinfo.fnl -= broker_trade.commission
            session.save("orders", vxorder)
            session.save("positions", cash_position, symbol_position)
            session.save("accounts", accountinfo)

            logger.info(
                f"[更新] 委托订单: {vxorder.exchange_order_id} 已成交"
                f" {vxorder.filled_volume:,.2f}/{vxorder.volume:,.2f} 委托状态:"
                f" {vxorder.status}"
            )

            if self._sched:
                self._sched.submit_event("on_execution_report", broker_trade)
                self._sched.submit_event("on_order_status", vxorder)

    def after_close(self, context: vxContext, event: vxEvent) -> None:
        "收盘后事件"

        for tdapi in self._channels.values():
            broker_account = tdapi.get_account()
            broker_positions = tdapi.get_positions()
            broker_orders = tdapi.get_orders()
            broker_trades = tdapi.get_execution_reports()
            self._sched.submit_event(
                "on_sync_brokerinfos",
                (broker_account, broker_positions, broker_orders, broker_trades),
            )

    def on_settle(self, context: vxContext, event: vxEvent) -> None:
        """日结事件"""
        with self._db.start_session() as session:
            session.execute(
                """UPDATE orders 
                    SET status='Expired' 
                    WHERE  status in ('PendingNew',"New",'PartiallyFilled')
                    AND created_dt > ?
                    AND created_dt < ?;
                """,
                (vxtime.today(), self._settle_date),
            )
            self._update_position_frozens(session=session)
            self._update_accountinfos(session=session)

            accountinfos = list(session.find("accounts"))
            session.save("history_accounts", *accountinfos)
            logger.info(f"保存账户信息: {len(accountinfos)}个")

            positions = list(session.find("positions"))
            session.save("history_positions", *positions)
            logger.info(f"保存持仓信息: {len(positions)}个")
        self._sched.stop()

    def _update_settle_date(
        self, session: vxDBSession, settle_date: DateTimeType
    ) -> None:
        """更新结算日期

        Arguments:
            settle_date {DateTimeType} -- 结算日期
        """
        if settle_date is None:
            settle_date = vxtime.today("23:59:59")
        else:
            settle_date = combine_datetime(settle_date, "23:59:59")

        if settle_date <= self._settle_date:
            logger.error(
                f"新设置的结算日期: {to_timestring(settle_date,'%Y-%m-%d')}"
                f"小于当前结算日期({to_timestring(self._settle_date,'%Y-%m-%d')})"
            )
            return

        self.delete("positions", volume=0)
        self.execute(
            "UPDATE positions SET volume_today=0, volume_his=volume,  settle_date=? ;",
            (settle_date,),
        )
        self._update_position_frozens(session=session, account_ids=[])
        self._update_accountinfos(session=session, account_ids=[])
        self.execute(
            """ UPDATE accounts 
                SET today_profit=0,
                    deposit=0,
                    withdraw=0,
                    asset_yd=asset,
                    nav_yd=nav,
                    fund_nav_yd=fund_nav, 
                    settle_date=? ;
            """,
            (settle_date,),
        )
        logger.info(
            f"结算日期：{to_timestring(self._settle_date,'%Y-%m-%d')} ==>"
            f" {to_timestring(settle_date,'%Y-%m-%d')} ..."
        )
        self._settle_date = settle_date

    def day_begin(self, context: vxContext, event: vxEvent) -> None:
        """开盘前准备事件"""

        if vxtime.is_holiday():
            logger.info("今天是节假日，不进行交易")
            return

        with self._db.start_session() as session:
            self._update_settle_date(session, vxtime.today("23:59:59"))

        if vxtime.now() > vxtime.today("15:00:00"):
            logger.info("已经收盘，不进行交易")
            return

        self._sched.submit_event(
            "before_trade", trigger=vxOnceTrigger(vxtime.today("09:15:00"))
        )
        self._sched.submit_event(
            "on_trade", trigger=vxOnceTrigger(vxtime.today("09:30:10"))
        )
        self._sched.submit_event(
            "noon_break_start", trigger=vxOnceTrigger(vxtime.today("11:30:00"))
        )
        self._sched.submit_event(
            "noon_break_end", trigger=vxOnceTrigger(vxtime.today("13:00:00"))
        )
        self._sched.submit_event(
            "before_close", trigger=vxOnceTrigger(vxtime.today("14:45:00"))
        )
        self._sched.submit_event(
            "on_close", trigger=vxOnceTrigger(vxtime.today("14:55:00"))
        )
        self._sched.submit_event(
            "after_close", trigger=vxOnceTrigger(vxtime.today("15:30:10"))
        )
        self._sched.submit_event(
            "on_settle", trigger=vxOnceTrigger(vxtime.today("16:30:00"))
        )

        self._sched.submit_event(
            "on_tick",
            trigger=vxIntervalTrigger(
                1,
                start_dt=vxtime.today("09:30:00"),
                end_dt=vxtime.today("11:30:00"),
            ),
        )
        self._sched.submit_event(
            "on_tick",
            trigger=vxIntervalTrigger(
                1,
                start_dt=vxtime.today("13:00:00"),
                end_dt=vxtime.today("15:00:00"),
            ),
        )

        if vxtime.today("09:15:00") < vxtime.now() < vxtime.today("15:00:00"):
            self._sched.submit_event("before_trade")

    def register_scheduler(self, sched: vxScheduler):
        """注册事件处理器

        Arguments:
            sched {vxScheduler} -- _description_
        """
        sched.register("on_tick", handler=self.on_price_change)
        sched.register("on_broker_order_status", handler=self.on_broker_order_status)
        sched.register(
            "on_broker_execution_report", handler=self.on_broker_execution_report
        )
        sched.register("on_sync_brokerinfos", handler=self.on_sync_brokerinfos)
        sched.register("after_close", handler=self.after_close)
        sched.register("before_day", handler=self.day_begin)
        self._sched = sched


if __name__ == "__main__":
    teller = vxTellerAPI("sqlite:///data/test.db")
    accountinfo = teller.create_account(
        portfolio_id="test",
        account_id="acc_for_test",
        init_balance=1000000,
        if_exists="delete",
    )
    print(accountinfo)
    print("get_accounts:")
    print(teller.get_accounts(account_id="acc_for_test"))
    print("get_positions")
    print(teller.get_positions("acc_for_test"))
    print("get_orders")
    print(teller.get_orders("acc_for_test"))
    print("get_execution_report")
    print(teller.get_execution_reports("acc_for_test"))
    order = teller.order_volume("acc_for_test", "SHSE.600000", 1000, 10.3, False)
    print(order)

    teller.order_cancel(order, check_channel=False)
    print("get_orders")
    print(teller.get_orders("acc_for_test"))
