from django.urls import include, path

from .constants import CRUD_URL_PK_NAME, CrudMethods
from .constants import REQUEST_METHODS as HttpVerbs


class MsbApiDefaultRoutes:

	@staticmethod
	def search_action_routes(cls, search: bool):
		actions = {HttpVerbs.POST: (CrudMethods.search if search == True else CrudMethods.not_found)}
		return path("/search", cls.as_view(actions=actions))

	@staticmethod
	def single_action_routes(cls, retrieve: bool = True, update: bool = True, delete: bool = True):
		actions = {
			HttpVerbs.GET: (CrudMethods.retrieve if retrieve == True else CrudMethods.not_found),
			HttpVerbs.PUT: (CrudMethods.update if update == True else CrudMethods.not_found),
			HttpVerbs.DELETE: (CrudMethods.delete if delete == True else CrudMethods.not_found),
		}
		return path(f"/<str:{(cls.pk_name or CRUD_URL_PK_NAME)}>", cls.as_view(actions=actions))

	@staticmethod
	def bulk_action_routes(cls, create: bool = True, list: bool = True, bulk_update: bool = True, bulk_delete: bool = True):
		actions = {
			HttpVerbs.GET: (CrudMethods.list if list == True else CrudMethods.not_found),
			HttpVerbs.POST: (CrudMethods.create if create == True else CrudMethods.not_found),
			HttpVerbs.PUT: (CrudMethods.bulk_update if bulk_update == True else CrudMethods.not_found),
			HttpVerbs.DELETE: (CrudMethods.bulk_delete if bulk_delete == True else CrudMethods.not_found),
		}
		return path("", cls.as_view(actions=actions))


class MsbApiRoutes:
	@classmethod
	def route(cls, method: str, url: str, action: str):
		return path(url, cls.as_view(actions={method: action}))

	@classmethod
	def crud_routes(cls, create: bool = True, retrieve: bool = True, update: bool = True, delete: bool = True,
	                list: bool = True, bulk_update: bool = True, bulk_delete: bool = True, search: bool = True):
		return include([
			MsbApiDefaultRoutes.search_action_routes(cls, search),
			MsbApiDefaultRoutes.bulk_action_routes(cls, create, list, bulk_update, bulk_delete),
			MsbApiDefaultRoutes.single_action_routes(cls, retrieve, update, delete),
		])
