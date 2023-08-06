"""基于sqlite3 的accountdb"""

from sqlite3 import IntegrityError
from typing import Dict, List, Union, Type
from vxquant.model.typehint import DateTimeType
from vxquant.model.contants import OrderOffset, OrderStatus, OrderDirection
from vxquant.model.exchange import vxOrder, vxTrade, vxTick, vxCashPosition, vxPosition
from vxquant.model.preset import vxMarketPreset
from vxquant.accountdb.base import vxAccountDB
from vxquant.exceptions import NoEnoughPosition
from vxutils.database.sqlite import vxSQLiteDB
from vxutils import logger, vxtime, combine_datetime, to_timestring


def _sub_volume(
    position: Union[vxCashPosition, vxPosition],
    volume: Union[float, int],
    allow_negative: bool = False,
) -> Union[vxCashPosition, vxPosition]:
    if volume > position.available and not allow_negative:
        raise NoEnoughPosition(
            f"{position.symbol}可用余额({position.available:,.2f})"
            f" 小于需扣减{volume:,.2f}"
        )

    delta = position.volume_his - volume
    position.volume_his = max(delta, 0)
    position.volume_today += min(delta, 0)
    return position


class vxSQLiteAccountDB(vxAccountDB):
    """账户数据库"""

    def __init__(
        self,
        db_uri: str = None,
        database_factory: Type[vxSQLiteDB] = None,
    ) -> None:
        super().__init__(db_uri, database_factory or vxSQLiteDB)

    def update_position_lasttrades(
        self, *prices: List[Union[Dict, vxTrade, vxTick]]
    ) -> None:
        if len(prices) == 1 and isinstance(prices[0], (list, tuple)):
            prices = prices[0]

        lasttrades = [
            {
                "symbol": price["symbol"],
                "lasttrade": (
                    price["lasttrade"] if "lasttrade" in price else price["price"]
                ),
                "created_dt": price["created_dt"],
            }
            for price in prices
            if (price["lasttrade"] if "lasttrade" in price else price["price"]) > 0
        ]
        self.executemany(
            f"""     
            UPDATE `positions` as t
            SET lasttrade=:lasttrade,
                marketvalue=ROUND(t.volume * :lasttrade,2),
                fnl = ROUND(t.volume * :lasttrade - t.cost,2),
                updated_dt = :created_dt
            WHERE t.symbol = :symbol
            AND t.settle_date={self.settle_date};
            """,
            lasttrades,
        )
        cur = self.execute(f"""
                SELECT  account_id,
                        SUM(marketvalue) as marketvalue,
                        SUM(fnl) as fnl
                FROM positions
                WHERE symbol !='CNY'
                AND settle_date = {self.settle_date}
                GROUP BY account_id;
            """)
        self.executemany(
            f"""
                UPDATE accounts
                SET asset=ROUND(balance+:marketvalue,2),
                    nav=ROUND(balance+:marketvalue - debt,2),
                    marketvalue=ROUND(:marketvalue,2),
                    today_profit = ROUND(balance+:marketvalue-nav_yd-deposit + withdraw,2),
                    fnl=ROUND(:fnl,2),
                    fund_nav=ROUND((balance+:marketvalue - debt)/fund_shares,4)
                WHERE account_id = :account_id
                AND settle_date= {self.settle_date};
            """,
            [dict(item) for item in cur],
        )

    def update_order_filleds(self, account_ids: List[str] = None) -> List[vxOrder]:
        """更新order成交情况

        Arguments:
            account_ids {List[str]} -- 待更新的account_ids
        """
        conditions = [
            """ 
                status in (
                    'PendingNew', 
                    'New',
                    'PartiallyFilled'
                ) 
            """,
            f"""created_dt > {vxtime.today()}""",
            f"""created_dt < {self._settle_date}""",
        ]
        if account_ids:
            conditions.append(f""" account_id in ('{"' , '".join(account_ids)}') """)

        cur = self.execute(f"""
                SELECT  order_id,
                        SUM(volume) as filled_volume, 
                        SUM(volume*price) as filled_amount,
                        SUM(commission) as commission
                FROM trades
                WHERE account_id in ('{"','".join(account_ids)}')
                GROUP BY order_id
            """)
        filleds = {item["order_id"]: item for item in cur}
        if not filleds:
            return

        cur = self.find("orders", f"""order_id in ('{"','".join(filleds.keys())}')""")
        orders = []
        for order in cur:
            order.filled_volume = filleds[order.order_id].filled_volume
            order.filled_amount = (
                (
                    filleds[order.order_id].filled_amount
                    + filleds[order.order_id].commission
                )
                if order.order_direction.name == "Buy"
                else (
                    filleds[order.order_id].filled_amount
                    - filleds[order.order_id].commission
                )
            )
            order.status = (
                "PartiallyFilled" if order.volume > order.filled_volume else "Filled"
            )
            orders.append(order)

        if orders:
            self.save("orders", orders)
        return orders

    def update_cash_position_frozens(self, account_ids: List[str]) -> None:
        """更新cash的frozens"""

        conditions = [
            """
            status in (
                'PendingNew',
                'New',
                'PartiallyFilled'
            )
            """,
        ]
        if account_ids:
            conditions.append(f"""account_id in ('{"','".join(account_ids)}')""")

        cur = self.execute(f"""
            SELECT account_id, 
                   sum((volume-filled_volume)*price*1.003) as frozen 
            FROM orders
            WHERE {' AND '.join(conditions)}
            AND order_direction='Buy'
            GROUP BY account_id ;
            """)
        cash_frozens = {
            account_id: {"account_id": account_id, "frozen": 0}
            for account_id in account_ids
        }
        cash_frozens.update({item["account_id"]: dict(item) for item in cur})
        self.executemany(
            f""" UPDATE positions
                SET frozen=ROUND(:frozen,2) ,
                    available=ROUND(volume-:frozen,2)
                WHERE account_id=:account_id
                AND symbol='CNY' 
                AND settle_date={self.settle_date};
            """,
            list(cash_frozens.values()),
        )
        self.executemany(
            f""" UPDATE accounts
                SET frozen=ROUND(:frozen,2) ,
                    available=ROUND(balance-:frozen,2)
                WHERE account_id=:account_id 
                AND settle_date={self.settle_date};
            """,
            list(cash_frozens.values()),
        )

    def update_symbol_position_frozens(self, account_ids: List[str]) -> None:
        """更新cash的frozens"""
        conditions = [
            """ 
                status in (
                    'PendingNew', 
                    'New',
                    'PartiallyFilled'
                ) 
            """,
            f"""created_dt<{self.settle_date}""",
            f"""created_dt>{vxtime.today()}""",
        ]
        if account_ids:
            conditions.append(f"""account_id in ('{"','".join(account_ids)}')""")

        cur = self.execute(f"""
                SELECT account_id, symbol, sum(volume-filled_volume) as frozen
                FROM orders
                WHERE {' AND '.join(conditions)}
                AND order_direction='OrderDirection.Sell' 
                GROUP BY account_id, symbol ;
            """)
        symbol_frozens = [dict(item) for item in cur]
        self.execute(f"""
                UPDATE positions
                SET frozen=0.0,
                    available=ROUND(volume,2)
                WHERE account_id in ('{"','".join(account_ids)}')
                AND allow_t0 = true
                AND settle_date={self.settle_date}
            """)
        self.execute(f"""
                UPDATE positions
                SET frozen=0.0,
                    available=ROUND(volume_his,2)
                WHERE account_id in ('{"','".join(account_ids)}')
                AND allow_t0 = false
                AND settle_date={self.settle_date}
            """)

        self.executemany(
            f"""
                UPDATE positions
                SET frozen=ROUND(:frozen,2),
                    available=ROUND(volume-:frozen,2)
                WHERE account_id=:account_id
                AND symbol=:symbol
                AND allow_t0 = true
                AND settle_date={self.settle_date}
            """,
            symbol_frozens,
        )
        self.executemany(
            f"""
                UPDATE positions
                SET frozen=ROUND(:frozen,2),
                    available=ROUND(volume_his-:frozen,2)
                WHERE account_id=:account_id
                AND symbol=:symbol
                AND allow_t0 = false
                AND settle_date={self.settle_date}
            """,
            symbol_frozens,
        )

    def update_accountinfos(self, account_ids: List[str]) -> None:
        if not account_ids:
            account_ids = self.distinct(
                "accounts", "account_id", settle_date=self.settle_date
            )
        accountinfos = []
        cur_acc = self.find(
            "accounts",
            f"""account_id in ('{"','".join(account_ids)}')""",
            settle_date=self._settle_date,
        )
        for accountinfo in cur_acc:
            accountinfo.marketvalue = 0
            accountinfo.fnl = 0
            cur = self.find(
                "positions",
                account_id=accountinfo.account_id,
                settle_date=self._settle_date,
            )
            for p in cur:
                if p.symbol == "CNY":
                    accountinfo.balance = p.marketvalue
                    accountinfo.frozen = p.frozen
                else:
                    accountinfo.marketvalue += p.marketvalue
                    accountinfo.fnl += p.fnl
            accountinfos.append(accountinfo)
        self.save("accounts", accountinfos)

    def _handle_buy_position(self, trade: vxTrade) -> None:
        filled_amount = trade.volume * trade.price + trade.commission
        src_position = self.findone(
            "positions",
            account_id=trade.account_id,
            symbol="CNY",
            settle_date=self.settle_date,
        )
        src_position = vxCashPosition(src_position.message)
        dst_position = self.findone(
            "positions",
            account_id=trade.account_id,
            symbol=trade.symbol,
            settle_date=self._settle_date,
        )
        if dst_position is None:
            accountinfo = self.findone(
                "accounts", account_id=trade.account_id, settle_date=self._settle_date
            )
            dst_position = vxPosition(
                portfolio_id=accountinfo.portfolio_id,
                account_id=trade.account_id,
                symbol=trade.symbol,
                security_type=vxMarketPreset(trade.symbol).security_type,
                allow_t0=vxMarketPreset(trade.symbol).allow_t0,
                settle_date=self._settle_date,
            )
        src_position = _sub_volume(src_position, filled_amount)
        dst_position.volume_today += trade.volume
        dst_position.cost += filled_amount
        self.save("positions", src_position, dst_position)

    def _handle_sell_position(self, trade: vxTrade) -> None:
        filled_amount = trade.volume * trade.price - trade.commission
        src_position = self.findone(
            "positions",
            account_id=trade.account_id,
            symbol=trade.symbol,
            settle_date=self.settle_date,
        )

        dst_position = self.findone(
            "positions",
            account_id=trade.account_id,
            symbol="CNY",
            settle_date=self.settle_date,
        )
        dst_position = vxCashPosition(dst_position.message)

        src_position = _sub_volume(src_position, trade.volume)
        src_position.cost -= filled_amount
        dst_position.volume_today += filled_amount
        self.save("positions", src_position, dst_position)

    def update_order(self, broker_order: vxOrder) -> vxOrder:
        """处理委托状态更新事件"""
        if (not broker_order) or (not isinstance(broker_order, vxOrder)):
            logger.error(
                f"on_broker_order_status: 更新参数不正确，broker_order:{broker_order}"
            )
            return

        vxorder = self.findone(
            "orders", exchange_order_id=broker_order.exchange_order_id
        )
        if vxorder is None:
            logger.debug(f"找不到委托单:{broker_order.exchange_order_id}")
            return None

        if vxorder.status not in [
            OrderStatus.PendingNew,
            OrderStatus.New,
            OrderStatus.PartiallyFilled,
        ] and broker_order.status in [
            OrderStatus.PendingNew,
            OrderStatus.New,
            OrderStatus.PartiallyFilled,
        ]:
            logger.warning(
                f"[忽略] 已存储的order已终止: {vxorder.status} //"
                f" {vxorder.filled_volume} ===="
                f" broker_order:{broker_order.status} // {broker_order.filled_volume} "
            )
            return None

        if vxorder.filled_volume > broker_order.filled_volume and broker_order.status:
            logger.warning(
                f"[忽略] 当前order: {vxorder.status} // {vxorder.filled_volume} ===="
                f" broker_order:{broker_order.status} // {broker_order.filled_volume} "
            )
            return None

        vxorder.filled_volume = broker_order.filled_volume
        vxorder.filled_amount = broker_order.filled_amount
        vxorder.reject_code = broker_order.reject_code
        vxorder.reject_reason = broker_order.reject_reason
        vxorder.status = broker_order.status

        self.save("orders", vxorder)
        if vxorder.order_direction == OrderDirection.Buy:
            self.update_cash_position_frozens(account_ids=[vxorder.account_id])
        else:
            self.update_symbol_position_frozens(account_ids=[vxorder.account_id])
        self.update_accountinfos([vxorder.account_id])
        logger.info(f"[更新]委托状态: {vxorder}")
        return vxorder

    def update_trade(self, broker_trade: vxTrade) -> vxTrade:
        """处理成交回报事件"""

        if broker_trade and (not isinstance(broker_trade, vxTrade)):
            logger.error(f"更新参数不正确，broker_trade:{broker_trade} ")
            return None, None

        broker_order = self.findone(
            "orders", exchange_order_id=broker_trade.exchange_order_id
        )

        if broker_order is None:
            logger.debug(
                "收到一个非法委托成交回报exchange_order_id :"
                f" {broker_trade.exchange_order_id}"
            )
            return None, None

        # 更新account_id 和 order_id
        broker_trade.account_id = broker_order.account_id
        broker_trade.order_id = broker_order.order_id

        try:
            self.insert("trades", broker_trade)
            logger.info(
                f"插入成交回报trade_id({broker_trade.trade_id})@order_id({broker_order.order_id})"
                f" volume({broker_trade.volume})"
            )

            vxorders = self.update_order_filleds([broker_trade.account_id])
            vxorder = vxorders[0] if vxorders else None
            if broker_trade.order_direction == OrderDirection.Buy:
                self.update_cash_position_frozens([broker_trade.account_id])
                self._handle_buy_position(trade=broker_trade)
            else:
                self.update_symbol_position_frozens([broker_trade.account_id])
                self._handle_sell_position(trade=broker_trade)

            self.update_position_lasttrades(broker_trade)
            self.update_accountinfos([broker_trade.account_id])
            return broker_trade, vxorder
        except IntegrityError as e:
            logger.error(f"插入数据已存在{broker_trade.trade_id}")
            return None, None

    def update_after_close(self) -> None:
        """收盘后事件

        1、持仓股票最新价格更新
        2、更新账户信息

        """
        self.execute(
            """UPDATE orders 
                SET status='Expired' 
                WHERE  status in ('PendingNew',"New",'PartiallyFilled')
                AND created_dt > ?
                AND created_dt < ?;
            """,
            (vxtime.today(), self.settle_date),
        )
        self.update_cash_position_frozens([])
        self.update_symbol_position_frozens([])
        self.update_accountinfos([])

        accountinfos = list(self.find("accounts"))
        self.save("history_accounts", *accountinfos)
        logger.info(f"保存账户信息: {len(accountinfos)}个")

        positions = list(self.find("positions"))
        self.save("history_positions", *positions)
        logger.info(f"保存持仓信息: {len(positions)}个")

    def update_settle_date(self, settle_date: DateTimeType) -> None:
        """更新结算日期

        Arguments:
            settle_date {DateTimeType} -- 结算日期
        """
        if settle_date is None:
            settle_date = vxtime.today("23:59:59")
        else:
            settle_date = combine_datetime(settle_date, "23:59:59")

        if settle_date <= self.settle_date:
            logger.error(
                f"新设置的结算日期: {to_timestring(settle_date,'%Y-%m-%d')}"
                f"小于当前结算日期({to_timestring(self.settle_date,'%Y-%m-%d')})"
            )
            return

        logger.info(
            f"结算日期：{to_timestring(self.settle_date,'%Y-%m-%d')} ==>"
            f" {to_timestring(settle_date,'%Y-%m-%d')} ..."
        )
        self.delete("positions", volume=0)
        self.execute(
            "UPDATE positions SET volume_today=0, volume_his=volume,  settle_date=? ;",
            (settle_date,),
        )

        self._settle_date = settle_date
        self.update_cash_position_frozens([])
        self.update_symbol_position_frozens([])
        self.update_accountinfos([])
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
