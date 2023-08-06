#!/usr/bin/python3
# coding=utf-8

import sys

from xarg import argp

from .xgit_modify_author import add_cmd_modify_author
from .xgit_modify_author import run_cmd_modify_author
from .xgit_modify_committer import add_cmd_modify_committer
from .xgit_modify_committer import run_cmd_modify_committer
from .xgit_summary import add_cmd_summary
from .xgit_summary import run_cmd_summary


def run_sub_command(args):
    if args.debug:
        sys.stdout.write(f"{args}\n")
        sys.stdout.flush()
    {
        "summary": run_cmd_summary,
        "modify-author": run_cmd_modify_author,
        "modify-committer": run_cmd_modify_committer,
    }[args.sub](args)


def main():
    try:
        _arg = argp(
            "xgit",
            description="Git tool based on GitPython",
            epilog=
            "For more, please visit https://github.com/zoumingzhe/xgit-python")
        _arg.add_opt_on('-d', '--debug', help="show debug information")
        _sub = _arg.add_subparsers(dest="sub")
        add_cmd_modify_author(_sub.add_parser("modify-author"))
        add_cmd_modify_committer(_sub.add_parser("modify-committer"))
        add_cmd_summary(_sub.add_parser("summary"))
        args = _arg.parse_args()
        run_sub_command(args)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        sys.stderr.flush()
