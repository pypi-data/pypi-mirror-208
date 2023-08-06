import logging
import os
from datetime import datetime

from msb.env import (Config)
from .constants import (
	LOG_DATETIME_FORMAT, SIMPLE_LOG_FORMAT,
	DEFAULT_FILE_HANDLER_NAME, DEFAULT_CONSOLE_HANDLER_NAME
)


def make_log_file_name(dir: str = '', filename: str = None):
	filename_prefix = f"{filename}-" if filename not in ['', None] else ''
	return os.path.join(dir, f"{filename_prefix}{datetime.today().strftime('%Y-%m-%d')}.log")


class LogConfig:
	_default_log_level: str
	_default_format_str: str

	def __init__(self, **kwargs):
		self._default_log_level = kwargs.get('default_level') or logging.WARNING
		self._default_format_str = None

	@staticmethod
	def init_default_config(logsdir: str, default_level: str = logging.INFO, emulate_prod=False):

		default_log_config = LogConfig(default_level=default_level)

		console_log_handler = default_log_config.get_console_handler(
			DEFAULT_CONSOLE_HANDLER_NAME,
			level=logging.INFO,
		)

		system_exceptions_file_handler = default_log_config.get_file_handler(
			DEFAULT_FILE_HANDLER_NAME, logs_dir=logsdir, level=logging.ERROR,
			formatter=SIMPLE_LOG_FORMAT, filename='exceptions'
		)

		debug_file_log_handler = default_log_config.get_file_handler(
			DEFAULT_FILE_HANDLER_NAME, logs_dir=logsdir, level=logging.DEBUG,
			formatter=SIMPLE_LOG_FORMAT, filename='log'
		)

		_root_logging_handlers = [console_log_handler]
		_debug_logging_handlers = [debug_file_log_handler]

		if Config.is_local_env():
			_root_logging_handlers.append(console_log_handler)
			_debug_logging_handlers.append(console_log_handler)
			if emulate_prod:
				_root_logging_handlers.append(system_exceptions_file_handler)
				_debug_logging_handlers.append(system_exceptions_file_handler)

		else:
			_root_logging_handlers.append(system_exceptions_file_handler)

		default_log_config.add_logger('console', handlers=[console_log_handler])
		default_log_config.add_logger('root', handlers=_root_logging_handlers)
		default_log_config.add_logger('debug', handlers=_debug_logging_handlers, level=logging.INFO)

	def add_formatter(self, name: str, format: str = ''):
		self.formatters[name] = {"format": format}

	def add_filters(self, name: str, handler_class: str):
		self.filters[name] = {
			'()': handler_class,
		}

	def add_logger(self, name: str, level: str = None, handlers: list = None, **kwargs):
		try:
			log_handlers = handlers if isinstance(handlers, list) else []
			_logger = logging.getLogger(name=name)
			log_level = level if level is not None else self._default_log_level

			_logger.setLevel(level=log_level)
			_logger.propagate = kwargs.get('propagate') == True

			for log_handler in log_handlers:
				_logger.addHandler(log_handler)

		except Exception as e:
			print(f"Logger registration failed for '{name}' :\n{e}")

	def get_file_handler(self, name, logs_dir: str, filename: str = None, handler_class=None, **kwargs):
		from logging.handlers import TimedRotatingFileHandler
		handler_class = handler_class if callable(handler_class) else TimedRotatingFileHandler
		init_kwargs = dict(filename=make_log_file_name(dir=logs_dir, filename=filename), when='midnight')
		return self.__build_log_handler(
			name=name, log_handler=handler_class, init_kwargs=init_kwargs, level=kwargs.get('level'),
			formatter=kwargs.get("formatter"), filters=kwargs.get('filters')
		)

	def get_email_handler(self, name, email_backend, handler_class: str = None, **kwargs):
		from django.utils.log import AdminEmailHandler
		handler_class = handler_class if callable(handler_class) else AdminEmailHandler
		init_kwargs = dict(
			include_html=kwargs.get('include_html') == True,
			email_backend=email_backend,
			reporter_class=kwargs.get('reporter_class')
		)
		return self.__build_log_handler(
			name=name, log_handler=handler_class, init_kwargs=init_kwargs, level=kwargs.get('level'),
			formatter=kwargs.get("formatter"), filters=kwargs.get('filters')
		)

	def get_console_handler(self, name, handler_class: str = None, **kwargs):
		handler_class = handler_class if callable(handler_class) else logging.StreamHandler
		init_kwargs = {}
		return self.__build_log_handler(
			name=name, log_handler=handler_class, init_kwargs=init_kwargs,
			level=kwargs.get('level'), formatter=kwargs.get("formatter"), filters=kwargs.get('filters')
		)

	def get_database_handler(self, name, func, **kwargs):
		from .handlers import DatabaseLogger
		init_kwargs = dict(callback_func=func)
		return self.__build_log_handler(
			name=name, log_handler=DatabaseLogger, init_kwargs=init_kwargs,
			level=kwargs.get('level'), formatter=kwargs.get("formatter"), filters=kwargs.get('filters')
		)

	def __build_log_handler(self, log_handler: logging.Handler, init_kwargs: dict = None, **kwargs):
		try:
			init_kwargs = init_kwargs if isinstance(init_kwargs, dict) else {}
			log_formatter = kwargs.get("formatter") or SIMPLE_LOG_FORMAT
			log_level = kwargs.get("level") or logging.WARNING
			_handler = log_handler(**init_kwargs)
			_handler.setLevel(level=log_level)
			_handler.setFormatter(logging.Formatter(log_formatter, datefmt=LOG_DATETIME_FORMAT))
			return _handler
		except Exception as e:
			logging.warning(e)
