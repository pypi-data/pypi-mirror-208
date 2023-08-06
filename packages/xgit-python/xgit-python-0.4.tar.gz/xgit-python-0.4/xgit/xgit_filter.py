#!/usr/bin/python3
# coding=utf-8

from xarg import argp


def add_cmd_filter_repo(_arg: argp):
    _arg.add_opt('-r',
                 '--repo',
                 type=str,
                 nargs=1,
                 default=['.'],
                 help="specify repo path")


def add_cmd_filter_branch(_arg: argp):
    _arg.add_opt('-b',
                 '--branch',
                 type=str,
                 nargs=1,
                 default=[None],
                 help="specify branch")


def add_cmd_filter_author(_arg: argp):
    _arg.add_opt('--author',
                 type=str,
                 nargs=1,
                 default=[None],
                 help="specify author")


def add_cmd_filter_path(_arg: argp):
    _arg.add_pos("path",
                 nargs=0,
                 type=str,
                 help="Commit with folder or file path")
