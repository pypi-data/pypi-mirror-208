from abc import (abstractmethod, ABC)

from .constants import (
	DEFAULT_MIGRATION_DATABASE,
	DEFAULT_DATABASE_NAME, DEFAULT_APP_LABLES_TO_ROUTE
)


class DjangoDatabaseRouterInterface(ABC):
	OP_LIST = ('write', 'read', 'relation', 'migration')
	OP_WRITE, OP_READ, OP_RELATION, OP_MIGRATION = OP_LIST
	db_allowed_app_labels: set = DEFAULT_APP_LABLES_TO_ROUTE

	@abstractmethod
	def db_for_read(self, model, **hints):
		"""Send all read operations of the model to `__database_to_read_from`."""
		pass

	@abstractmethod
	def db_for_write(self, model, **hints) -> str:
		"""Send all write operations of the model to `__database_to_write_to`."""
		pass

	@abstractmethod
	def allow_relation(self, obj1, obj2, **hints) -> bool:
		"""Determine if relationship is allowed between two objects."""
		pass

	@abstractmethod
	def allow_migrate(self, db, app_label, model_name=None, **hints) -> bool:
		"""Ensure that the app's models get created on the right database."""
		pass


class MsbDatabaseRouter(DjangoDatabaseRouterInterface):
	db_allowed_app_labels: set = DEFAULT_APP_LABLES_TO_ROUTE
	db_to_read_from: str = DEFAULT_DATABASE_NAME
	db_to_write_to: str = DEFAULT_DATABASE_NAME
	db_to_migrate_to: set = DEFAULT_MIGRATION_DATABASE

	"""
	   Determine how to route database calls for an app's models (in this case, for an app named Example).
	   All other models will be routed to the next router in the DATABASE_ROUTERS setting if applicable,
	   or otherwise to the default database.
	   """

	def get_mapping(self, app: str, model_name: str, op: str):
		"Implement this method in child classes"
		pass

	def db_for_read(self, model, **hints):

		"""Send all read operations of the model to `__database_to_read_from`."""
		app_label = model._meta.app_label
		model_name = model.__name__.lower()
		if (_db := self.get_mapping(app=app_label, model_name=model_name, op=self.OP_WRITE)) is not None:
			return _db
		elif app_label in self.db_allowed_app_labels:
			return self.db_to_read_from
		else:
			return None

	def db_for_write(self, model, **hints) -> str:
		"""Send all write operations of the model to `__database_to_write_to`."""
		app_label = model._meta.app_label
		model_name = model.__name__.lower()
		if (_db := self.get_mapping(app=app_label, model_name=model_name, op=self.OP_WRITE)) is not None:
			return _db
		elif app_label in self.db_allowed_app_labels:
			return self.db_to_write_to
		else:
			return None

	def allow_relation(self, obj1, obj2, **hints) -> bool:
		"""Determine if relationship is allowed between two objects."""

		# Allow any relation between two models that are both in the Example app.
		if obj1._meta.app_label in self.db_allowed_app_labels or obj2._meta.app_label in self.db_allowed_app_labels:
			return True
		# No opinion if neither object is in the Example app (defer to default or other routers).
		elif self.db_to_read_from not in [obj1._meta.app_label, obj2._meta.app_label]:
			return None
		# Block relationship if one object is in the Example app and the other isn't.
		return False

	def allow_migrate(self, db, app_label, model_name=None, **hints) -> bool:
		"""Ensure that the app's models get created on the right database."""
		model_name = model_name.lower() if model_name is not None else ''
		# No opinion for the scenario as of now
		_migrate = None

		if (mapped_db := self.get_mapping(app=app_label, model_name=model_name, op=self.OP_MIGRATION)) is not None:
			_migrate = mapped_db == db

		# check if we should even try to route
		elif app_label in self.db_allowed_app_labels:
			# Allow app model to migrate on the database
			_migrate = db in self.db_to_migrate_to

		return _migrate
