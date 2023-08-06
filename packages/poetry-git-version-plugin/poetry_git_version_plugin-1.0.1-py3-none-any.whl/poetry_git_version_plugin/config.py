import os
from copy import deepcopy

from poetry.core.pyproject.toml import PyProjectTOML

from poetry_git_version_plugin.utils import serialize_to_boolean

PLUGIN_NAME = 'poetry-git-version-plugin'


class PluginConfig(object):
    """Обертка над конфигурацией pyproject"""

    pyproject: PyProjectTOML

    _default_setting = {
        # Maker alpha
        'make_alpha_version': True,
        # Alpha Version Format
        'alpha_version_format': '{version}a{distance}',
        # 'alpha_version_format': '{version}a{distance}+{commit_hash}',
        # Ignore PEP 440
        'ignore_pep440': True,
        # Ignore public format PEP 440
        'ignore_public_pep440': True,
        # Ignore some errors
        'ignore_errors': True,
    }

    def __init__(self, pyproject: PyProjectTOML) -> None:
        self.pyproject = pyproject

    @property
    def settings(self):
        settings = self.pyproject.data.get('tool', {}).get(PLUGIN_NAME, {})
        new_settings = deepcopy(self._default_setting)
        new_settings.update(settings)
        return new_settings

    @property
    def make_alpha_version(self) -> bool:
        try:
            return serialize_to_boolean(os.environ['PACKAGE_VERSION_MAKE_ALPHA_VERSION'])

        except KeyError:
            return self.settings['make_alpha_version']

    @property
    def alpha_version_format(self) -> str:
        try:
            return os.environ['PACKAGE_VERSION_ALPHA_VERSION_FORMAT']

        except KeyError:
            return self.settings['alpha_version_format']

    @property
    def ignore_pep440(self) -> bool:
        try:
            return serialize_to_boolean(os.environ['PACKAGE_VERSION_IGNORE_PEP440'])

        except KeyError:
            return self.settings['ignore_pep440']

    @property
    def ignore_public_pep440(self) -> bool:
        try:
            return serialize_to_boolean(os.environ['PACKAGE_VERSION_IGNORE_PUBLIC_PEP440'])

        except KeyError:
            return self.settings['ignore_public_pep440']

    @property
    def ignore_errors(self) -> bool:
        try:
            return serialize_to_boolean(os.environ['PACKAGE_VERSION_IGNORE_ERRORS'])

        except KeyError:
            return self.settings['ignore_errors']
