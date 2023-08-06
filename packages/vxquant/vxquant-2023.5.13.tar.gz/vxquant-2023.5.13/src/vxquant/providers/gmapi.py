"""掘金量化tick行情数据"""

import polars as pl
from tqdm import tqdm
from typing import List, Dict, Union
from vxquant.providers.base import (
    vxHQProvider,
    vxGetDividendProvider,
    vxGetAccountProvider,
    vxGetExecutionReportsProvider,
    vxGetOrdersProvider,
    vxGetPositionsProvider,
    vxOrderBatchProvider,
    vxOrderCancelProvider,
    vxInitProviderContext,
    vxCalendarProvider,
)
from vxquant.model.tools.gmData import (
    gmTickConvter,
    gmAccountinfoConvter,
    gmCashPositionConvter,
    gmOrderConvter,
    gmPositionConvter,
    gmTradeConvter,
)
from vxquant.model.exchange import (
    vxTick,
    vxAccountInfo,
    vxCashPosition,
    vxPosition,
    vxOrder,
    vxTrade,
)
from vxquant.model.instruments import vxInstruments
from vxquant.model.typehint import InstrumentType, DateTimeType
from vxsched import vxContext
from vxutils import to_timestring, vxtime, logger, to_datetime

try:
    from gm import api as gm_api

except ImportError as e:
    raise ImportError("掘金量化库并未安装，请使用pip install gm 安装") from e


class vxInitGMProviderContext(vxInitProviderContext):
    def __init__(self, gm_token: str = "", gm_strategyid: str = ""):
        self._gm_token = gm_token
        self._gm_strategyid = gm_strategyid
        super().__init__()

    def set_context(self, context: vxContext, **kwargs):
        if self._gm_token:
            gm_api.set_token(self._gm_token)

        # context.gmcontext.accountdb = context.accountdb
        context.gm_strategyid = self._gm_strategyid
        context.gm_token = self._gm_token
        return super().set_context(context, **kwargs)


class vxGMHQProvider(vxHQProvider):
    _BATCH_SIZE = 100

    def _hq(self, *symbols: List[InstrumentType]) -> Dict[InstrumentType, vxTick]:
        allticks = []
        for i in range(0, len(symbols), self._BATCH_SIZE):
            gmticks = gm_api.current(symbols=symbols[i : i + self._BATCH_SIZE])
            allticks.extend(gmticks)

        return dict(map(lambda gmtick: gmTickConvter(gmtick, key="symbol"), gmticks))


class vxGMCalendarProvider(vxCalendarProvider):
    def get_trade_dates(self, market: str = "cn") -> List[InstrumentType]:
        return gm_api.get_trading_dates(
            "SHSE", "2005-01-01", f"""{to_timestring(vxtime.now(),"%Y")}-12-31"""
        )


class vxGMGetDividendProvider(vxGetDividendProvider):
    def __call__(
        self,
        symbol: InstrumentType,
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
    ) -> Dict[str, float]:
        start_date = to_timestring(start_date or vxtime.now(), "%Y-%m-%d")
        end_date = to_timestring(end_date or vxtime.now(), "%Y-%m-%d")
        diviends = gm_api.stk_get_dividend(symbol, start_date, end_date)
        for div in diviends:
            created_dt = to_timestring(div.pop("created_at"), "%Y-%m-%d")
            div["trade_date"] = created_dt
        return diviends


class vxGMGetAccountProvider(vxGetAccountProvider):
    def __call__(self, account_id: str = None) -> vxAccountInfo:
        gmcash = self.context["gmcontext"].account(account_id).cash
        return gmAccountinfoConvter(gmcash)


class vxGMGetCreditAccountProvider(vxGetAccountProvider):
    def __call__(self, account_id: str = None) -> vxAccountInfo:
        gmcash = self.context["gmcontext"].account(account_id).cash
        return gmAccountinfoConvter(gmcash)


class vxGMGetPositionsProvider(vxGetPositionsProvider):
    def __call__(
        self, symbol: InstrumentType = None, account_id: str = None
    ) -> Dict[InstrumentType, Union[vxPosition, vxCashPosition]]:
        if symbol and symbol == "CNY":
            gmcash = self.context["gmcontext"].account(account_id).cash
            return {"CNY": gmCashPositionConvter(gmcash)}
        elif symbol:
            gmposition = (
                self.context["gmcontext"].account(account_id).position(symbol, 1)
            )
            return {symbol: gmPositionConvter(gmposition)} if gmposition else None

        gmcash = self.context["gmcontext"].account(account_id).cash
        vxpositions = {"CNY": gmCashPositionConvter(gmcash)}
        gmpositions = self.context["gmcontext"].account().positions()
        vxpositions.update(
            map(
                lambda gmposition: gmPositionConvter(gmposition, key="symbol"),
                gmpositions,
            )
        )

        return vxpositions


class vxGMGetOrdersProvider(vxGetOrdersProvider):
    def __call__(
        self, account_id: str = None, filter_finished: bool = False
    ) -> Dict[str, vxOrder]:
        gmorders = (
            gm_api.get_unfinished_orders() if filter_finished else gm_api.get_orders()
        )
        return dict(
            map(
                lambda gmorder: gmOrderConvter(gmorder, key="exchange_order_id"),
                gmorders,
            )
        )


class vxGMGetExecutionReportsProvider(vxGetExecutionReportsProvider):
    def __call__(
        self, account_id: str = None, order_id: str = None, trade_id: str = None
    ) -> Dict[str, vxTrade]:
        gmtrades = gm_api.get_execution_reports()
        if order_id:
            gmtrades = [
                gmtrade for gmtrade in gmtrades if gmtrade.cl_ord_id == order_id
            ]

        if trade_id:
            gmtrades = [gmtrade for gmtrade in gmtrades if gmtrade.exec_id == trade_id]

        return dict(
            map(lambda gmtrade: gmTradeConvter(gmtrade, key="trade_id"), gmtrades)
        )


class vxGMOrderBatchProvider(vxOrderBatchProvider):
    def __call__(self, *vxorders) -> List[vxOrder]:
        if len(vxorders) == 1 and isinstance(vxorders[0], list):
            vxorders = vxorders[0]

        gmorders = gm_api.order_batch(
            [
                {
                    "symbol": vxorder.symbol,
                    "volume": vxorder.volume,
                    "price": vxorder.price,
                    "side": vxorder.order_direction.value,
                    "order_type": vxorder.order_type.value,
                    "position_effect": vxorder.order_offset.value,
                    "order_business": gm_api.OrderBusiness_NORMAL,
                    "position_src": gm_api.PositionSrc_L1,
                }
                for vxorder in vxorders
            ]
        )
        for vxorder, gmorder in zip(vxorders, gmorders):
            vxorder.exchange_order_id = gmorder.cl_ord_id
            if not vxorder.account_id:
                vxorder.account_id = gmorder.account_id
        return vxorders


class vxGMCreditOrderBatchProvider(vxOrderBatchProvider):
    def __call__(self, *vxorders) -> List[vxOrder]:
        raise NotImplementedError


class vxGMOrderCancelProvider(vxOrderCancelProvider):
    def __call__(self, *vxorders) -> None:
        if len(vxorders) == 1 and isinstance(vxorders[0], list):
            vxorders = vxorders[0]

        wait_cancel_orders = [
            {"cl_ord_id": vxorder.exchange_order_id, "account_id": ""}
            for vxorder in vxorders
            if vxorder.exchange_order_id
        ]
        return gm_api.order_cancel(wait_cancel_orders)
