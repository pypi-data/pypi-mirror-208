"""miniQMT agent"""

import sys
import os
import subprocess
from pathlib import Path
from vxquant.config import QCONFIG
from vxquant.apis import vxMdAPI, vxTdAPI, vxTeller
from vxquant.cli.base import vxQuantCommand
from vxsched import vxscheduler, vxDailyTrigger, vxContext
from vxutils import vxtime, logger, vxWrapper, to_timestring

try:
    from xtquant import xtdata
    from xtquant.xttype import StockAccount
    from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
    from xtquant import xtconstant
except ImportError as e:
    raise ImportError("xtquant未安装，请将QMT安装目录")

_qmtagent_config = {
    "custom_context": {},
    "mdapi": {
        "current": {
            "class": "vxquant.providers.miniqmt.vxMiniQMTHQProvider",
            "params": {},
        },
        "calendar": {
            "class": "vxquant.providers.miniqmt.vxMiniQMTCalendarProvider",
            "params": {},
        },
    },
    "tdapis": {
        "default": {
            "init": {
                "class": "vxquant.providers.miniqmt.vxInitMinitQMTProviderContext",
                "params": {
                    "miniqmt_path": "",
                },
            },
            "current": {
                "class": "vxquant.providers.miniqmt.vxMiniQMTHQProvider",
                "params": {},
            },
            "get_account": {
                "class": "vxquant.providers.miniqmt.vxMiniQMTGetAccountProvider",
                "params": {},
            },
            "get_positions": {
                "class": "vxquant.providers.miniqmt.vxMiniQMTGetPositionsProvider",
                "params": {},
            },
            "get_orders": {
                "class": "vxquant.providers.miniqmt.vxMiniQMTGetOrdersProvider",
                "params": {},
            },
            "get_execution_reports": {
                "class": (
                    "vxquant.providers.miniqmt.vxMiniQMTGetExecutionReportsProvider"
                ),
                "params": {},
            },
            "order_batch": {
                "class": "vxquant.providers.miniqmt.vxMiniQMTOrderBatchProvider",
                "params": {},
            },
            "order_cancel": {
                "class": "vxquant.providers.miniqmt.vxMiniQMTOrderCancelProvider",
                "params": {},
            },
        }
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
}


def run_miniqmtagent(config: str, mod: str) -> None:
    ENV = os.environ
    ENV["QMTCONFIGFILE"] = config
    ENV["STRATEGYMOD"] = mod

    while True:
        try:
            if vxtime.now() < vxtime.today("09:10:00"):
                with vxtime.timeit("等待今天开盘..."):
                    vxtime.sleep(vxtime.today("09:10:00") - vxtime.now())
            elif vxtime.now() < vxtime.today("15:00:00"):
                subprocess.run([sys.executable, "-m", "vxquant.cli.qmtagent"], env=ENV)
            else:
                with vxtime.timeit("等待明天开盘..."):
                    vxtime.sleep(vxtime.today("09:10:00") - vxtime.now() + 24 * 60 * 60)

        finally:
            with vxtime.timeit("程序退出，等待5秒..."):
                vxtime.sleep(5)


def run_debug_miniagent(config: str, mod: str) -> None:
    ENV = os.environ
    ENV["QMTCONFIGFILE"] = config
    ENV["STRATEGYMOD"] = mod

    while True:
        try:
            # subprocess.run([sys.executable, "-m", "vxquant.cli.qmtagent"], env=ENV)
            main(config, mod)
        finally:
            with vxtime.timeit("程序退出，等待5秒..."):
                vxtime.sleep(5)


def main(config: str, mod_path: str) -> None:
    """主函数"""
    QCONFIG.load_json(config)
    context = QCONFIG.create_context()

    if mod_path and Path(mod_path).is_dir():
        vxscheduler.load_modules(mod_path)
    else:
        logger.info(f"策略模块目录 {mod_path} 不存在")

    logger.info("=" * 80)
    logger.info(f"{' 初始化完成 ':=^80}")
    logger.info("=" * 80)

    vxscheduler.run(context=context)


vxQuantCommand("qmt", run_miniqmtagent, _qmtagent_config)
vxQuantCommand("qmtdebug", run_debug_miniagent, _qmtagent_config)

if __name__ == "__main__":
    config = os.environ.get("QMTCONFIGFILE", "./etc/config.json")
    mod_path = os.environ.get("STRATEGYMOD", "./mod/")
    main(config, mod_path)
