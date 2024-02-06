"""
setup global logging

note: It's my first time to use log function.
Reference: https://docs.python.org/zh-cn/3/howto/logging-cookbook.html#logging-cookbook
"""
import types
import typing
import logging
import functools


class UILoggingHandle:
    """
    UI handle, provides hooks
    """

    def __init__(self, log_hook: typing.Optional[typing.Callable[[str, int, str, ..., ...], typing.Any]] = None):
        """

        :param log_hook:
        """
        self.log_hook = log_hook

    def log(self, name: str, level: int, msg: str, args=(), kws=None):
        """
        set a log
        :param name: logger.name
        :param level:
        :param msg:
        :param args:
        :param kws:
        :return:
        """
        if self.log_hook is not None:
            self.log_hook(name, level, msg, args, kws)


DEFAULT_UI_LOGGING_HANDLE = UILoggingHandle()


class Logger:
    """
    the base logger, provides log decorators
    """

    def __init__(self, logger_name: str | None = None, ui_handle: typing.Optional[UILoggingHandle] = None):
        """
        :param logger_name: to be passed `logging.getLogger`
        :param ui_handle: UI Logging handle, use `logger.DEFAULT_UI_LOGGING_HANDLE` if is None.
        """
        self.logger = logging.getLogger(logger_name)
        self.ui_handle = ui_handle

    def debug(self, msg, *args, **kwargs):
        """
        return self.logger.debug
        """
        if self.ui_handle is None:
            DEFAULT_UI_LOGGING_HANDLE.log(self.logger.name, logging.DEBUG, msg, args, kwargs)
        return self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        return self.logger.info
        """
        if self.ui_handle is None:
            DEFAULT_UI_LOGGING_HANDLE.log(self.logger.name, logging.INFO, msg, args, kwargs)
        return self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        return self.logger.warning
        """
        if self.ui_handle is None:
            DEFAULT_UI_LOGGING_HANDLE.log(self.logger.name, logging.WARNING, msg, args, kwargs)
        return self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        return self.logger.error
        """
        if self.ui_handle is None:
            DEFAULT_UI_LOGGING_HANDLE.log(self.logger.name, logging.ERROR, msg, args, kwargs)
        return self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        return self.logger.critical
        """
        if self.ui_handle is None:
            DEFAULT_UI_LOGGING_HANDLE.log(self.logger.name, logging.CRITICAL, msg, args, kwargs)
        return self.logger.critical(msg, *args, **kwargs)

    def important_function(self, log_level: int = logging.INFO,
                           print_parameters: typing.Optional[typing.Iterable[str]] = None):
        """
        Return a wrapper to register the function as an important function.
        `logger.before_function_called` and `logger.logger_after_function_called` will be auto called.
        Logger will auto log it when you call the function.
        :param log_level: log level
        :param print_parameters: the parameters to print, if not found, set `"NOT FOUND!"`
        """
        return functools.partial(self._important_function,
                                 log_level=log_level, print_parameters=print_parameters)

    def _important_function(self, func, *, log_level, print_parameters):
        wrap = functools.partial(self.function_called, func, log_level, print_parameters)
        return functools.update_wrapper(wrap, func)

    def function_called(self, __function, __log_level, __print_parameters, *args, **kwargs):
        """
        Called when the important function be called.
        """
        self.before_function_called(__function, args, kwargs, log_level=__log_level,
                                    print_parameters=__print_parameters)
        try:
            ret = __function(*args, **kwargs)
        except Exception as err:
            self.logger.error(format(err))
            raise err
        else:
            self.after_function_called(__function, ret, __log_level)
            return ret

    def before_function_called(self, func: types.FunctionType, func_args: tuple, func_kwargs: dict[str, typing.Any],
                               log_level: int = logging.INFO,
                               print_parameters: typing.Optional[typing.Iterable[str]] = None):
        """
        The function called before an important function `func` called.
        :param func: The wrapped important function.
        :param func_args: function positional arguments
        :param func_kwargs: function keyword arguments
        :param log_level: log level
        :param print_parameters: the parameters to print, if not found, set `"NOT FOUND!"`
        :return: None
        """
        func_name = func.__name__ if hasattr(func, "__name__") else getattr(type(func), "__name__", "UNKNOWN")
        if not print_parameters:
            self.logger.log(log_level, 'call function "%s"', func_name)
            return
        f = 'call function "%s", with ' + "=%s, ".join(print_parameters)
        ls = []
        key_args = dict(zip(func.__annotations__.keys(), func_args))
        key_args.update(func_kwargs)
        for name in print_parameters:
            if name in key_args:
                ls.append(key_args[name])
            else:
                ls.append('"NOT FOUND!"')
        self.logger.log(log_level, f, func_name, *ls)

    def after_function_called(self, func, returned, log_level: int):
        """
        The function called after an important function `func` called.
        """
        func_name = func.__name__ if hasattr(func, "__name__") else getattr(type(func), "__name__", "UNKNOWN")
        self.logger.log(log_level, 'function "%s" exited, returned %s', func_name, returned)
