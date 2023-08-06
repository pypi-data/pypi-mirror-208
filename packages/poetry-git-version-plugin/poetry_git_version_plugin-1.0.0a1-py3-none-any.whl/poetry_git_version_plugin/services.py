import re
from pathlib import Path
from typing import List, Optional

import git
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from git.objects import Commit
from packaging.version import VERSION_PATTERN
from poetry.core.constraints.version import Version
from poetry.poetry import Poetry

from poetry_git_version_plugin import config
from poetry_git_version_plugin.exceptions import PluginException

VERSION_REGEX_COMPILE = re.compile(r'^\s*' + VERSION_PATTERN + r'\s*$', re.VERBOSE | re.IGNORECASE)
VERSION_CANON_REGEX_COMPILE = re.compile(
    r'^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$'
)


def validate_version(version_string: str):
    """Проверка версии на PEP 440

    Args:
        version_string (str): Версия

    Raises:
        PluginException: Версия не соответствует стандарту

    """

    if VERSION_REGEX_COMPILE.search(version_string) is None:
        return 1

    if VERSION_CANON_REGEX_COMPILE.search(version_string) is None:
        return 2

    return 0


class GitService(object):
    repo: git.Repo

    def __init__(self) -> None:
        path = Path.cwd()
        self.repo = git.Repo(path, search_parent_directories=True)

    @property
    def commits(self) -> List[Commit]:
        return list(self.repo.iter_commits())

    @property
    def current_commit(self) -> Commit:
        return self.repo.head.commit

    @property
    def tags(self) -> List[git.Tag]:
        return list(self.repo.tags)[::-1]

    def get_current_tag(self) -> Optional[git.Tag]:
        """Получение тега нынешнего коммита"""

        tags = list(self.repo.tags)[::-1]

        for tag in tags:
            if tag.commit == self.repo.head.commit:
                return tag

        return None

    def get_last_tag(self) -> Optional[git.Tag]:
        """Получение последнего тега нынешней ветки"""

        commits = set(self.commits)
        tags = self.tags

        for tag in tags:
            if tag.commit in commits:
                return tag

        return None

    def get_current_short_rev(self) -> str:
        return self.current_commit.name_rev[:7]

    def get_distance(self, from_commit: Commit, to_commit: Commit) -> int:
        return len(list(self.repo.iter_commits(f'{from_commit}..{to_commit}')))


class VersionService(object):
    io: IO
    plugin_config: config.PluginConfig

    git_service: GitService

    def __init__(self, io: IO, plugin_config: config.PluginConfig) -> None:
        self.io = io
        self.plugin_config = plugin_config

        self.git_service = GitService()

    def construct_alpha_version(self, version: str, distance: str, commit_hash: str):
        return self.plugin_config.alpha_version_format.format(
            version=version,
            distance=distance,
            commit_hash=commit_hash,
        )

    def get_main_version(self) -> Optional[str]:
        tag = self.git_service.get_current_tag()
        return tag.name if tag is not None else None

    def get_alpha_version(self):
        tag = self.git_service.get_last_tag()

        version = '0.0.0'
        distance_from_commit = self.git_service.commits[-1]

        if tag is not None:
            distance_from_commit = tag.commit
            version = str(tag)

        distance = self.git_service.get_distance(distance_from_commit, self.git_service.current_commit)
        commit_hash = self.git_service.get_current_short_rev()

        return self.construct_alpha_version(version, distance, commit_hash)

    def __get_version(self) -> str:
        self.io.write(f'<b>{config.PLUGIN_NAME}</b>: Find git <b>current tag</b>... ', verbosity=Verbosity.VERBOSE)

        version = self.get_main_version()

        if version is not None:
            self.io.write_line(f'success, setting dynamic version to: {version}', Verbosity.VERBOSE)
            return version

        self.io.write_line('fail', Verbosity.VERBOSE)

        if not self.plugin_config.make_alpha_version:
            raise PluginException('No Git version found, not extracting dynamic version')

        self.io.write(f'<b>{config.PLUGIN_NAME}</b>: Make <b>alpha version</b>... ', verbosity=Verbosity.VERBOSE)

        version = self.get_alpha_version()

        self.io.write_line(f'success, setting dynamic version to: {version}', Verbosity.VERBOSE)

        return version

    def validate_version(self, version: str):
        is_valid = validate_version(version)

        if is_valid == 0:
            return version

        if is_valid == 1:
            self.io.write_line(f'Invalid PEP 440 version: "{version}"', Verbosity.VERBOSE)

            if not self.plugin_config.ignore_pep440:
                raise PluginException(f'Invalid PEP 440 version: "{version}"')

        if is_valid == 2:
            self.io.write_line(f'Invalid public PEP 440 version: "{version}"', Verbosity.VERBOSE)

            if not self.plugin_config.ignore_public_pep440:
                raise PluginException(f'Invalid public PEP 440 version: "{version}"')

    def get_version(self) -> str:
        version = self.__get_version()
        self.validate_version(version)
        return version

    @classmethod
    def safe_get_version(cls, io: IO, poetry: Poetry) -> Optional[Version]:
        plugin_config = config.PluginConfig(poetry.pyproject)

        try:
            version = cls(io, plugin_config).get_version()
            return Version.parse(version)

        except Exception as ex:
            if not plugin_config.ignore_errors:
                raise ex

            if not isinstance(ex, PluginException):
                ex = PluginException(ex)

            io.write_error_line(f'{ex}. Ignore Exception.')

            return None
