import logging

from .constants import (SIMPLE_LOG_FORMAT)


# custom log handler that emits to the database
class DatabaseLogger(logging.Handler):
	__log_callback_func = None

	def __init__(self, callback_func=None, *args, **kwargs):
		logging.Handler.__init__(self, *args, **kwargs)
		self.setFormatter(logging.Formatter(SIMPLE_LOG_FORMAT))
		self.level = logging.INFO
		self.__log_callback_func = callback_func

	def emit(self, record):
		try:
			if callable(self.__log_callback_func):
				return self.__log_callback_func(**record.__dict__)
		except Exception:
			pass
