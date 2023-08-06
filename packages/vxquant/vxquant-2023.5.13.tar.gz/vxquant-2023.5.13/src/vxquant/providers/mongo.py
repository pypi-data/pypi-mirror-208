"""mongodb providers"""

from typing import Dict, Union, List
from multiprocessing import Lock
from vxsched import vxscheduler
from vxquant.model.typehint import InstrumentType
from vxquant.model.contants import (
    OrderDirection,
    OrderType,
    OrderStatus,
    OrderOffset,
    OrderRejectReason,
)
from vxquant.providers.base import (
    vxGetAccountProvider,
    vxGetOrdersProvider,
    vxGetPositionsProvider,
    vxGetExecutionReportsProvider,
    vxOrderBatchProvider,
    vxOrderCancelProvider,
)
from vxquant.model.exchange import (
    vxAccountInfo,
    vxOrder,
    vxPosition,
    vxCashPosition,
    vxTrade,
)
from vxutils import logger
from vxutils.database.dbproxy import vxMongoProxy

_mongodb_lock = Lock()


class vxMongoGetAccountProvider(vxGetAccountProvider):
    def __init__(self) -> None:
        if "dbconn" not in self.context.keys():
            db_params = self.context.settings.get("db_params", {})
            self.context.dbconn = vxMongoProxy(**db_params)
        self._accounts = self.context.dbconn["accounts"]
        self._positions = self.context.dbconn["positions"]

    def __call__(self, account_id: str = None) -> vxAccountInfo:
        item = self._accounts.find_one({"account_id": account_id}, {"_id": 0})
        accountinfo = vxAccountInfo(dict(item))
        item = self._positions.find_one({"account_id": account_id, "symbol": "CNY"})
        accountinfo.balance = item["volume"]
        accountinfo.frozen = item["frozen"]

        items = list(
            self._positions.aggreate(
                [
                    {"$match": {"account_id": account_id, "symbol": {"$ne": "CNY"}}},
                    {
                        "$group": {
                            "marketvalue": {"$sum": "marketvalue"},
                            "fnl": {"$sum": "fnl"},
                        }
                    },
                ]
            )
        )
        if items:
            accountinfo.marketvalue = items[0]["marketvalue"]
            accountinfo.fnl = item[0]["fnl"]
        else:
            accountinfo.marketvalue = 0
            accountinfo.fnl = 0
        return accountinfo


class vxMongoGetPositionsProvider(vxGetPositionsProvider):
    def __init__(self) -> None:
        if "dbconn" not in self.context.keys():
            db_params = self.context.settings.get("db_params", {})
            self.context.dbconn = vxMongoProxy(**db_params)
        self._positions = self.context.dbconn["positions"]

    def __call__(
        self, symbol: InstrumentType = None, acccount_id: str = None
    ) -> Dict[InstrumentType, Union[vxPosition, vxCashPosition]]:
        if acccount_id is None:
            raise ValueError("未指定account_id")

        query = {"account_id": acccount_id}
        if symbol:
            query["symbol"] = symbol

        cur = self._positions.find(query, {"_id": 0})
        return {
            item["symbol"]: vxPosition(item)
            if item["symbol"] != "CNY"
            else vxCashPosition(item)
            for item in cur
        }


class vxMongoGetOrdersProvider(vxGetOrdersProvider):
    def __init__(self) -> None:
        if "dbconn" not in self.context.keys():
            db_params = self.context.settings.get("db_params", {})
            self.context.dbconn = vxMongoProxy(**db_params)
        self._orders = self.context.dbconn["orders"]

    def __call__(
        self, account_id: str = None, filter_finished: bool = False
    ) -> Dict[str, vxOrder]:
        if account_id is None:
            raise ValueError("未指定account_id")

        query = {"account_id": account_id}
        if filter_finished:
            query["status"] = {"$in": ["PendingNew", "New", "PartiallyFilled"]}
        cur = self._orders.find(query, {"_id": 0})
        return {item["order_id"]: vxOrder(item) for item in cur}


class vxMongoGetExecutionReportsProvider(vxGetExecutionReportsProvider):
    def __init__(self) -> None:
        if "dbconn" not in self.context.keys():
            db_params = self.context.settings.get("db_params", {})
            self.context.dbconn = vxMongoProxy(**db_params)
        self._trades = self.context.dbconn["trades"]

    def __call__(
        self, account_id: str = None, order_id: str = None, trade_id: str = None
    ) -> Dict[str, vxTrade]:
        query = {"account_id": account_id}
        if order_id:
            query["order_id"] = order_id
        if trade_id:
            query["trade_id"] = trade_id

        cur = self._db.trades.find(query, {"_id": 0})
        return {item["trade_id"]: vxTrade(item) for item in cur}


def _frozen_position(dbconn, vxorder) -> bool:
    """冻结仓位"""
    if vxorder.order_direction == OrderDirection.Buy:
        frozen_symbol = "CNY"
        frozen_volume = vxorder.volume * vxorder.price * 1.003
    else:
        frozen_symbol = vxorder.symbol
        frozen_volume = vxorder.volume

    with dbconn.start_session(lock=_mongodb_lock) as session:
        ret_cur = dbconn.positions.update_one(
            {
                "account_id": vxorder.account_id,
                "symbol": frozen_symbol,
                "available": {"$gte": frozen_volume},
            },
            {"$inc": {"frozen": frozen_volume, "available": -frozen_volume}},
            session=session,
        )
        if ret_cur.matched_count == 0:
            vxorder.status = OrderStatus.Rejected
            vxorder.reject_code = (
                OrderRejectReason.NoEnoughCash
                if frozen_symbol == "CNY"
                else OrderRejectReason.NoEnoughPosition
            )
            vxorder.reject_reason = (
                f"账户({vxorder.account_id}) 冻结{frozen_symbol}资金 :{frozen_volume} 失败。"
            )
        else:
            vxorder.status = OrderStatus.PendingNew

        dbconn.orders.update_one(
            {"order_id": vxorder.order_id}, {"$set": vxorder.message}, session=session
        )

    return vxorder


def _update_frozen(self, account_id, symbol, volume, session) -> bool:
    ret_cur = self._db.positions.update_one(
        {"account_id": account_id, "symbol": symbol, "frozen": {"$get": volume}},
        {"$inc": {"frozen": -volume, "available": volume}},
        session=session,
    )
    if ret_cur.matched_count == 0:
        raise ValueError(f"账号({account_id}) 解冻{symbol}仓位 {volume} 失败.")
    if symbol == "CNY":
        self._db.accounts.update_one(
            {
                "account_id": account_id,
            },
            {"$inc": {"frozen": -volume, "available": volume}},
            session=session,
        )
    return True


class vxMongoOrderBatchProvider(vxOrderBatchProvider):
    def __init__(self) -> None:
        if "dbconn" not in self.context.keys():
            db_params = self.context.settings.get("db_params", {})
            self.context.dbconn = vxMongoProxy(**db_params)
        self._dbconn = self.context.dbconn

    def __call__(self, *vxorders) -> List[vxOrder]:
        submit_orders = []

        for order in vxorders:
            if not isinstance(order, vxOrder):
                logger.warning(f"order 类型不正确 : {type(order)}")
                continue

            frozen_order = _frozen_position(self._dbconn, order)

            if frozen_order.status == OrderStatus.Rejected:
                vxscheduler.submit_event("on_order_status", data=frozen_order)
            submit_orders.append(order)
        vxscheduler.submit_event("on_submit_order_batch", data=submit_orders)
        return submit_orders


class vxMongoOrderCancelProvider(vxOrderCancelProvider):
    def __init__(self) -> None:
        if "dbconn" not in self.context.keys():
            db_params = self.context.settings.get("db_params", {})
            self.context.dbconn = vxMongoProxy(**db_params)
        self._dbconn = self.context.dbconn

    def __call__(self, *vxorders) -> None:
        vxscheduler.submit_event("on_submit_order_cancel", data=vxorders)


@vxscheduler.event_handler("on_order_status")
def on_order_status(context, event):
    vxorder = event.data
    if vxorder.status in [OrderStatus.Rejected,OrderStatus.Suspended,OrderStatus.Filled,OrderStatus.Canceled]:
