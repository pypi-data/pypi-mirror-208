"""CLI命令"""
import json
import textwrap
import argparse
from pathlib import Path
from typing import Dict, Callable, Any
from vxsched import vxscheduler
from vxutils import logger


class vxCommand:
    cmds: Dict[str, "vxCommand"] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        vxCommand.cmds[self.name] = self

    def set_parser(self, sub_parser: argparse.ArgumentParser) -> None:
        self.parser = sub_parser.add_parser(
            self.name,
            prog=f"vxquant {self.name}",
            usage=f"vxquant {self.name} [options] ",
            description=textwrap.dedent(self.__doc__ or ""),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            help=f"""vxquant {self.name} [options] """,
            add_help=False,
        )
        self.parser.add_argument("-h", "--help", help="显示当前帮助信息", action="help")
        self.add_options()

    def add_options(self) -> None:
        pass

    def __call__(self, args) -> Any:
        pass


class vxInitDirCommand(vxCommand):
    def __call__(self, args) -> Any:
        root = Path(".")
        for dir_name in ["etc", "mod", "log", "data"]:
            root.joinpath(dir_name).mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录完成: {root.joinpath(dir_name).absolute()}")


class vxQuantCommand(vxCommand):
    def __init__(
        self,
        name: str,
        run_func: Callable,
        example_config: Dict,
    ):
        self.run = run_func
        self.__doc__ = self.run.__doc__
        self.example_config = example_config
        super().__init__(name=name)

    def add_options(self) -> None:
        self.parser.add_argument(
            "-g", "--generate-config", help="生成默认配置文件", default=None, type=str
        )
        self.parser.add_argument(
            "-c", "--config", help="配置文件", default="etc/config.json", type=str
        )
        self.parser.add_argument(
            "-m", "--mod", help="策略模块地方", default="./mod/", type=str
        )
        self.parser.add_argument(
            "-d", "--debug", help="调试模式", default=False, action="store_true"
        )

    def __call__(self, args):
        if args.generate_config:
            with open(args.generate_config, "w") as fp:
                json.dump(self.example_config, fp, indent=4)
            return

        if args.debug:
            logger.setLevel("DEBUG")

        self.run(config=args.config, mod=args.mod)


vxInitDirCommand("init")
vxQuantCommand("sched", vxscheduler.server_forever, {})
