#!/usr/bin/python3
# coding=utf-8

import glob
import os
import shutil
import sys
from typing import List
from typing import Optional

import setuptools
from xarg import argp

from ..util import URL_PROG


def run(args) -> int:
    if hasattr(args, "setup_py") and isinstance(args.setup_py, str):
        exec(args.setup_py)
    else:
        setuptools.setup()
    return 0


def check(args) -> int:
    sys.argv = 'setup.py check'.split()
    return run(args)


def sdist(args) -> int:
    sys.argv = 'setup.py sdist'.split()
    return run(args)


def bdist_wheel(args) -> int:
    sys.argv = 'setup.py bdist_wheel --universal'.split()
    return run(args)


def install(args) -> int:
    # TODO: uninstall
    sys.argv = 'setup.py install'.split()
    return run(args)


def clean(args) -> int:
    to_delete = []
    to_delete.extend(glob.glob("build"))
    to_delete.extend(glob.glob("dist"))
    to_delete.extend(glob.glob("*.egg-info"))

    # delete build/dist/*.egg-info directorys
    for dir in to_delete:
        if os.path.isdir(dir):
            if hasattr(args, "debug") and args.debug:
                sys.stdout.write(f"delete directory:{dir}\n")
                sys.stdout.flush()
            shutil.rmtree(dir)

    return 0


def add_cmd(_arg: argp):
    _arg.add_opt_on('--clean', help="clean build files")
    _arg.add_opt_on('--check', help="build check")
    _arg.add_opt_on('--sdist', help="build sdist")
    _arg.add_opt_on('--bdist_wheel', help="build bdist_wheel")
    _arg.add_opt_on('--all', help="build all")
    _arg.add_opt_on('--install', help="install build package")


def run_cmd(args) -> int:
    os.chdir(args.root)

    if os.path.isfile('setup.py'):
        with open('setup.py', 'r') as f:
            args.setup_py = f.read()
            if hasattr(args, "debug") and args.debug:
                sys.stdout.write(f"setup.py:\n{args.setup_py}\n")
                sys.stdout.flush()

    if args.clean:
        clean(args)

    if args.all or args.check:
        check(args)

    if args.all or args.sdist:
        sdist(args)

    if args.all or args.bdist_wheel:
        bdist_wheel(args)

    if args.install:
        install(args)

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    _arg = argp("xpip-build-setup",
                description="build python package based on setuptools",
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
