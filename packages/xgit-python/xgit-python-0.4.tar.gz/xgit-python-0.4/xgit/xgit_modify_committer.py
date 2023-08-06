#!/usr/bin/python3
# coding=utf-8

import sys

from git.cmd import Git
from xarg import argp

from .xgit_filter import add_cmd_filter_repo


def add_cmd_modify_committer(_arg: argp):
    add_cmd_filter_repo(_arg)
    _arg.add_pos('name', nargs=1, help="specify new committer name")
    _arg.add_pos('email', nargs=1, help="specify new committer email")
    _arg.add_pos('old',
                 nargs=-1,
                 help="specify any old committer name or email")


def run_cmd_modify_committer(args):
    _name = args.name[0]
    _email = args.email[0]
    _old = " ".join(['"{}"'.format(i) for i in args.old])
    _ret = Git(args.repo[0]).execute(["git", "gc"])
    sys.stdout.write(f"{_ret}\n")
    sys.stdout.flush()
    _ctx = """for old_name_or_email in {2}; do
 if [ "$GIT_COMMITTER_NAME" = "$old_name_or_email" ]; then
   export GIT_COMMITTER_NAME="{0}";
   export GIT_COMMITTER_EMAIL="{1}";
 elif [ "$GIT_COMMITTER_EMAIL" = "$old_name_or_email" ]; then
  export GIT_COMMITTER_NAME="{0}";
  export GIT_COMMITTER_EMAIL="{1}";
 fi done""".format(_name, _email, _old).replace("\n", "")
    _cmd = [
        "git",
        "filter-branch",
        "--env-filter",
        _ctx,
        "--tag-name-filter",
        "cat",
        "--force",
        "--",
        "--branches",
        "--tags",
    ]
    _ret = Git(args.repo[0]).execute(_cmd)
    sys.stdout.write(f"{_ret}\n")
    sys.stdout.flush()


def main():
    try:
        _arg = argp("xgit-modify-committer", description="modify committer")
        add_cmd_modify_committer(_arg)
        args = _arg.parse_args()
        run_cmd_modify_committer(args)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        sys.stderr.flush()
