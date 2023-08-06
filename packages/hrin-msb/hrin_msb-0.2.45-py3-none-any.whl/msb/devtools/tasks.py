import logging
from argparse import ArgumentParser

from msb.env import NameConst, PathConst

from .constants import (REGEX_TO_SELECT_ENV_VARIABLE, REGEX_TO_REPLACE_ENV_VARIABLE)
from .django import (DjangoMigration, DjangoFixtures)
from .funcs import (require_django, log_to_console)


def build_prod_env_file_from(dev_env_file_path: str = None, prod_env_file_path: str = None):
	import os, re

	dev_env_file_path = dev_env_file_path or PathConst.DEV_ENV_FILE_PATH
	prod_env_file_path = prod_env_file_path or PathConst.PROD_ENV_FILE_PATH

	if os.path.isfile(dev_env_file_path) and os.path.isfile(prod_env_file_path):
		with open(dev_env_file_path, "r+") as dev_env_file:
			dev_env_file_content = dev_env_file.read()

		prod_env_file_content = re.sub(
			REGEX_TO_SELECT_ENV_VARIABLE, REGEX_TO_REPLACE_ENV_VARIABLE, dev_env_file_content
		)

		with open(prod_env_file_path, "w+") as prod_env_file:
			prod_env_file.write(prod_env_file_content)


@require_django
class MsbAppSetupTask:

	@property
	def is_local_env(self):
		from django.conf import settings
		return self.env.lower() == NameConst.LOCAL_ENV_NAME and settings.IS_LOCAL_ENVIRONMENT

	def _initialize_setup_environment(self):
		parser = ArgumentParser(description='Run Msb Setup Script For Django Application')
		parser.add_argument('-env', choices=NameConst.ENV_NAME_LIST, help='Environment Name', required=True)
		args = parser.parse_args()
		self.env = args.env

	def __load_django_db_fixtures(self):
		_fixture_dirs = [NameConst.DEFAULT_FIXTURE_DIR_NAME, *self.fixture_dirs]
		log_to_console(f"Loading Database Fixtures From {_fixture_dirs} Dirs.", format=True)
		database_fixtures = DjangoFixtures(env=self.env)
		database_fixtures.load(*_fixture_dirs)

	def __run_django_db_migrations(self, apps: list, dbs: list, load_fixtures: bool = False, **kwargs):
		try:
			migration = DjangoMigration(env=self.env, **kwargs)
			migration.set_apps_to_migrate(*apps)
			migration.set_dbs_to_migrate(*dbs)
			migration.run()
		except Exception as e:
			logging.exception(e)

	def __init__(self, **kwargs):
		self._initialize_setup_environment()

	def __ask(self, ques: str):
		return str(input(f"{ques}?. : ")).lower().strip(" ")

	def run_database_setup(self, apps: list, dbs: list, fixture_config: dict):

		self.fixture_dirs = fixture_config.get(self.env) or []
		log_to_console(f"Welcome to Database Setup Wizard", format=True)
		print(f"HINT : Reply/Input '1' for yes/agree, anything else to no/skip.\n{'*' * 100}")

		run_db_migrations, drop_tables, load_fixtures = (True, False, True)

		if self.is_local_env:
			if run_db_migrations := bool(self.__ask(f"Run Database Migrations for {apps}")):
				drop_tables = bool(self.__ask("Remove Database tables? This will also remove old migration files."))

			load_fixtures = bool(self.__ask(f"Load Database fixtures for {self.env} Env"))

		if run_db_migrations:
			self.__run_django_db_migrations(
				apps=apps, dbs=dbs, load_fixtures=load_fixtures,
				remove_migration_files=drop_tables,
				drop_tables_from_db=drop_tables,
				db_to_drop_tables_from=[NameConst.DEFAULT_DATABASE_NAME]
			)

		if load_fixtures:
			self.__load_django_db_fixtures()


class MsbAppPreCommitTask:
	pass
