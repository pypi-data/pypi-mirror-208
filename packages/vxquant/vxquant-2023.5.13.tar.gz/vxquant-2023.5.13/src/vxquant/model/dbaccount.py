"""基于mongodb的多账户管理"""

import polars as pl
import uuid
from pymongo import UpdateMany, UpdateOne, InsertOne, IndexModel, DeleteMany, DeleteOne
from vxquant.model.contants import OrderDirection, OrderOffset, OrderType, OrderStatus
from vxquant.model.exchange import (
    vxAccountInfo,
    vxOrder,
    vxTrade,
    vxCashPosition,
    vxPosition,
)
from vxquant.model.preset import vxMarketPreset
from vxquant.exceptions import NoEnoughCash, NoEnoughPosition
from vxsched import vxengine
from vxutils import logger, vxtime, singleton


@singleton
class AccountManager:
    def __init__(self, db, publisher, hqfetcher):
        self._db = db
        self._publisher = publisher
        self._hqfetcher = hqfetcher

    def register_engine(self, engine=None):
        engine = engine or vxengine
        engine.register("on_order_status", self.on_order_status)
        engine.register("on_execution_reports", self.on_execution_report)

    def create_account(
        self,
        account_id=None,
        portfolio_id=None,
        balance=1000000.00,
        channel_name="simtrade",
        on_error="skip",
    ) -> vxAccountInfo:
        account = self._db.accounts.find_one({"account_id": account_id})
        if account and on_error == "skip":
            logger.warning(f"账号: {account_id} 已存在，无需创建。 ")
            return account

        if account:
            logger.warning(f"账号{account_id}已存在，删除原来账号各类信息.")
            self._db.accounts.delete_many({"account_id": account_id})
            self._db.positions.delete_many({"account_id": account_id})
            self._db.orders.delete_many({"account_id": account_id})
            self._db.trades.delete_many({"account_id": account_id})

        account_id = account_id or str(uuid.uuid4())
        portfolio_id = portfolio_id or str(uuid.uuid4())
        account_info = vxAccountInfo(
            account_id=account_id,
            portfolio_id=portfolio_id,
            deposit=balance,
            balance=balance,
            marketvalue=0,
            fund_shares=balance,
            fund_nav_yd=1.0,
            settle_day=vxtime.today("00:00:00") - 60 * 60 * 24,
            channel=channel_name,
        )

        cash_position = vxCashPosition(
            portfolio_id=portfolio_id,
            account_id=account_id,
            volume_today=balance,
        )
        with self._db.start_session() as session:
            self._db.accounts.insert_one(account_info.message, session=session)
            self._db.positions.insert_one(cash_position.message, session=session)
        return account_info

    def get_account(self, account_id):
        item = self._db.accounts.find_one({"account_id": account_id}, {"_id": 0})
        return vxAccountInfo(dict(item))

    def get_orders(self, account_id, order_id=None, unfinished=False, df=False):
        query = {"account_id": account_id}
        if order_id:
            query["order_id"] = order_id

        if unfinished:
            query["status"] = {"$in": ["PendingNew", "New", "PartiallyFilled"]}

        cur = self._db.orders.find(query, {"_id": 0})

        return (
            pl.DataFrame([dict(item) for item in cur])
            if df
            else {item["order_id"]: vxOrder(item) for item in cur}
        )

    def get_execution_reports(self, account_id, order_id=None, df=False):
        query = {"account_id": account_id}
        if order_id:
            query["order_id"] = order_id

        cur = self._db.trades.find(query, {"_id": 0})
        return (
            pl.DataFrame([dict(item) for item in cur])
            if df
            else {item["trade_id"]: vxTrade(item) for item in cur}
        )

    def get_positions(self, account_id, symbol=None, df=False):
        query = {"account_id": account_id}
        if symbol:
            query["symbol"] = symbol

        cur = self._db.positions.find(query, {"_id": 0})
        return (
            pl.DataFrame([dict(item) for item in cur])
            if df
            else {
                item["symbol"]: (
                    vxPosition(item)
                    if item["symbol"] != "CNY"
                    else vxCashPosition(item)
                )
                for item in cur
            }
        )

    def _frozen_position(self, account_id, symbol, volume, session) -> bool:
        """冻结仓位"""

        ret_cur = self._db.positions.update_one(
            {
                "account_id": account_id,
                "symbol": symbol,
                "available": {"$gte": volume},
            },
            {"$inc": {"frozen": volume, "available": -volume}},
            session=session,
        )
        if ret_cur.matched_count == 0:
            raise (
                NoEnoughCash(f"账户({account_id}) 冻结{symbol}资金 :{volume} 失败。")
                if symbol == "CNY"
                else NoEnoughPosition(f"账户({account_id}) 冻结{symbol}仓位 :{volume} 失败。")
            )

        if symbol == "CNY":
            self._db.accounts.update_one(
                {
                    "account_id": account_id,
                },
                {"$inc": {"frozen": volume, "available": -volume}},
                session=session,
            )
        return True

    def _release_positon(self, account_id, symbol, volume, session) -> bool:
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

    def order_batch(self, account_id, orders):
        submit_orders = []
        with self._db.start_session() as session:
            for order in orders:
                if not isinstance(order, vxOrder):
                    logger.warning(f"order 类型不正确 : {type(order)}")
                    continue
                order.account_id = account_id
                if order.order_direction == OrderDirection.Buy:
                    frozen_volume = order.volume * order.price * 1.003
                    frozen_symbol = "CNY"
                else:
                    frozen_volume = order.volume
                    frozen_symbol = order.symbol

                try:
                    self._frozen_position(
                        account_id=account_id,
                        symbol=frozen_symbol,
                        volume=frozen_volume,
                        session=session,
                    )
                    self._db.orders.insert_one(order.message)
                    submit_orders.append(order)
                except ValueError as e:
                    logger.error(e)

        item = self._db.accounts.find_one(
            {"account_id": account_id}, {"account_id": 1, "channel": 1}
        )
        channel = item["channel"]
        self._publisher("submit_order_batch", submit_orders, channel=channel)
        return submit_orders

    def order_volume(self, account_id, symbol, volume, price: float = 0.0) -> vxOrder:
        if volume == 0:
            raise ValueError(f"volume 不能为 {volume}")

        if price <= 0.0:
            tick = self._hqfetcher(symbol)[symbol]

        order = vxOrder(
            account_id=account_id,
            symbol=symbol,
            order_direction=OrderDirection.Buy if volume > 0 else OrderDirection.Sell,
            order_offset=OrderOffset.Open if volume > 0 else OrderOffset.Close,
            order_type=OrderType.Limit if price > 0 else OrderType.Market,
            volume=abs(int(volume)),
            price=price or tick.lasttrade,
            status=OrderStatus.PendingNew,
        )
        return self.order_batch(account_id=account_id, orders=[order])

    def on_order_status(self, context, event) -> vxOrder:
        vxorder = event.data
        if vxorder.status == OrderStatus.PendingNew:
            self._db.orders.insert_one(vxorder.message)
            return

        self._db.orders.update_one
        (
            {
                "order_id": vxorder.order_id,
                "status": {
                    "$in": ["PendingNew", "New", "PartiallyFilled", "PendingCancel"],
                },
                "filled_volume": {"$le": vxorder.filled_volume},
            },
            {
                "$set": {
                    "exchange_order_id": vxorder.exchange_order_id,
                    "filled_volume": vxorder.filled_volume,
                    "filled_vwap": vxorder.filled_vwap,
                    "filled_amount": vxorder.filled_amount,
                    "status": vxorder.status.name,
                    "reject_code": vxorder.reject_code,
                    "reject_reason": vxorder.reject_reason,
                    "updated_dt": vxorder.updated_dt,
                    "created_dt": vxorder.created_dt,
                }
            },
        )

    def on_execution_report(self, context, event) -> vxTrade:
        vxtrade = event.data
        with self._db.start_session() as session:
            self._save_execution_report(vxtrade=vxtrade, session=session)
            cur = self._db.positions.find(
                {
                    "account_id": vxtrade.account_id,
                    "symbol": {"$in": ["CNY", vxtrade.symbol]},
                },
                session=session,
            )
            positions = {
                item["symbol"]: (
                    vxPosition(item)
                    if item["symbol"] != "CNY"
                    else vxCashPosition(item)
                )
                for item in cur
            }

            if vxtrade.order_direction == OrderDirection.Buy:
                self._handle_buy_execution_report(positions, vxtrade, session)
            else:
                self._handle_sell_execution_report(positions, vxtrade, session)

    def _save_execution_report(self, vxtrade, session):
        self._db.trades.update_one(
            {"trade_id": vxtrade.trade_id},
            {"$set": vxtrade.message},
            upsert=True,
            session=session,
        )

    def _handle_buy_execution_report(self, positions, vxtrade, session):
        cash_release = vxtrade.volume * vxtrade.price + vxtrade.commission
        cash_position = positions["CNY"]

        cash_position.frozen -= cash_release
        if cash_position.volume_his > cash_release:
            cash_position.volume_his -= cash_release
        else:
            cash_position.volume_today = cash_position.volume - cash_release
            cash_position.volume_his = 0

        symbol_position = positions.get(
            vxtrade.symbol,
            vxPosition(
                account_id=vxtrade.account_id,
                symbol=vxtrade.symbol,
                lasttrade=vxtrade.price,
                allow_t0=vxMarketPreset(vxtrade.symbol).allow_t0,
                security_type=vxMarketPreset(vxtrade.symbol).security_type,
            ),
        )
        symbol_position.volume_today += vxtrade.volume
        symbol_position.cost += cash_release
        symbol_position.lasttrade = vxtrade.price

        self._db.positions.bulk_write(
            [
                UpdateOne(
                    {"account_id": vxtrade.account_id, "symbol": "CNY"},
                    {"$set": cash_position.message},
                    upsert=True,
                ),
                UpdateOne(
                    {"account_id": vxtrade.account_id, "symbol": vxtrade.symbol},
                    {"$set": symbol_position.message},
                    upsert=True,
                ),
            ],
            session=session,
        )
        self._db.accounts.update_one(
            {"account_id": vxtrade.account_id},
            {
                "$inc": {
                    "asset": -vxtrade.commission,
                    "nav": -vxtrade.commission,
                    "balance": -cash_release,
                    "frozen": -cash_release,
                    "marketvalue": vxtrade.volume * vxtrade.price,
                    "fnl": -vxtrade.commission,
                    "today_profit": -vxtrade.commission,
                }
            },
            upsert=True,
            session=session,
        )

    def _handle_sell_execution_report(self, positions, vxtrade, session):
        cash_release = vxtrade.volume * vxtrade.price - vxtrade.commission
        cash_position = positions["CNY"]
        cash_position.volume_today += cash_release

        symbol_position = positions[vxtrade.symbol]
        if symbol_position.volume_his > vxtrade.volume:
            symbol_position.volume_his -= vxtrade.volume
        else:
            symbol_position.volume_today = vxtrade.volume - vxtrade.volume
            symbol_position.volume_his = 0

        symbol_position.lasttrade = vxtrade.price
        symbol_position.frozen -= vxtrade.volume
        symbol_position.cost -= cash_release

        self._db.positions.bulk_write(
            [
                UpdateOne(
                    {"account_id": vxtrade.account_id, "symbol": "CNY"},
                    {"$set": cash_position.message},
                    upsert=True,
                ),
                UpdateOne(
                    {"account_id": vxtrade.account_id, "symbol": vxtrade.symbol},
                    {"$set": symbol_position.message},
                    upsert=True,
                ),
            ],
            session=session,
        )
        self._db.accounts.update_one(
            {"account_id": vxtrade.account_id},
            {
                "$inc": {
                    "asset": -vxtrade.commission,
                    "nav": -vxtrade.commission,
                    "balance": cash_release,
                    "frozen": cash_release,
                    "marketvalue": -vxtrade.volume * vxtrade.price,
                    "fnl": -vxtrade.commission,
                    "today_profit": -vxtrade.commission,
                }
            },
            upsert=True,
            session=session,
        )

    def update_ticks(self):
        cur = self._db.positions.aggreate(
            [
                {"$match": {"symbol": {"$ne": "CNY"}, "volume": {"$gt": 0}}},
                {"$group": {"_id": "$symbol", "lasttrade": {"$max": "$lasttrade"}}},
            ]
        )

        symbols = {item["_id"]: item["lasttrade"] for item in cur}
        vxticks = self._hqfetcher(symbols.keys())
        cmds = [
            UpdateMany({"symbol": symbol}, {"$set": {}})
            for symbol, vxtick in vxticks.items()
            if vxtick.lasttrade != symbols[symbol]
        ]
        for symbol, vxtick in vxticks.items():
            if vxtick.lasttrade == symbols[symbol]:
                continue
            cmds.append()

    def on_settle(self, settle_day):
        """日结"""


if __name__ == "__main__":
    from vxutils.database.mongodb import vxMongoDB
    from vxquant.mdapi.hq.tdx import vxHqAPI

    db = vxMongoDB("mongodb://uat:uat@127.0.0.1:27017/uat", "uat")

    manager = AccountManager(db, None, vxHqAPI())
    # acc = manager.create_account("test", balance=10000000.00, on_error="replace")
    # print(acc)
    print(manager.get_account("test"))
    print(manager.get_positions("test"))
    # order = manager.order_volume("test", "SHSE.600000", 10000, 11.00)
    trade = vxTrade(
        account_id="test",
        symbol="SHSE.600000",
        order_direction="Sell",
        volume=1000,
        price=12.0,
        commission=3,
    )
    manager.on_execution_report(trade)
    print(manager.get_execution_reports("test"))
