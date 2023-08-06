import polars as pl
from multiprocessing import Lock
from typing import Dict, Union
from collections import defaultdict
from vxquant.model.typehint import DateTimeType
from vxquant.model.preset import vxMarketPreset
from vxquant.model.contants import (
    OrderDirection,
    OrderRejectReason,
    OrderStatus,
    TransferDirection,
)
from vxquant.model.exchange import (
    vxAccountInfo,
    vxPosition,
    vxCashPosition,
    vxOrder,
    vxTrade,
    vxTransferInfo,
)
from vxquant.exceptions import NoEnoughPosition, NoEnoughCash
from vxutils import vxtime, logger, to_json, to_timestring


def sub_volume(
    position: Union[vxCashPosition, vxPosition], volume: Union[float, int]
) -> Union[vxCashPosition, vxPosition]:
    if volume > position.available:
        raise NoEnoughPosition(
            f"{position.symbol}可用余额({position.available:,.2f}) 小于需扣减{volume:,.2f}"
        )

    delta = position.volume_his - volume
    position.volume_his = max(delta, 0)
    position.volume_today += min(delta, 0)
    return position


class vxStockAccount:
    def __init__(
        self,
        accountinfo: vxAccountInfo,
        positions: Dict = None,
        orders: Dict = None,
        trades: Dict = None,
        transferinfos: Dict = None,
        portfolio_id: str = None,
    ) -> None:
        self._portfolio_id = accountinfo.portfolio_id
        self._account_id = accountinfo.account_id
        self._accountinfo = accountinfo
        self._positions = positions or {
            "CNY": vxCashPosition(
                portfolio_id=self._portfolio_id, account_id=self._account_id
            )
        }
        if orders:
            self._unfinished_orders = {
                order.order_id: order
                for order in orders.values()
                if order.status in ["PendingNew", "New", "PartialyFilled"]
            }
            self._orders = orders
        else:
            self._unfinished_orders = {}
            self._orders = {}
        self._trades = trades or {}
        self._transferinfos = transferinfos or []
        self._lock = Lock()

    def __str__(self) -> str:
        return to_json(self.message)

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def portfolio_id(self) -> str:
        return self._portfolio_id

    @property
    def message(self) -> Dict:
        message = self.account_info.message
        message["positions"] = {
            symbol: position.message for symbol, position in self._positions.items()
        }
        message["orders"] = {
            order_id: order.message for order_id, order in self._orders.items()
        }
        message["trades"] = {
            trade_id: trade.message for trade_id, trade in self._trades.items()
        }
        message["transferinfos"] = [
            transferinfo.message for transferinfo in self._transferinfos
        ]
        return message

    @classmethod
    def load_account(
        cls, portfolio_id: str = None, account_id: str = None
    ) -> "vxStockAccount":
        return None

    @classmethod
    def create_account(
        cls, account_id: str, init_balance: float = 0.0, portfolio_id=None
    ) -> "vxStockAccount":
        account = cls.load_account(portfolio_id=portfolio_id, account_id=account_id)
        if account:
            return account

        accountinfo = vxAccountInfo(
            portfolio_id=portfolio_id,
            account_id=account_id,
            fund_nav_yd=1.0,
            asset_yd=0,
            nav_yd=0,
        )

        account = vxStockAccount(accountinfo)
        account.deposit(init_balance)
        return account

    @property
    def account_info(self) -> vxAccountInfo:
        self._accountinfo.marketvalue = 0
        self._accountinfo.fnl = 0
        for p in self._positions.values():
            if p.symbol == "CNY":
                self._accountinfo.frozen = p.frozen
                self._accountinfo.balance = p.marketvalue
            else:
                self._accountinfo.marketvalue += p.marketvalue
                self._accountinfo.fnl += p.fnl

        return self._accountinfo

    @property
    def cash(self) -> vxCashPosition:
        return self._positions["CNY"]

    @property
    def positions(self) -> Dict[str, vxPosition]:
        return self._positions

    def deposit(
        self,
        amount: float = 0.0,
        transfer_dt: DateTimeType = None,
    ) -> vxTransferInfo:
        """转入金额"""
        if amount <= 0.0:
            raise ValueError(f"转入金额amount({amount})必须大于0.0")

        transfer_dt = transfer_dt or vxtime.now()

        transferinfo = vxTransferInfo(
            account_id=self._account_id,
            amount=amount,
            transfer_direction=TransferDirection.In,
            created_dt=transfer_dt,
        )
        with self._lock:
            self.cash.volume_today += amount
            self._transferinfos.append(transferinfo)
            self.account_info.fund_shares += amount / self.account_info.fund_nav_yd
            self.account_info.deposit += amount

        return transferinfo

    def withdraw(
        self, amount: float = 0.0, transfer_dt: DateTimeType = None
    ) -> vxTransferInfo:
        """转出金额"""
        if amount <= 0.0:
            raise ValueError(f"转出金额amount({amount})必须大于0.0")

        transfer_dt = transfer_dt or vxtime.now()

        transferinfo = vxTransferInfo(
            account_id=self._account_id,
            amount=amount,
            transfer_direction=TransferDirection.Out,
            created_dt=transfer_dt,
        )
        with self._lock:
            sub_volume(self.cash, amount)
            self._transferinfos.append(transferinfo)
            self.account_info.fund_shares -= amount / self.account_info.fund_nav
            self.account_info.withdraw += amount
        return transferinfo

    def __getitem__(self, symbol: str) -> Union[vxCashPosition, vxPosition]:
        position = self._positions.get(symbol, None)
        if position is None:
            position = vxPosition(
                portfolio_id=self._portfolio_id,
                account_id=self._account_id,
                symbol=symbol,
                security_type=vxMarketPreset(symbol).security_type,
                allow_t0=vxMarketPreset(symbol).allow_t0,
            )

        return position

    def require_position(self, symbol: str) -> vxPosition:
        if symbol not in self._positions:
            self._positions[symbol] = vxPosition(
                portfolio_id=self._portfolio_id,
                account_id=self._account_id,
                symbol=symbol,
                security_type=vxMarketPreset(symbol).security_type,
                allow_t0=vxMarketPreset(symbol).allow_t0,
            )

        return self._positions[symbol]

    def get_orders(self, exchange_order_id: str = None) -> Union[str, vxOrder]:
        if exchange_order_id is None:
            return self._orders
        else:
            return self._orders.get(exchange_order_id, None)

    def get_trades(
        self,
        order_id: str = None,
        trade_id: str = None,
    ) -> Union[str, vxTrade]:
        if trade_id is not None:
            return self._trades.get(trade_id, None)

        if order_id is not None:
            return {
                trade_id: trade
                for trade_id, trade in self._trades.items()
                if trade.order_id == order_id
            }
        return self._trades

    @property
    def _position_frozens(self) -> Dict[str, float]:
        frozens = defaultdict(lambda: 0.0)
        for order in self._unfinished_orders.values():
            if order.status not in [
                OrderStatus.PendingNew,
                OrderStatus.New,
                OrderStatus.PartiallyFilled,
            ]:
                continue

            if order.order_direction == OrderDirection.Buy:
                frozens["CNY"] += max(
                    order.price * (order.volume - order.filled_volume) * 1.03, 0
                )
            else:
                frozens[order.symbol] += max(order.volume - order.filled_volume, 0)

        return frozens

    def frozen_order(self, vxorder: vxOrder) -> bool:
        with self._lock:
            if vxorder.order_direction == OrderDirection.Buy:
                frozen_volume = vxorder.volume * vxorder.price * 1.03
                if frozen_volume > self.cash.available:
                    raise NoEnoughCash(
                        f"需要冻结{frozen_volume:,.2f},可用余额: {self.cash.available:,.2f}不足。"
                    )
                vxorder = vxOrder(vxorder.message)
                self._unfinished_orders[vxorder.order_id] = vxorder
                self._orders[vxorder.order_id] = vxorder
                self.cash.frozen = self._position_frozens["CNY"]
            else:
                frozen_volume = vxorder.volume
                position = self.__getitem__(vxorder.symbol)
                if frozen_volume > position.available:
                    raise NoEnoughPosition(
                        f"需要冻结{frozen_volume:,.2f},可用仓位: {position.avaliable:,.2f}"
                    )
                vxorder = vxOrder(vxorder.message)
                self._unfinished_orders[vxorder.order_id] = vxorder
                self._orders[vxorder.order_id] = vxorder
                position.frozen = self._position_frozens[vxorder.symbol]

    def _release_order(self, vxorder: vxOrder) -> bool:
        self._unfinished_orders.pop(vxorder.order_id, None)
        if vxorder.order_direction == OrderDirection.Buy:
            self.cash.frozen = self._position_frozens["CNY"]
        else:
            self._positions[vxorder.symbol].frozen = self._position_frozens[
                vxorder.symbol
            ]

    def on_tick(self, vxticks):
        with self._lock:
            [
                self._positions[symbol].update(lasttrade=vxticks[symbol].lasttrade)
                for symbol in set(self._positions.keys()) & set(vxticks.keys())
            ]

    def on_order_status(self, vxorder: vxOrder) -> None:
        with self._lock:
            if self._orders[vxorder.order_id].filled_volume > vxorder.filled_volume:
                logger.warning(
                    f"收到异常的order状态更新: 存档状态 {self._orders[vxorder.order_id]}，最新order:"
                    f" {vxorder}"
                )
                return
            if vxorder.order_id not in self._unfinished_orders:
                return

            self._orders[vxorder.order_id].status = vxorder.status
            self._orders[vxorder.order_id].reject_code = vxorder.reject_code
            self._orders[vxorder.order_id].reject_reason = vxorder.reject_reason

            if vxorder.status not in [
                OrderStatus.Filled,
                OrderStatus.Canceled,
                OrderStatus.Rejected,
                OrderStatus.Suspended,
            ]:
                # 未终止的委托订单，按照收到成交回报进行更新。
                return

            # 已经终结的委托订单，更新状态并更新冻结金额
            self._orders[vxorder.order_id].exchange_order_id = vxorder.exchange_order_id
            self._orders[vxorder.order_id].filled_volume = vxorder.filled_volume
            self._orders[vxorder.order_id].filled_amount = vxorder.filled_amount
            self._release_order(vxorder)

    def on_execution_reports(self, vxtrade: vxTrade) -> None:
        with self._lock:
            # 成交回报信息入库
            self._trades[vxtrade.trade_id] = vxtrade
            # 更新position
            if vxtrade.order_id in self._unfinished_orders:
                self._unfinished_orders[vxtrade.order_id].exchange_order_id = (
                    vxtrade.exchange_order_id
                )
                self._unfinished_orders[
                    vxtrade.order_id
                ].filled_volume += vxtrade.volume
                self._unfinished_orders[vxtrade.order_id].filled_amount += (
                    vxtrade.price * vxtrade.volume
                )

            if vxtrade.order_direction == OrderDirection.Buy:
                cash_use = vxtrade.price * vxtrade.volume + vxtrade.commission
                self.cash.frozen = self._position_frozens["CNY"]
                sub_volume(self.cash, cash_use)
                position = self.require_position(vxtrade.symbol)
                position.volume_today += vxtrade.volume
                position.cost += cash_use
                position.lasttrade = vxtrade.price
            else:
                cash_got = vxtrade.price * vxtrade.volume - vxtrade.commission
                self._position[vxtrade.symbol] = self._position_frozens[vxtrade.symbol]
                position = self.require_position(vxtrade.symbol)
                sub_volume(position, vxtrade.volume)
                self.cash.volume_today += cash_got
                position.lasttrade = vxtrade.price

    def on_settle(self, settle_date: DateTimeType = None, vxticks: Dict = None) -> None:
        """每日日结"""
        settle_date = to_timestring(settle_date or vxtime.today(), "%Y-%m-%d")
        logger.warning("=" * 60)
        logger.info(f"账号: {self._account_id} 结算日: {settle_date}")
        # 1. unfinished_orders 需要设置未expired状态
        for order in self._unfinished_orders.values():
            logger.info(f"委托订单{order.order_id} 设置未 Expired。")
            order.status = OrderStatus.Expired
        self._unfinished_orders = {}
        # 2. 更新lasttrade/更新positions
        if vxticks:
            self.on_tick(vxticks)
        logger.info(f"持仓股票({len(vxticks) if vxticks else 0}只) 更新最新成交价格.")
        # 3. 清空orders/trades/transferinfos列表
        positions = []
        for p in self._positions.values():
            p.frozen = 0
            positions.append(p.message)

        accounts = pl.DataFrame([self.account_info.message])
        positions = pl.DataFrame(positions)
        orders = pl.DataFrame([o.message for o in self._orders.values()])
        trades = pl.DataFrame([o.message for o in self._trades.values()])
        transferinfos = pl.DataFrame([t.message for t in self._transferinfos])
        # 4. 更新account_info列表
        logger.info(f"账户信息: {accounts}")
        logger.info(f"持仓信息: {positions}")
        logger.info(f"委托订单信息: {orders}")
        logger.info(f"成交回报信息: {trades}")
        logger.info(f"资金转账信息: {transferinfos}")

        return accounts, positions, orders, trades, transferinfos

    def after_settle(self, settle_date: DateTimeType = None) -> None:
        """日结后资料"""
        self._account_info.asset_yd = self._account_info.asset
        self._account_info.nav_yd = self._account_info.nav
        self._account_info.fund_nav_yd = self._account_info.fund_nav
        self._account_info.settle_date = settle_date or vxtime.today()
        self._account_info.deposit = 0
        self._account_info.withdraw = 0

        for p in self._positions.values():
            p.volume_his = p.volume
            p.volume_today = 0

        self._unfinished_orders = {}
        self._orders = {}
        self._trades = {}
        self._transferinfos = []


if __name__ == "__main__":
    a = vxStockAccount.create_account(account_id="test", init_balance=1000000)
    a.withdraw(100)
    a.deposit(100)
    # print(a.account_info)

    order = vxOrder(
        account_id="test",
        symbol="SHSE.513500",
        order_direction="Buy",
        order_offset="Open",
        order_type="Limit",
        volume=10000,
        price=1.0,
        status="PendingNew",
    )
    # * print(order)
    a.frozen_order(order)
    assert a.cash.frozen == 10300
    # * print(a["CNY"])
    trade = vxTrade(
        account_id="test",
        order_id=order.order_id,
        exchange_order_id="exchange_order_idxxxxxxx1",
        symbol="SHSE.513500",
        order_direction=order.order_direction,
        order_offset=order.order_offset,
        order_type=order.order_type,
        volume=1000,
        price=0.9,
        commission=5,
    )
    a.on_execution_reports(trade)

    trade2 = vxTrade(
        account_id="test",
        order_id=order.order_id,
        exchange_order_id="exchange_order_idxxxxxxx2",
        symbol="SHSE.513500",
        order_direction=order.order_direction,
        order_offset=order.order_offset,
        order_type=order.order_type,
        volume=1000,
        price=1,
        commission=50,
    )
    a.on_execution_reports(trade2)
    a.on_settle("2023-03-07")
    # * order.filled_volume = 10000
    # * order.filled_amount = 0.9 * 1000 + 5 + 1000 + 50
    # * order.status = "Canceled"
    # * a.on_order_status(order)
    # * trade2 = vxTrade(
    # *     account_id="test",
    # *     order_id=order.order_id,
    # *     exchange_order_id="exchange_order_idxxxxxxx2",
    # *     symbol="SHSE.513500",
    # *     order_direction=order.order_direction,
    # *     order_offset=order.order_offset,
    # *     order_type=order.order_type,
    # *     volume=1000,
    # *     price=1,
    # *     commission=50,
    # * )

    # * # print(a["SHSE.513500"])
    # * print(a)
