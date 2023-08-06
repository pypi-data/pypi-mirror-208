import logging
from dataclasses import dataclass

from msb.env import NameConst


@dataclass
class DbVendorConfig:
	query_to_list_tables: str
	query_to_drop_table: str
	excluded_tables: list

	def queries_to_drop_multiple_tables(self, table_list) -> list:
		_drop_table_queries = []
		if isinstance(table_list, list) and len(table_list) > 0:
			for table in table_list:
				if table[0] not in self.excluded_tables and self.query_to_drop_table.strip(" ") != "":
					_drop_table_queries.append(self.query_to_drop_table.format(table_name=table[0]))
		return _drop_table_queries


class DjangoMigrationConfig:
	_is_local_env: bool = False
	_remove_migration_files: bool = False
	_drop_tables_from_db: bool = False
	_db_to_drop_tables_from: list = list()
	_apps_to_migrate: list = list()
	_dbs_to_migrate: list = list()

	@property
	def is_local_env(self) -> bool:
		return self._is_local_env

	@property
	def remove_migration_files(self) -> bool:
		return self._remove_migration_files

	@property
	def drop_tables_from_db(self) -> bool:
		return self._drop_tables_from_db

	@property
	def db_to_drop_tables_from(self) -> tuple:
		return self._db_to_drop_tables_from

	@property
	def apps_to_migrate(self) -> tuple:
		return self._apps_to_migrate

	@property
	def dbs_to_migrate(self) -> tuple:
		return self._dbs_to_migrate

	def set_apps_to_migrate(self, *app_list):
		self._apps_to_migrate = app_list

	def set_dbs_to_migrate(self, *db_list):
		self._dbs_to_migrate = db_list

	def __init__(self, env: str, **kwargs):

		if isinstance(env, str):

			self._is_local_env = env.lower() == NameConst.LOCAL_ENV_NAME

			if self.is_local_env:
				self._remove_migration_files = kwargs.get("remove_migration_files") == True
				self._drop_tables_from_db = kwargs.get("drop_tables_from_db") == True
				self._db_to_drop_tables_from = kwargs.get("db_to_drop_tables_from") or [NameConst.DEFAULT_DATABASE_NAME]
		else:
			logging.warning("Invalid or empty environment name.")


class DjangoFixtureDirs:
	pass
