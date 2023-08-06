"""配置文件"""
import json
from pathlib import Path
from typing import Union
from vxquant.apis import vxMdAPI, vxTdAPI, vxTeller, vxTellerAPI
from vxsched import vxContext, vxscheduler, vxDailyTrigger
from vxutils import logger, vxWrapper, vxtime


__default_config__ = {
    "custom_context": {},
    "mdapi": {},
    "tdapi": {"channel": "default", "providers": {}},
    "tdapis": {},
    "accountdb": {
        "db_uri": "data/vxquant.db",
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


class vxQuantConfig(vxContext):
    """vxQuant配置文件"""

    _default_config: dict = __default_config__

    def __init__(self, **kwargs):
        super().__init__(self._default_config, **kwargs)

    def load_json(
        self, config_file: Union[str, Path] = "etc/config.json", encoding="utf-8"
    ) -> None:
        """加载配置文件

        Keyword Arguments:
            config_file {Union[str,Path]} -- 配置文件路径 (default: {"etc/config.json"})

        Example:

            {
                "custom_context": {},
                "mdapi": {},
                "tdapi": {"channel": "default", "providers": {}},
                "tdapis": {},
                "accountdb": {
                    "db_uri": "data/vxquant.db",
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
        """
        try:
            with open(config_file, "r", encoding=encoding) as fp:
                kwargs = json.load(fp)
        except OSError:
            kwargs = {}

        self.update(kwargs)
        logger.info(f"通过{config_file}初始化context完成.")

    def create_context(self, **kwargs) -> vxContext:
        """创建context"""

        context = vxContext(**kwargs)

        if "sched" not in kwargs:
            context.sched = vxscheduler
            logger.info("初始化 sched 完成")
            # context.scheduler = vxscheduler
        context.sched.submit_event("day_begin", trigger=vxDailyTrigger("09:10:00"))
        if vxtime.today("09:10:00") < vxtime.now() < vxtime.today("15:00:00"):
            context.sched.submit_event("day_begin")

        for mod_name, mod_config in self.custom_context.items():
            try:
                context[mod_name] = vxWrapper.init_by_config(mod_config.to_dict())
                logger.info(f"初始化{mod_name}: {kwargs[mod_name]}")
            except Exception as e:
                logger.error(f"初始化{mod_name}失败: {e}")

        if "mdapi" in self.keys():
            try:
                context.mdapi = vxMdAPI(**self.mdapi.to_dict())
                context.mdapi.set_context(context)
                vxticks = context.mdapi.current("SHSE.000300")
                logger.info(
                    f"测试实时行情接口: {'SHSE.000300'} --"
                    f" {vxticks['SHSE.000300'].lasttrade:,.2f}"
                )
                # todo: 从配置文件中读取日历，并且更新到vxtime的holidays中
                cal = context.mdapi.calendar(start_date="2005-01-01")
                logger.info(f"获取交易日历: {len(cal)}天")
                logger.warning("初始化mdapi 完成")

            except Exception as e:
                logger.error(f"初始化行情接口失败: {e}")
                context.mdapi = vxMdAPI()
                logger.info(f"使用默认行情接口: {context.mdapi}")

        if "tdapis" in self.keys():
            context.channels = {}

            for channel_name, channel_config in self.tdapis.items():
                try:
                    tdapi = vxTdAPI(**channel_config.to_dict())
                    tdapi.set_context(context)
                    accountinfo = tdapi.get_account()
                    context.channels[channel_name] = tdapi
                    logger.info(
                        f"下单通道 {channel_name}测试交易接口:"
                        f" {accountinfo.account_id} 账户余额: {accountinfo.nav:,.2f}元)"
                    )
                    logger.warning("初始化tdapi 完成")
                except Exception as e:
                    logger.info(f"下单通道 {channel_name} 初始化交易接口失败: {e}", exc_info=True)
                    context.channels.pop(channel_name)

        try:
            if "accountdb" in self.keys():
                db_uri = self.accountdb.db_uri
                context.teller = vxTellerAPI(db_uri=db_uri, mdapi=context.mdapi)
                context.teller.register_scheduler(context.sched)
                for channel_name, tdapi in context.channels.items():
                    context.teller.add_channel(channel_name, tdapi)

                for account_config in self.accountdb.accounts:
                    context.teller.create_account(**account_config.to_dict())
                    logger.info(
                        f"{account_config.portfolio_id} 创建账户:"
                        f" {account_config.account_id} 通道: {account_config.channel}"
                    )
                    context.sched.trigger_events()
                # context.teller.register_scheduler(context.sched)

            else:
                logger.warning("没有交易接口,不创建账户.")
        except Exception as e:
            logger.error(f"初始化账户失败: {e},账户配置: {self.accountdb.accounts}", exc_info=True)

        return context


QCONFIG = vxQuantConfig()


if __name__ == "__main__":
    QCONFIG.load_json()
    context = QCONFIG.create_context()
    print(context.mdapi.current("SHSE.000300"))
    print(context.mdapi.calendar(start_date="2020-01-01", end_date="2023-01-31"))
