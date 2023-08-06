import logging

from django.db.models import (manager, DateTimeField, IntegerField, CharField, TextField)

from msb.logging import (
	LOG_DB, LOG_TABLE, CHOICES_LOG_LEVELS, DEFAULT_DBLOG_COLUMN_MAPPINGS,
	SYSTEM_DBLOG_COLUMN_MAPPINGS
)
from .models import (MsbModel)


class LoggingModelManager(manager.Manager):
	log_db = LOG_DB

	def get_queryset(self):
		return super(LoggingModelManager, self).get_queryset().using(self.log_db)

	@property
	def exceptions(self):
		return self.get_queryset().filter(level=logging.CRITICAL)

	@property
	def errors(self):
		return self.get_queryset().filter(level=logging.ERROR)

	@property
	def warnings(self):
		return self.get_queryset().filter(level=logging.WARNING)

	@property
	def info(self):
		return self.get_queryset().filter(level=logging.INFO)


class LoggingModel(MsbModel):
	_log_table_columns_mapping: dict = DEFAULT_DBLOG_COLUMN_MAPPINGS

	class Meta:
		abstract = True
		managed = False

	level = CharField(choices=CHOICES_LOG_LEVELS, max_length=255, default=logging.INFO)
	message = TextField(default=None, null=True)
	created_at = DateTimeField(auto_now_add=True, db_column='created_at')

	objects = LoggingModelManager()

	@classmethod
	def create(cls, *args, **kwargs):

		init_kwargs = kwargs
		init_args = args
		try:
			if isinstance(cls._log_table_columns_mapping, dict) and len(cls._log_table_columns_mapping.keys()) > 0:
				init_kwargs = {k: kwargs.get(v) for k, v in cls._log_table_columns_mapping.items()}

			return cls(*init_args, **init_kwargs).save()

		except Exception as e:
			return logging.warning(e)


class SystemLogModel(LoggingModel):
	_log_table_columns_mapping: dict = SYSTEM_DBLOG_COLUMN_MAPPINGS

	class Meta:
		db_table = LOG_TABLE
		abstract = True
		managed = False

	logger = CharField(max_length=255, default='root')

	msg = TextField(default=None)
	module = CharField(max_length=255, default=None, null=True)
	func_name = CharField(max_length=255, default=None, null=True)
	thread_name = CharField(max_length=255, default=None, null=True)
	process_name = CharField(max_length=255, default=None, null=True)
	filename = CharField(max_length=255, default=None, null=True)

	args = TextField(default=None, null=True)
	pathname = TextField(default=None, null=True)
	exc_info = TextField(default=None, null=True)
	exc_text = TextField(default=None, null=True)
	stack_info = TextField(default=None, null=True)
	lineno = IntegerField(default=0, null=True)

	objects = LoggingModelManager()
