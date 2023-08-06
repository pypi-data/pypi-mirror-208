#!/usr/bin/python3
# coding=utf-8

from errno import ENOENT
import os
import sys
from typing import List
from typing import Optional

from xarg import argp

from ..util import URL_PROG
from .setup import add_cmd as add_cmd_setup
from .setup import run_cmd as run_cmd_setup


def add_cmd(_arg: argp):
    _arg.add_opt_on('-d', '--debug', help="show debug information")
    _arg.add_opt('--path',
                 nargs=1,
                 type=str,
                 const='.',
                 default='.',
                 help="specify root path")
    _sub = _arg.add_subparsers(dest="sub_build")
    add_cmd_setup(_sub.add_parser("setup", help="build based on setuptools"))


def run_cmd(args) -> int:
    cmds = {
        "setup": run_cmd_setup,
    }
    if not hasattr(args, "sub_build") or args.sub_build not in cmds:
        return ENOENT
    args.root = os.path.realpath(args.path)
    if hasattr(args, "debug") and args.debug:
        sys.stdout.write(f"root:{args.root}\n")
        sys.stdout.flush()
    return cmds[args.sub_build](args)


def main(argv: Optional[List[str]] = None) -> int:
    _arg = argp("xpip-build",
                description="build python package",
                epilog=f"For more, please visit {URL_PROG}")
    add_cmd(_arg)
    args = _arg.parse_args(argv)

    if hasattr(args, "debug") and args.debug:
        sys.stdout.write(f"{args}\n")
        sys.stdout.flush()

    try:
        return run_cmd(args)
    except KeyboardInterrupt:
        return 0
    except BaseException as e:
        if hasattr(args, "debug") and args.debug:
            raise e
        sys.stderr.write(f"{e}\n")
        sys.stderr.flush()
        return 10000
