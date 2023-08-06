"""api工具箱"""
import io
import importlib
import pathlib

from typing import Any, Union, Dict
from collections.abc import Mapping
import vxutils

try:
    import simplejson as json
except ImportError:
    import json
__all__ = ["import_tools", "vxAPIWrappers", "vxWrapper"]


def import_tools(mod_path, params=None):
    """导入工具"""

    if params is None:
        params = {}

    cls_or_obj = mod_path
    if isinstance(mod_path, str):
        if mod_path.find(".") > -1:
            class_name = mod_path.split(".")[-1]
            mod_name = ".".join(mod_path.split(".")[:-1])
            mod = importlib.import_module(mod_name)
            cls_or_obj = getattr(mod, class_name)
        else:
            cls_or_obj = importlib.import_module(mod_path)

    return cls_or_obj(**params) if isinstance(cls_or_obj, type) else cls_or_obj


class vxWrapper:
    """根据参数配置，包装任意对象"""

    def __init__(self, mod_path=None, params=None):
        self._provider = None
        self.register(mod_path, params)

    @property
    def provider(self):
        return self._provider

    def register(self, mod_path, params=None):
        provider = import_tools(mod_path, params)
        if provider is None:
            raise ValueError("provider is None")
        self._provider = provider

    def __repr__(self):
        return f"{self.__class__.__name__}(provider={self._provider})"

    __str__ = __repr__

    def __getattr__(self, key):
        if self.__dict__.get("_provider", None) is None:
            raise AttributeError("Warpper({self.__name__}) 未进行初始化工作")
        return getattr(self._provider, key)

    def __call__(self, *args, **kwargs):
        return self._provider(*args, **kwargs)

    def __getstate__(self):
        # if hasattr(self._provider, "__getstate__"):
        #    return {"_provider": self._provider}

        import joblib

        with io.BytesIO() as bfp:
            joblib.dump(self._provider, bfp)
            return {"_privider_pickle": bfp.getvalue()}

    def __setstate__(self, state):
        try:
            import joblib

            with io.BytesIO(state["_privider_pickle"]) as bfp:
                self._provider = joblib.load(bfp)
        except ImportError:
            self._provider = state["_provider"]

    @staticmethod
    def init_by_config(config: dict):
        """根据配置文件初始化对象

        配置文件格式:
        config = {
            'class': 'vxsched.vxEvent',
            'params': {
                "type": "helloworld",
                "data": {
                    'class': 'vxutils.vxtime',
                },
                "trigger": {
                    "class": "vxsched.triggers.vxIntervalTrigger",
                    "params":{
                        "interval": 10
                    }
                }
            }
        }

        """
        # if not isinstance(config, dict):
        #    raise TypeError("config must be a dict")

        if not isinstance(config, Mapping) or "class" not in config:
            return config

        mod_path = config["class"]
        params = {
            k: (
                vxWrapper.init_by_config(v)
                if isinstance(v, Mapping) and "class" in v
                else v
            )
            for k, v in config.get("params", {}).items()
        }

        if isinstance(mod_path, str):
            if mod_path.find(".") > -1:
                class_name = mod_path.split(".")[-1]
                mod_name = ".".join(mod_path.split(".")[:-1])
                mod = importlib.import_module(mod_name)
                cls_or_obj = getattr(mod, class_name)
            else:
                cls_or_obj = importlib.import_module(mod_path)

        return cls_or_obj(**params) if isinstance(cls_or_obj, type) else cls_or_obj


class vxAPIWrappers:
    """api box"""

    __defaults__ = {}

    def __init__(self, **providers: Union[str, Dict]) -> None:
        _providers = dict(**self.__defaults__)
        _providers.update(**providers)
        self.register_providers(**_providers)

    @property
    def context(self):
        return self._context

    def __getitem__(self, key: str):
        return self.__dict__[key]

    def __str__(self):
        message = {
            name: (
                f"module {tool.__name__}(id-{id(tool)})"
                if hasattr(tool, "__name__")
                else f"class {tool.__class__.__name__}(id-{id(tool)})"
            )
            for name, tool in self.__dict__.items()
        }

        return (
            f"< {self.__class__.__name__} (id-{id(self)}) :"
            f" {vxutils.to_json(message)} >"
        )

    def _load_privoder(self, provider: Any, providers: dict = None) -> None:
        """加载当个工具"""
        if providers is None:
            providers = {}

        if isinstance(provider, str) and provider.startswith("@"):
            provider_name = provider[1:]
            if provider_name in self.__dict__:
                return self.__dict__[provider_name]

            elif provider_name in providers:
                return self._load_privoder(providers[provider_name], providers)
            else:
                raise ValueError(f"{provider} is not available. ")

        if not isinstance(provider, dict) or "class" not in provider:
            return provider

        params = provider.get("params", {})
        kwargs = {k: self._load_privoder(v, providers) for k, v in params.items()}
        return import_tools(provider["class"], kwargs)

    def register_providers(self, **providers):
        from vxutils import logger

        for name, provider_config in providers.items():
            if not provider_config:
                continue

            if name in self.__dict__:
                logger.warning(
                    "providers({name}) 已注册为: {self.__dict__[name]},忽略更新"
                )
                continue

            try:
                provider = self._load_privoder(provider_config, providers)
                self.__dict__[name] = provider
                logger.info(f"注册{name}接口成功 ")
            except Exception as err:
                logger.error(
                    f"加载provider: {name}({provider_config})出错: {err}", exc_info=True
                )


if __name__ == "__main__":
    from vxutils import vxtime

    providers = {
        "vxtime": {
            "class": "vxutils.vxtime",
        },
        "cache": {"class": "vxutils.vxLRUCache", "params": {"size_limit": 10000}},
        "event": {
            "class": "vxsched.vxEvent",
            "params": {
                "type": "@context",
                "data": {
                    "class": "vxutils.vxtime",
                },
                "trigger": {
                    "class": "vxsched.triggers.vxIntervalTrigger",
                    "params": {
                        "interval": 10,
                        "start_dt": vxtime.now() + 10,
                        "skip_holiday": True,
                    },
                },
                "channel": float("inf"),
            },
        },
        "context": "this_is_context",
    }
    a = vxAPIWrappers(**providers)
    print(a)
