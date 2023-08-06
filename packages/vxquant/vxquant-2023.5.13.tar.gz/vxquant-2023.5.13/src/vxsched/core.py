"""vxsched调度器 """

import contextlib
import importlib
import os
import time

from collections import defaultdict
from multiprocessing.dummy import Lock, Process
from pathlib import Path
from queue import Empty
from typing import Any, List, Callable, Union
from vxsched.context import vxContext
from vxsched.event import vxEvent, vxEventQueue, vxTrigger
from vxutils import logger, vxtime


__all__ = ["vxScheduler", "vxscheduler"]

_default_context = {
    "settings": {},
    "params": {},
    "executor": {
        "class": "concurrent.futures.ThreadPoolExecutor",
        "params": {"thread_name_prefix": "vxSchedThread"},
    },
}


class vxTask:
    """调度任务类"""

    def __init__(
        self, handler: Callable, time_limit: float = 1.0, lock: Lock = None
    ) -> None:
        self._handler = handler
        self.time_limit = time_limit
        self.lock = lock
        self.cost_time = 0

    def __call__(self, context: vxContext, event: vxEvent) -> Any:
        start = time.perf_counter()
        try:
            if self.lock:
                with self.lock:
                    ret = self._handler(context, event)
            else:
                ret = self._handler(context, event)
        except KeyboardInterrupt as user_abort:
            ret = None
            logger.error(f"{self} 用户提前终止...")
            raise KeyboardInterrupt("用户提前终止... ") from user_abort

        except Exception as err:
            ret = err
            logger.error(f"{self} run handler error: {err}", exc_info=True)

        finally:
            self.cost_time = time.perf_counter() - start
            if self.cost_time > self.time_limit:
                logger.warning(
                    f"{self._handler} 运行时间 {self.cost_time*1000:,.2f}ms.  触发消息: {event}"
                )

        return ret

    def __eq__(self, _other: object) -> bool:
        if isinstance(_other, vxTask):
            return self._handler == _other._handler
        else:
            return self._handler == _other

    def __hash__(self) -> int:
        return hash(self._handler)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._handler})"

    __repr__ = __str__


class vxScheduler:
    def __init__(self):
        self._context = None
        self._queue = vxEventQueue()
        self._handlers = defaultdict(set)
        self._active = False
        self._is_initialized = False
        self._worker_threads = []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id-{id(self)})"

    __repr__ = __str__

    @property
    def context(self):
        """上下文环境"""
        return self._context

    def initialize(self, context: vxContext = None) -> None:
        """初始化"""
        if self._is_initialized is True:
            logger.warning("已经初始化，请勿重复初始化")
            return

        self._context = context or self._context or vxContext(_default_context)
        self.submit_event("__init__")
        self.trigger_events()
        self._is_initialized = True
        logger.info(f"{self} 触发初始化完成 ... ")

    def is_alive(self):
        """是否运行中"""
        return self._active

    def trigger_events(self, *trigger_events) -> List:
        """同步触发已到期的消息"""
        if len(trigger_events) == 1 and isinstance(trigger_events[0], list):
            trigger_events = trigger_events[0]

        events = {t_event.id: t_event for t_event in trigger_events}

        with contextlib.suppress(Empty):
            while not self._queue.empty():
                q_event = self._queue.get_nowait()
                if q_event.id not in events or q_event > events[q_event.id]:
                    events[q_event.id] = q_event

        return [
            list(
                map(
                    lambda hdl: self._run_handler(hdl, event),
                    self._handlers[event.type],
                )
            )
            for event in events.values()
        ]

        return

    def submit_event(
        self,
        event: Union[vxEvent, str],
        data: Any = None,
        trigger: vxTrigger = None,
        priority: float = 10,
        **kwargs,
    ) -> vxEvent:
        """提交一个消息"""

        if isinstance(event, str):
            send_event = vxEvent(
                type=event,
                data=data,
                trigger=trigger,
                priority=priority,
                **kwargs,
            )

        elif isinstance(event, vxEvent):
            send_event = event
        else:
            raise ValueError(f"{self} event 类型{type(event)}错误，请检查: {event}")

        logger.debug(f"提交消息: {send_event}")
        self._queue.put_nowait(send_event)

    def handle_reply(self, handler: vxTask, event: vxEvent, ret: Any):
        """处理回复消息"""
        if (
            event.type != "__handle_timerecord__"
            and self._handlers["__handle_timerecord__"]
        ):
            self.submit_event(
                "__handle_timerecord__", (str(handler), event, handler.cost_time)
            )
        if event.reply_to and self._handlers["__handle_reply__"]:
            self.submit_event("__handle_reply__", (event, ret))

    def _run_handler(self, handler: Callable, event: vxEvent) -> None:
        """单独运行一个handler"""

        ret = None
        try:
            ret = handler(self.context, event)
        finally:
            self.handle_reply(handler, event, ret)
        return ret

    def register(
        self,
        event_type: str,
        time_limit: float = 1.0,
        lock: Lock = None,
        handler: Callable = None,
    ) -> Callable:
        """注册一个handler"""

        if not isinstance(handler, vxTask):
            handler = vxTask(handler, time_limit, lock)

        if handler in self._handlers[event_type]:
            return

        self._handlers[event_type].add(handler)
        logger.info(
            f"{self} register event_type:"
            f" '{event_type}' time_limit: {time_limit*1000:,.2f}ms "
            f"handler: {handler} "
        )

    def unregister(self, event_type: str, handler: Callable) -> None:
        """取消注册handler"""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.warning(
                f"{self} unregister event_type: {event_type} handler: {handler}"
            )

    def event_handler(
        self, event_type: str, time_limit: float = 1.0, lock: Lock = None
    ) -> Callable:
        """消息处理函数装饰器"""

        def deco(handler):
            self.register(event_type, time_limit, lock, handler=handler)
            return handler

        return deco

    def run(
        self,
        context: vxContext = None,
    ) -> None:
        if self._is_initialized is False:
            self.initialize(context)
        self._active = True
        self._run()

    def _run(self) -> None:
        """单个线程运行"""
        logger.info(f"{self} worker 开始运行...")
        try:
            while self._active:
                with contextlib.suppress(Empty):
                    event = self._queue.get(timeout=1.0)

                    if self._handlers[event.type]:
                        list(
                            map(
                                lambda hdl: self._run_handler(hdl, event=event),
                                self._handlers[event.type],
                            )
                        )

        finally:
            self._active = False
            logger.info(f"{self} worker 结束运行...")

    def start(
        self,
        context: vxContext = None,
        blocking: bool = False,
        workers: int = 5,
    ) -> None:
        """启动调度器"""
        if self._active:
            logger.info(f"{self} 已经激活运行...")
            return

        if self._is_initialized is False:
            self.initialize(context)

        self._active = True
        self._worker_threads = []
        for i in range(workers):
            t = Process(target=self._run, name=f"vxWorker{i}")
            t.daemon = True
            t.start()
            self._worker_threads.append(t)

        if blocking:
            try:
                while self._active:
                    vxtime.sleep(1.0)
            except Exception:
                self.stop()

        return

    def stop(self) -> None:
        """停止调度器"""
        self._active = False
        for t in self._worker_threads:
            if t.is_alive():
                t.join()

    def server_forever(
        self, config: Union[str, Path] = None, mod: Union[str, Path] = "mod/"
    ):
        if isinstance(config, str):
            config = Path(config)
        elif config is None:
            config = Path("config.json")

        context = (
            vxContext.load_json(config.absolute(), _default_context)
            if config.exists()
            else vxContext(_default_context)
        )
        self.load_modules(mod)
        self.start(context=context, blocking=True)

    def load_modules(self, mod_path: Union[str, Path]) -> Any:
        """加载策略目录"""
        if isinstance(mod_path, Path):
            mod_path = mod_path.absolute()

        if not os.path.exists(mod_path):
            logger.warning(msg=f"{mod_path} is not exists")
            return

        modules = os.listdir(mod_path)
        logger.info(f"loading strategy dir: {mod_path}.")
        logger.info("=" * 80)
        for mod in modules:
            if (not mod.startswith("__")) and mod.endswith(".py"):
                try:
                    loader = importlib.machinery.SourceFileLoader(
                        mod, os.path.join(mod_path, mod)
                    )
                    spec = importlib.util.spec_from_loader(loader.name, loader)
                    strategy_mod = importlib.util.module_from_spec(spec)
                    loader.exec_module(strategy_mod)
                    logger.info(f"Load Module: {strategy_mod} Sucess.")
                    logger.info("+" * 80)
                except Exception as err:
                    logger.error(f"Load Module: {mod} Failed. {err}", exc_info=True)
                    logger.error("-" * 80)


vxscheduler = vxScheduler()

if __name__ == "__main__":
    vxscheduler.server_forever()
