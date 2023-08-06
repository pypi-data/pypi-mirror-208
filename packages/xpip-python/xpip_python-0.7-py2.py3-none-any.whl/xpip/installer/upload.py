#!/usr/bin/python3
# coding=utf-8

import sys
from typing import List
from typing import Optional

from twine.commands.check import main as check
from twine.commands.upload import main as upload
from xarg import argp

from ..util import URL_PROG


def add_cmd(_arg: argp):
    _arg.add_opt_on('-d', '--debug', help="show debug information")
    _arg.add_opt_on('--no-check')
    _arg.add_opt_on('--only-check')
    _arg.add_pos('dists',
                 nargs='+',
                 help="The distribution files to upload to the repository.")


def run_cmd(args) -> int:
    if hasattr(args, "debug") and args.debug:
        for f in args.dists:
            sys.stdout.write(f"{f}\n")
        sys.stdout.flush()
    if not args.no_check:
        check(args.dists)
    if not args.only_check:
        upload(args.dists)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    _arg = argp("xpip-upload",
                description="upload python package",
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
