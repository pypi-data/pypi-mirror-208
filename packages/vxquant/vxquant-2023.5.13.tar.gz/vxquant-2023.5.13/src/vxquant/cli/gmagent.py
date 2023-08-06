"""掘金量化命令"""

import os
import subprocess
import sys

from pathlib import Path
from typing import Union

from vxquant.cli.base import vxQuantCommand
from vxquant.config import QCONFIG
from vxquant.model.exchange import TradeStatus
from vxquant.model.preset import vxMarketPreset
from vxquant.model.tools.gmData import gmOrderConvter
from vxquant.model.tools.gmData import gmTradeConvter
from vxsched import vxscheduler
from vxutils import logger
from vxutils import to_timestamp
from vxutils import vxtime


try:
    from gm import api as gm_api

    # from vxquant.tdapi.gm import gmTdAPI
except ImportError:
    gm_api = None
    gmTdAPI = None


_gmagent_config = {
    "custom_context": {},
    "mdapi": {
        "current": {
            "class": "vxquant.providers.gmapi.vxGMHQProvider",
            "params": {},
        },
        "calendar": {
            "class": "vxquant.providers.gmapi.vxGMCalendarProvider",
            "params": {},
        },
        "get_dividend": {
            "class": "vxquant.providers.gmapi.vxGetDividendProvider",
            "params": {},
        },
    },
    "gm_strategyid": "",
    "gm_token": "",
    "tdapis": {
        "default": {
            "init": {
                "class": "vxquant.providers.gmapi.vxInitGMProviderContext",
                "params": {},
            },
            "current": {
                "class": "vxquant.providers.gmapi.vxGMHQProvider",
                "params": {},
            },
            "get_account": {
                "class": "vxquant.providers.gmapi.vxGMGetAccountProvider",
                "params": {},
            },
            "get_positions": {
                "class": "vxquant.providers.gmapi.vxGMGetPositionsProvider",
                "params": {},
            },
            "get_orders": {
                "class": "vxquant.providers.gmapi.vxGMGetOrdersProvider",
                "params": {},
            },
            "get_execution_reports": {
                "class": "vxquant.providers.gmapi.vxGMGetExecutionReportsProvider",
                "params": {},
            },
            "order_batch": {
                "class": "vxquant.providers.gmapi.vxGMOrderBatchProvider",
                "params": {},
            },
            "order_cancel": {
                "class": "vxquant.providers.gmapi.vxGMOrderCancelProvider",
                "params": {},
            },
        },
    },
    "accountdb": {
        "db_uri": "sqlite:///data/vxquant.db",
        "accounts": [
            {
                "portfolio_id": "default",
                "account_id": "default",
                "init_balance": 1_000_000.00,
                "if_exists": "ignore",
                "channel": "default",
            },
        ],
    },
    "notify": {},
    "preset_events": {
        "before_trade": "09:15:00",
        "on_trade": "09:30:00",
        "noon_break_start": "11:30:00",
        "noon_break_end": "13:00:00",
        "before_close": "14:45:00",
        "on_close": "14:55:00",
        "after_close": "15:30:00",
        "on_settle": "16:30:00",
    },
    "tick_symbols": [
        "SHSE.000001",
        "SHSE.000688",
        "SHSE.511880",
        "SHSE.510300",
        "SHSE.511990",
        "SHSE.511660",
        "SHSE.204001",
        "SZSE.399001",
        "SZSE.399673",
        "SZSE.159001",
        "SZSE.159919",
        "SZSE.159915",
        "SZSE.159937",
        "SZSE.131810",
    ],
}


def init(gmcontext):
    """
    掘金量化策略中必须有init方法,且策略会首先运行init定义的内容
    """

    # 设置 时间函数
    vxtime.set_timefunc(lambda: to_timestamp(gmcontext.now))
    logger.info("=" * 80)
    logger.info(f"{' 初始化开始 ':=^80}")
    logger.info("=" * 80)

    configfile = os.environ.get("GMCONFIGFILE", "gmagent.json")
    mod_path = os.environ.get("STRATEGYMOD", "mod/")

    QCONFIG.load_json(configfile)
    context = QCONFIG.create_context(gmcontext=gmcontext)

    gm_api.subscribe(QCONFIG.tick_symbols, "tick")
    logger.info(f"订阅on_tick数据: {QCONFIG.tick_symbols}")

    gm_api.schedule(quit_simtrade, "1d", "16:40:00")
    logger.info("提交退出事件: 16:40:00")

    if mod_path and Path(mod_path).is_dir():
        vxscheduler.load_modules(mod_path)
    else:
        logger.info(f"策略模块目录 {mod_path} 不存在")

    vxscheduler.initialize(context=context)

    logger.info("=" * 80)
    logger.info(f"{' 初始化完成 ':=^80}")
    logger.info("=" * 80)


def on_tick(gmcontext, gmtick=None):
    """on tick"""
    vxscheduler.trigger_events()


def on_order_status(gmcontext, order):
    """
    委托状态更新事件. 参数order为委托信息
    响应委托状态更新事情，下单后及委托状态更新时被触发
    3.0.113 后增加.
    与on_order_status 具有等同含义, 在二者都被定义时(当前函数返回类型为类，速度更快，推介使用),
    只会调用 on_order_status_v2
    """
    logger.debug(f"gmorder: {order}")
    broker_order = gmOrderConvter(order)
    logger.debug(f"收到券商委托更新: {broker_order}")
    vxscheduler.submit_event("on_broker_order_status", data=broker_order)
    vxscheduler.trigger_events()


def on_execution_report(gmcontext, execrpt):
    """
    委托执行回报事件. 参数 execrpt 为执行回报信息
    响应委托被执行事件，委托成交后被触发
    3.0.113 后增加
    已 on_execution_report 具有等同含义, 在二者都被定义时(当前函数返回类型为类，速度更快，推介使用), 只会调用 on_execution_report_v2
    """

    logger.debug(f"gmtrade: {execrpt}")
    broker_trade = gmTradeConvter(execrpt)
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
                        _preset.commission_coeff_peramount + _preset.tax_coeff_peramount
                    )
                )
            ),
            0.5,
        )

    if broker_trade.status != TradeStatus.Trade:
        logger.warning(f"收到非成交的回报信息: {broker_trade}")
        return

    logger.debug(f"收到券商成交回报信息: {broker_trade}")
    vxscheduler.submit_event("on_broker_execution_report", data=broker_trade)
    vxscheduler.trigger_events()


def quit_simtrade(gmcontext):
    """退出时调用"""
    configfile = os.environ.get("GMCONFIGFILE", "gmagent.json")
    vxscheduler.submit_event("on_exit", data=configfile)
    vxscheduler.trigger_events()
    gm_api.stop()


def run_gmagent(config: Union[str, Path], mod: Union[str, Path]) -> None:
    QCONFIG.load_json(config)
    ENV = os.environ
    ENV["gm_strategyid"] = QCONFIG.gm_strategyid
    ENV["gm_token"] = QCONFIG.gm_token
    ENV["GMCONFIGFILE"] = config
    ENV["STRATEGYMOD"] = mod

    while True:
        try:
            if vxtime.now() < vxtime.today("09:10:00"):
                with vxtime.timeit("等待今天开盘..."):
                    vxtime.sleep(vxtime.today("09:10:00") - vxtime.now())
            elif vxtime.now() < vxtime.today("15:00:00"):
                subprocess.run([sys.executable, "-m", "vxquant.cli.gmagent"], env=ENV)
            else:
                with vxtime.timeit("等待明天开盘..."):
                    vxtime.sleep(vxtime.today("09:10:00") - vxtime.now() + 24 * 60 * 60)

        finally:
            with vxtime.timeit("程序退出，等待5秒..."):
                vxtime.sleep(5)


def run_debug_gmagent(config: Union[str, Path], mod: Union[str, Path]) -> None:
    logger.info(f"调试模式启动:{config},{mod}")
    QCONFIG.load_json(config)
    ENV = os.environ
    ENV["gm_strategyid"] = QCONFIG.gm_strategyid
    ENV["gm_token"] = QCONFIG.gm_token
    ENV["GMCONFIGFILE"] = config
    ENV["STRATEGYMOD"] = mod

    while True:
        try:
            subprocess.run([sys.executable, "-m", "vxquant.cli.gmagent"], env=ENV)
        finally:
            with vxtime.timeit("程序退出，等待5秒..."):
                vxtime.sleep(5)


vxQuantCommand("gm", run_gmagent, _gmagent_config)
vxQuantCommand("gmdebug", run_debug_gmagent, _gmagent_config)

if __name__ == "__main__":
    gm_strategyid = os.environ.get("gm_strategyid", None)
    gm_token = os.environ.get("gm_token", None)

    assert gm_token is not None
    assert gm_strategyid is not None
    logger.info(f"策略ID: {gm_strategyid} token: {gm_token}")

    try:
        gm_api.run(
            strategy_id=gm_strategyid,
            filename="vxquant.cli.gmagent",
            mode=gm_api.MODE_LIVE,
            token=gm_token,
        )
    except Exception as e:
        logger.error(f"运行错误: {e}")
    finally:
        logger.warning("========== 运行结束 ==========")
        vxtime.sleep(5)
