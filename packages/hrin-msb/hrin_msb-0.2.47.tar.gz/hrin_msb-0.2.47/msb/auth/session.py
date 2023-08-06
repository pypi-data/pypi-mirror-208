import datetime
from dataclasses import dataclass
from typing import (List, Dict)


@dataclass
class UserAccountType:
	id: int
	name: str


@dataclass
class UserRole:

	def __init__(self, **kwargs):
		self.id = kwargs.get('id')
		self.name = kwargs.get('name')
		self.access_type = kwargs.get('access_type')

	def set_role(self, id: int, name: str, access_type: int):
		self.id, self.name, self.access_type = (id, name, access_type)
		return self


@dataclass
class UserLocation:

	def __init__(self, **kwargs):
		self.l_key = kwargs.get('l_key')
		self.name = kwargs.get('name')
		self.c_key = kwargs.get('c_key')
		self.country = kwargs.get('country')

	def set_location(self, id: int, name: str):
		self.l_key, self.name = (id, name)
		return self

	def set_country(self, id: int, name: str):
		self.c_key, self.country = (id, name)
		return self


@dataclass
class MenuPermissions:

	def __init__(self, menu_id: str = None, permission_str: str = ''):
		self.menu_id = menu_id
		self.permission_str = permission_str if (isinstance(permission_str, str) and len(permission_str) > 0) else "0000"

	@property
	def can_create(self):
		return bool(self.permission_str[0])

	@property
	def can_read(self):
		return bool(self.permission_str[1])

	@property
	def can_update(self):
		return bool(self.permission_str[2])

	@property
	def can_delete(self):
		return bool(self.permission_str[3])


@dataclass
class Reporties:
	def __init__(self, *reporties):
		self._reporties: list = list(reporties)

	def add(self, *reporties):
		self._reporties.extend(list(reporties))


class SessionData:

	def to_json(self):
		return {k: (v.__dict__ if hasattr(v, '__dict__') else v) for k, v in self.__dict__.items()}

	def __parsed_token_data(self, value, data_type):
		if not isinstance(value, data_type):
			return data_type(**value) if isinstance(value, dict) else data_type(*value)
		return value

	def __init__(self, id: id = None, email: str = None, username: str = None, **kwargs):
		self.id: int = id
		self.email: str = email
		self.username: str = username

		self.work_id: str = kwargs.get('work_id', '')
		self.image: str = kwargs.get('image', '')
		self.has_management_access: bool = False
		self.permissions: Dict = dict()
		self.login_time = datetime.datetime.now().__str__()
		self.auth_type = kwargs.get('auth_type', None)

		self.location: UserLocation = self.__parsed_token_data(kwargs.get('location', {}), UserLocation)
		self.role: UserRole = self.__parsed_token_data(kwargs.get('role', {}), UserRole)

		self.subscriptions: List = kwargs.get('subscriptions', [])
		self.dr_list: List = kwargs.get('dr_list', [])
		self.is_authenticated = kwargs.get('is_authenticated', False)

	def add_permission(self, menu_id, permission):
		self.permissions[menu_id] = permission

	def add_subscription(self, *subscriptiions):
		self.subscriptions.extend(subscriptiions)

	def set_has_management_access(self, status: bool = False):
		if (not self.has_management_access) and (status):
			self.has_management_access = status

	def add_reporties(self, *reporties):
		# if len(reporties) > 0:
		self.dr_list.extend(list(reporties))

	def set_is_authenticated(self, status):
		self.is_authenticated = status

	def set_auth_type(self, auth_type: str):
		self.auth_type = auth_type

	def get(self, key: str = '', default=None):
		return getattr(self, key, default)
