"""账户数据库存储方案    """

from contextlib import contextmanager
from typing import Dict, List, Union, Type
from vxquant.model.contants import OrderStatus, OrderDirection
from vxquant.model.typehint import DateTimeType
from vxquant.model.exchange import (
    vxAccountInfo,
    vxOrder,
    vxTrade,
    vxPortfolioInfo,
    vxPosition,
    vxCashPosition,
    vxTransferInfo,
)
from vxutils.database.sqlite import vxSQLiteDB
from vxutils.database.base import vxDataBase
from vxutils.dataorm import vxDataBase as vxDataBase2, vxDBSession
from vxutils import logger, vxtime, to_timestamp, to_timestring, combine_datetime


class vxAccountDB:
    """账户数据库"""

    def __init__(
        self,
        db_uri: str = None,
        database_factory: Type[vxDataBase] = None,
    ) -> None:
        if database_factory is None:
            database_factory = vxSQLiteDB
        self._dbconn: vxDataBase = database_factory.connect(db_uri)

        # 账户信息
        self.create_table("accounts", ["account_id"], vxAccountInfo)
        self.create_table(
            "history_accounts", ["account_id", "settle_date"], vxAccountInfo
        )

        self.create_table(
            "broker_accounts", ["account_id", "settle_date"], vxAccountInfo
        )
        # 账号持仓
        self.create_table(
            "positions",
            ["account_id", "symbol", "position_side"],
            vxPosition,
        )
        self.create_table(
            "history_positions",
            ["account_id", "symbol", "settle_date", "position_side"],
            vxPosition,
        )
        self.create_table(
            "broker_positions",
            ["account_id", "symbol", "settle_date", "position_side"],
            vxPosition,
        )
        # 账户交易委托
        self.create_table("orders", ["order_id"], vxOrder)
        self.create_table("broker_orders", ["exchange_order_id"], vxOrder)
        # 账户成交回报
        self.create_table("trades", ["trade_id"], vxTrade)
        self.create_table("broker_trades", ["trade_id"], vxTrade)
        # 账户转账记录
        self.create_table("transferinfos", ["transfer_id"], vxTransferInfo)
        # 账户组合信息
        self.create_table(
            "portfolios", ["portfolio_id", "settle_date"], vxPortfolioInfo
        )

        self._settle_date = self._get_lastest_settle_date() or vxtime.today("23:59:59")
        logger.info(f"账户数据库初始化完成: {to_timestring(self.settle_date)}")

    def __getattr__(self, attr: str):
        return getattr(self._dbconn, attr)

    @contextmanager
    def start_session(self):
        """启动事务"""
        with self._dbconn.lock, self._dbconn:
            yield self

    def create_account(
        self,
        portfolio_id: str,
        account_id: str,
        init_balance=0.0,
        created_dt: DateTimeType = None,
        if_exists: str = "ignore",
        channel: str = "sim",
    ) -> vxAccountInfo:
        """创建新账户"""
        if_exists = if_exists.lower()
        created_dt = to_timestamp(created_dt or vxtime.today())
        settle_date = self.settle_date

        accountinfo = self.findone("accounts", account_id=account_id)

        if if_exists == "ignore" and accountinfo:
            return accountinfo
        elif if_exists == "delete":
            self.delete("accounts", account_id=account_id)
            self.delete("history_accounts", account_id=account_id)
            self.delete("positions", account_id=account_id)
            self.delete("history_positions", account_id=account_id)
            self.delete("orders", account_id=account_id)
            self.delete("trades", account_id=account_id)
            self.delete("transferinfos", account_id=account_id)
        # elif accountinfo:
        #    raise ValueError(f"账户id ({account_id})已存在，请勿重复创建")

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

        self.save("accounts", accountinfo)
        self.save("positions", cash)
        self.save("transferinfos", transferinfo)

    def _get_lastest_settle_date(self) -> DateTimeType:
        """获取最近的结算日期"""
        return self.max("accounts", "settle_date")

    @property
    def settle_date(self) -> float:
        """当前结算日期

        Returns:
            float -- 当前待结算日期的timestamp格式数据
        """
        return self._settle_date

    @property
    def broker_accountids(self) -> tuple:
        return self.distinct("broker_accounts", "account_id")

    def update_order(self, broker_order: vxOrder) -> None:
        """处理委托状态更新事件"""

    def update_trade(self, broker_trade: vxTrade) -> None:
        """处理成交回报事件"""

    def update_position_lasttrades(
        self, *prices: List[Union[Dict, vxTrade, vxOrder]]
    ) -> None:
        """更新持仓股票最新价格
        prices:[
            {
                "symbol":"SHSE.600000",
                "lasttrade": 10.31  or "price": 10.31,
                "created_dt": 16232132111.12 or "updated_dt": 16232132111.12
                ...
            }
        ]
        """

    def _save_broker_account(self, broker_accountinfo: vxAccountInfo) -> None:
        """保存broker的账户信息

        Arguments:
            broker_accountinfo {vxAccountInfo} -- 从broker获取的accountinfo信息
        """
        yesterday = self.max(
            "accounts",
            "settle_date",
            f"settle_date < {self.settle_date}",
            account_id=broker_accountinfo.account_id,
        )
        db_accountinfo = self.findone(
            "accounts",
            account_id=broker_accountinfo.account_id,
            settle_date=yesterday,
        )
        if not db_accountinfo:
            db_accountinfo = vxAccountInfo(broker_accountinfo.message)
            db_accountinfo.portfolio_id = "default"
            db_accountinfo.fund_shares = broker_accountinfo.nav
            db_accountinfo.asset_yd = broker_accountinfo.asset
            db_accountinfo.nav_yd = broker_accountinfo.nav
            db_accountinfo.fund_nav_yd = broker_accountinfo.fund_nav
            db_accountinfo.settle_date = self.settle_date
            db_accountinfo.channel = "physical"
        else:
            db_accountinfo.debt = broker_accountinfo.debt
            db_accountinfo.balance = broker_accountinfo.balance
            db_accountinfo.frozen = broker_accountinfo.frozen
            db_accountinfo.margin_available = broker_accountinfo.margin_available
            db_accountinfo.marketvalue = broker_accountinfo.marketvalue
            db_accountinfo.fnl = broker_accountinfo.fnl
            db_accountinfo.fund_shares = broker_accountinfo.fund_shares
            db_accountinfo.settle_date = self.settle_date

        self.save("broker_accounts", db_accountinfo)
        return db_accountinfo.account_id

    def _save_broker_positions(
        self,
        broker_account_id: str,
        broker_positions: Dict[str, Union[vxPosition, vxCashPosition]],
    ) -> None:
        self.delete(
            "broker_positions",
            account_id=broker_account_id,
            settle_date=self.settle_date,
        )
        positions = []
        for p in broker_positions.values():
            p.portfolio_id = "default"
            p.settle_date = self.settle_date
            positions.append(p)
        self.save("broker_positions", positions)

    def sync_with_broker(
        self,
        broker_accountinfo: vxAccountInfo,
        broker_positions: Dict,
        broker_orders: Dict = None,
        broker_trades: Dict = None,
        settle_date: DateTimeType = None,
    ) -> None:
        """同步broker的持仓和信息"""
        if settle_date is None:
            settle_date = self.settle_date

        logger.info(f"日结日期：{to_timestring(settle_date,'%Y-%m-%d')}")
        broker_accountinfo.settle_date = settle_date
        account_id = self._save_broker_account(broker_accountinfo)
        logger.info(f"更新broker_accounts: {account_id} 基本信息")

        if broker_positions:
            self._save_broker_positions(account_id, broker_positions)
            logger.info(f"更新broker_positions: {len(broker_positions)}个")

        exchange_order_ids = self.distinct("orders", "exchange_order_id")

        if broker_orders:
            self.save("broker_orders", list(broker_orders.values()))
            for exchange_order_id in exchange_order_ids:
                if exchange_order_id not in broker_orders:
                    continue
                self.update_order(broker_orders[exchange_order_id])
                logger.info(
                    "更新broker_orders:"
                    f" {exchange_order_id} 委托状态{broker_orders[exchange_order_id].status}"
                )

        if broker_trades:
            self.save("broker_trades", list(broker_trades.values()))
            saved_tradeids = self.distinct("trades", "trade_id")

            for broker_trade in broker_trades.values():
                if broker_trade.exchange_order_id not in exchange_order_ids or (
                    broker_trade.trade_id in saved_tradeids
                ):
                    continue
                self.update_trade(broker_trade)
                logger.warning(f"新增成交回报: {broker_trade}")

    def update_after_close(self) -> None:
        """收盘后事件

        1、将未成交的委托单状态更新为已超时
        2、更新账户信息frozens
        3、保存账户信息和持仓信息至历史表


        """

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
            f" {to_timestring(settle_date,'%Y-%m-%d')} 开始..."
        )
        cur = self.find("broker_accounts", settle_date=self.settle_date)
        data = []
        for broker_accountinfo in cur:
            broker_accountinfo.deposit = 0
            broker_accountinfo.withdraw = 0
            broker_accountinfo.asset_yd = broker_accountinfo.asset
            broker_accountinfo.nav_yd = broker_accountinfo.nav
            broker_accountinfo.fund_nav_yd = broker_accountinfo.fund_nav
            broker_accountinfo.settle_date = settle_date
            data.append(broker_accountinfo)

        if data:
            self.save("broker_accounts", data)
            logger.info(f"结转broker_accounts: {len(data)}个")

        cur = self.find("broker_positions", settle_date=self.settle_date)
        data = []
        for broker_position in cur:
            broker_position.volume_his = broker_position.volume
            broker_position.volume_today = 0
            broker_position.settle_date = settle_date
            data.append(broker_position)

        if data:
            self.save("broker_positions", data)
            logger.info(f"结转broker_positions: {len(data)}个")

        cur = self.find("accounts")
        data = []
        for accountinfo in cur:
            accountinfo.deposit = 0
            accountinfo.withdraw = 0
            accountinfo.asset_yd = accountinfo.asset
            accountinfo.nav_yd = accountinfo.nav
            accountinfo.fund_nav_yd = accountinfo.fund_nav
            accountinfo.settle_date = settle_date
            data.append(accountinfo)
        if data:
            self.save("history_accounts", data)
            self.save("accounts", data)
            logger.info(f"结转accounts: {len(data)}个")

        cur = self.find("positions")
        data = []
        for position in cur:
            if position.volume <= 0:
                continue

            position.volume_his = position.volume
            position.volume_today = 0
            position.settle_date = settle_date
            data.append(position)
        if data:
            self.save("positions", data)
            self.save("history_positions", data)
            logger.info(f"结转positions: {len(data)}个")
        self.delete("positions", volume=0)

        self._settle_date = settle_date
        self.update_cash_position_frozens([])
        self.update_symbol_position_frozens([])
        self.update_accountinfos([])
        logger.info(
            f"结转完成,当前结算日: {to_timestring(self.settle_date,'%Y-%m-%d')}"
        )

    def update_cash_position_frozens(self, account_ids: List = None) -> None:
        """更新账户资金冻结"""

    def update_symbol_position_frozens(self, account_ids: List = None) -> None:
        """更新持仓冻结"""

    def update_accountinfos(self, account_ids: List = None) -> None:
        """更新账户信息"""

    def update_order_filleds(self, account_ids: List = None) -> None:
        """更新委托单成交数量"""
