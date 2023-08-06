from poetry.console.commands.command import Command

from poetry_git_version_plugin.exceptions import plugin_exception_wrapper


class GitVersionCommand(Command):
    name = 'git-version'

    @plugin_exception_wrapper
    def handle(self) -> None:  # pragma: no cover
        self.io.write_line(str(self.poetry.package.version))
