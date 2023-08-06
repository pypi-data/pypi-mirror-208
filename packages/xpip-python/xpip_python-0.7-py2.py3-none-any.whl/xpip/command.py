#!/usr/bin/python3
# coding=utf-8

from errno import ENOENT
import sys
from typing import List
from typing import Optional

from xarg import argp

from .builder.build import add_cmd as add_cmd_build
from .builder.build import run_cmd as run_cmd_build
from .installer.mirror import add_cmd as add_cmd_mirror
from .installer.mirror import run_cmd as run_cmd_mirror
from .installer.upload import add_cmd as add_cmd_upload
from .installer.upload import run_cmd as run_cmd_upload
from .util import URL_PROG


def add_cmd(_arg: argp):
    _arg.add_opt_on('-d', '--debug', help="show debug information")
    _sub = _arg.add_subparsers(dest="sub")
    add_cmd_build(_sub.add_parser("build", help="build python package"))
    add_cmd_upload(_sub.add_parser("upload", help="upload python package"))
    add_cmd_mirror(_sub.add_parser("mirror", help="pip mirror management"))


def run_command(args) -> int:
    cmds = {
        "build": run_cmd_build,
        "upload": run_cmd_upload,
        "mirror": run_cmd_mirror,
    }
    if not hasattr(args, "sub") or args.sub not in cmds:
        return ENOENT
    return cmds[args.sub](args)


def main(argv: Optional[List[str]] = None) -> int:
    _arg = argp("xpip",
                description="Python package. Build. Install.",
                epilog=f"For more, please visit {URL_PROG}")
    add_cmd(_arg)
    args = _arg.parse_args(argv)

    if hasattr(args, "debug") and args.debug:
        sys.stdout.write(f"{args}\n")
        sys.stdout.flush()

    try:
        return run_command(args)
    except KeyboardInterrupt:
        return 0
    except BaseException as e:
        if hasattr(args, "debug") and args.debug:
            raise e
        sys.stderr.write(f"{e}\n")
        sys.stderr.flush()
        return 10000
