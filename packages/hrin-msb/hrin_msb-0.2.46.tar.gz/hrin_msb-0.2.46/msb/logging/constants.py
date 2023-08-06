import logging

LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_DEBUG = logging.DEBUG
LOG_LEVEL_WARNING = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR
LOG_LEVEL_CRITICAL = logging.CRITICAL

CHOICES_LOG_LEVELS = (
	(LOG_LEVEL_INFO, 'INFO'),
	(LOG_LEVEL_DEBUG, 'DEBUG'),
	(LOG_LEVEL_WARNING, 'WARNING'),
	(LOG_LEVEL_ERROR, 'ERROR'),
	(LOG_LEVEL_CRITICAL, 'CRITICAL'),
)

LOG_DB = "logs"
LOG_TABLE = "system_logs"
DEFAULT_CONSOLE_HANDLER_NAME = 'console'
DEFAULT_FILE_HANDLER_NAME = 'file'

DEBUG_REQUIRED_FILTER_CLASS = "django.utils.log.RequireDebugTrue"
DEBUG_REQUIRED_FILTER_NAME = 'require_debug_true'

SIMPLE_LOG_FORMAT = '[%(levelname)s] : %(message)s '
SIMPLE_LOG_FILE_FORMAT = '[%(levelname)s] %(asctime)s : %(message)s '
VERBOSE_LOG_FORMAT = "%(levelname)s %(asctime)s %(module)s %(process:d)s %(thread:d)s %(message)s "

LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_FILTERS = {
	DEBUG_REQUIRED_FILTER_NAME: {"()": DEBUG_REQUIRED_FILTER_CLASS}
}

DEFAULT_DBLOG_COLUMN_MAPPINGS = {"level": "levelname", "message": "message", }

SYSTEM_DBLOG_COLUMN_MAPPINGS = {
	**DEFAULT_DBLOG_COLUMN_MAPPINGS, "logger": "name", "msg": "msg", "module": "module", "stack_info": "stack_info",
	"filename": "filename", "func_name": "funcName", "thread_name": "threadName", "process_name": "processName",
	"args": "args", "pathname": "pathname", "exc_info": "exc_info", "exc_text": "exc_text", "lineno": "lineno",
}
