import logging
import os

from msb.env import (NameConst, PathConst)

from .dataclasses import (DjangoMigrationConfig)
from .funcs import (log_to_console, get_django_db_vendor_config)


class DjangoBase:
	def _execute_cmd(self, *args, format=True, log=True):
		from django.core.management import call_command
		if log:
			log_to_console(msg=f"executing {' '.join(args if len(args) > 0 else 'all')} ", format=format)
		call_command(*args)

	def _db_query(self, db_connection, *queries):
		if db_connection and len(queries) > 0:
			with db_connection.cursor() as cursor:
				_result = []
				for query in queries:
					print(f"Executing Query = {query}\n")
					query_result = cursor.execute(query)
					if query.lstrip(' ').lower().startswith(('select', 'show')):
						_result.append(cursor.fetchall())
					else:
						_result.append(query_result)
				return _result[0] if len(_result) == 1 else _result


class DjangoMigration(DjangoBase, DjangoMigrationConfig):

	def run(self):
		try:
			if self.drop_tables_from_db:
				self.__drop_tables_from_database()
			self.__build_migrations()
			self.__migrate_databases()

		except Exception as e:
			logging.exception(e)

	def __init__(self, env: str, **kwargs):
		DjangoMigrationConfig.__init__(self, env=env, **kwargs)

	def __remove_migration_files(self, migration_dir: str):
		if self.is_local_env or self.remove_migration_files:
			log_to_console(msg=f"Removing Migration Files From '{migration_dir}' ")
			for miration_file in os.listdir(migration_dir):
				if miration_file not in ['__init__.py', '__pycache__']:
					os.remove(os.path.join(migration_dir, miration_file))
					log_to_console(miration_file)

	def __drop_tables_from_database(self):
		if not self.is_local_env:
			return logging.warning(msg=f"Dropping Tables only allowed in Local Enviroment")
		from django.db import connections
		for db in self.db_to_drop_tables_from:
			con = connections[db]
			db_config = get_django_db_vendor_config(db_connection=con)
			if db_config:
				log_to_console(f"Dropping Tables From Database[{db}]", format=True)
				table_list = self._db_query(con, db_config.query_to_list_tables)
				queries_to_drop_tables = db_config.queries_to_drop_multiple_tables(table_list, )

				self._db_query(con, *[*queries_to_drop_tables])

	def __build_migrations(self):
		for app_name in self.apps_to_migrate:
			log_to_console(msg=f"Buiding Migration Files For '{app_name}' ", format=True)

			migration_dir = PathConst.APP_DIR_PATH.joinpath(app_name).joinpath(NameConst.MIGRATIONS_DIR_NAME)
			if not os.path.isdir(migration_dir):
				os.mkdir(migration_dir, 0o777)

			self.__remove_migration_files(migration_dir=migration_dir)
			self._execute_cmd("makemigrations", app_name)

	def __migrate_databases(self):
		xargs = ["--no-input"] if not self.is_local_env else []
		for db in set(self.dbs_to_migrate):
			self._execute_cmd("migrate", "--database", db, *xargs)


class DjangoFixtures(DjangoBase):

	def load(self, *from_dirs):
		for fixture_dir in from_dirs:
			fixture_dir = PathConst.FIXTURES_DIR_PATH.joinpath(fixture_dir.lower())
			self.__load_database_fixtures_from_dir(dir=fixture_dir)

	def __init__(self, env: str, file_ext: str = NameConst.YAML_FILE_EXTENTION_NAME):
		self.env = env
		self.file_ext = file_ext

	def __get_list_of_fixtures_to_load_from_dir(self, dir: str):
		if os.path.isdir(dir):
			return sorted(list(filter(lambda f: os.path.splitext(f)[1] == f".{self.file_ext}", os.listdir(dir))))
		else:
			logging.warning(f"Fixture Directory '{dir}' not found.")
			return []

	def __load_database_fixtures_from_dir(self, dir: str):
		_fixtures_list = self.__get_list_of_fixtures_to_load_from_dir(dir=dir)
		_seperator = '-' * 50
		_log = f"## Loading {len(_fixtures_list)} fixtures from '{os.path.basename(dir)}' Dir in following sequence :"
		print(_seperator, _log,)
		for _fixture in _fixtures_list:
			_status = "Success"
			try:
				self._execute_cmd("loaddata", _fixture, format=False, log=False)
			except Exception as e:
				_status = f"Failed->{e}"
			finally:
				print(_fixture,":", _status)
