from typing import Callable

from poetry_git_version_plugin import config


class PluginException(RuntimeError):
    def __str__(self) -> str:
        if isinstance(self.args[0], BaseException):
            ex = self.args[0]
            message = ex.__class__.__name__
            if ex.args:
                args_message = ': ' + '; '.join(ex.args) if ex.args else ''
                message = f'{message}{args_message}'

        else:
            message = '; '.join(self.args)

        return f'<b>{config.PLUGIN_NAME}</b>: {message}'


def plugin_exception_wrapper(func: Callable):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except PluginException as ex:
            raise ex

        except BaseException as ex:
            raise PluginException(ex) from ex

    return wrapper
