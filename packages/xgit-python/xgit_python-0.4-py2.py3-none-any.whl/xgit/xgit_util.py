#!/usr/bin/python3
# coding=utf-8

from typing import Iterator

from git import Commit
from git.repo import Repo


def author(commit: Commit, no_email: bool = False):
    assert type(commit) is Commit, "{} is not Commit".format(type(commit))
    assert type(no_email) is bool, "{} is not bool".format(type(no_email))
    _author = commit.author
    return _author.name if no_email else "{} <{}>".format(
        _author.name, _author.email)


def committer(commit: Commit, no_email: bool = False):
    assert type(commit) is Commit, "{} is not Commit".format(type(commit))
    assert type(no_email) is bool, "{} is not bool".format(type(no_email))
    _committer = commit.committer
    return _committer.name if no_email else "{} <{}>".format(
        _committer.name, _committer.email)


def committed_datetime(commit: Commit, no_time: bool = True):
    assert type(commit) is Commit, "{} is not Commit".format(type(commit))
    assert type(no_time) is bool, "{} is not bool".format(type(no_time))
    _datetime_format = {
        "date": '%Y-%m-%d',
        "datetime": '%Y-%m-%d %H:%M:%S',
    }["date" if no_time else "datetime"]
    return commit.committed_datetime.strftime(_datetime_format)


class xgit_object():
    '''
    '''

    def __init__(self, repo: str):
        self.__repo = Repo(repo)

    def filter_commits(self, branch: str, path: list,
                       **kwargs) -> Iterator[Commit]:
        return self.__repo.iter_commits(branch, path, **kwargs)

    def short_hexsha(self, commit: Commit):
        assert type(commit) is Commit, "{} is not Commit".format(type(commit))
        return self.__repo.git.rev_parse(commit.hexsha, short=9)
