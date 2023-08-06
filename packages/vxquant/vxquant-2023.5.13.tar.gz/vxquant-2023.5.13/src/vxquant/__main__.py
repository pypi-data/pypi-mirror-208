"""配置文件"""
import sys
import textwrap
import argparse
from vxquant.cli import vxCommand


desc = """
vxquant是一个量化金融框架Python包，用于为个人提供实盘交易以及量化研究支持，使用户更加专注于交易策略的编写。
框架具有以下特点：
1. 支持多账户体系运行
2. 支持掘金量化实盘以及模拟盘
3. 支持miniQMT实盘以及模拟盘
本命令为vxquant框架命令行接口，本接口可方便执行以下命令.
"""


def main(args=None) -> int:
    if args is None:
        args = sys.argv[1:]
    if len(args) == 0:
        args = ["-h"]

    parser = argparse.ArgumentParser(
        prog="vxquant",
        usage="vxquant <command> [options]",
        description=textwrap.dedent(desc),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    parser.add_argument(
        "-v",
        "--version",
        help="显示vxquant版本",
        action="version",
        version="2023.5.12",
    )
    parser.add_argument("-h", "--help", help="显示当前帮助信息", action="help")
    sub_parser = parser.add_subparsers(metavar="命令列表", dest="cmd")

    for command in vxCommand.cmds.values():
        command.set_parser(sub_parser)

    args = parser.parse_args(args)
    command = vxCommand.cmds[args.cmd]
    command(args)


if __name__ == "__main__":
    main()
