"""
setup global logging

note: It's my first time to use log function.
Reference: https://docs.python.org/zh-cn/3/howto/logging-cookbook.html#logging-cookbook
"""
import types
import typing
import logging
import functools


class Logger:
    """
    the base logger, provides log decorators
    """

    def __init__(self, logger_name: str | None = None):
        """
        :param logger_name: to be passed `logging.getLogger`
        """
        self.logger = logging.getLogger(logger_name)

    def debug(self, msg, *args, **kwargs):
        """
        return self.logger.debug
        """
        return self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        return self.logger.info
        """
        return self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        return self.logger.debug
        """
        return self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        return self.logger.error
        """
        return self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        return self.logger.critical
        """
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

    def _important_function(self, func, log_level, print_parameters):
        wrap = functools.partial(self.function_called,
                                 __log_level=log_level, __print_parameters=print_parameters)
        return functools.update_wrapper(wrap, func)

    def function_called(self, func, *args, __log_level, __print_parameters, **kwargs):
        """
        Called when the important function be called.
        """
        self.before_function_called(func, args, kwargs, log_level=__log_level, print_parameters=__print_parameters)
        try:
            ret = func(*args, **kwargs)
        except Exception as err:
            self.logger.error(format(err))
            raise err
        else:
            self.after_function_called(func, ret, __log_level)
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
