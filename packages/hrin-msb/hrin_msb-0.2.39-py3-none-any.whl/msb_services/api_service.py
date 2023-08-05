from django.db.models.query import QuerySet

from msb_cipher import Cipher
from msb_dataclasses import Singleton
from msb_dataclasses.search_parameter import SearchParameter
from msb_db import (DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET)
from msb_db.models import (MsbModel)
from msb_exceptions import CustomExceptionHandler
from .exceptions import ApiServiceExceptions


class ApiService(CustomExceptionHandler, metaclass=Singleton):
	db_model: MsbModel | None = None
	resource_name: str | None = None
	exception_class_name: ApiServiceExceptions | None = None

	@property
	def resource_name_value(self) -> str | None:
		try:
			if not self.resource_name:
				import re
				class_name = re.split('(?<=.)(?=[A-Z])', self.__class__.__name__.replace("Service", ""))
				return " ".join(class_name)
			return self.resource_name
		except Exception:
			return None

	@property
	def exception_class(self) -> ApiServiceExceptions:
		if not isinstance(self.exception_class_name, ApiServiceExceptions):
			return ApiServiceExceptions
		return self.exception_class_name

	@property
	def cipher(self):
		return Cipher

	def __decrypt(self, data):
		return Cipher.decrypt(data=data)

	def __init__(self):
		if self.db_model is None:
			raise ApiServiceExceptions.InvalidDatabaseModel(resource=self.resource_name_value)

	def search(self, params: SearchParameter) -> QuerySet:
		try:
			model_query = params.get_query(self.db_model)
			return model_query.all()[params.offset:params.offset + params.limit]
		except Exception:
			return QuerySet()

	def create(self, *model_data_list) -> bool:
		try:
			create_status = False
			if len(model_data_list) == 0:
				raise ApiServiceExceptions.InvalidDataForCreateOperation(resource=self.resource_name_value)

			if len(model_data_list) == 1:
				model_data = model_data_list[0]
				_model = self.db_model(**model_data)
				_model.save()
				create_status = True
			else:
				create_status = self.db_model.objects.bulk_create(
					[self.db_model(**model_data) for model_data in model_data_list]
				)
				create_status = True
		except Exception:
			raise ApiServiceExceptions.CreateOperationFailed(resource=self.resource_name_value)
		return create_status

	def retrieve(self, pk=None, silent=False):
		try:
			if pk is None:
				raise ApiServiceExceptions.InvalidPk(resource=self.resource_name_value)
			return self.db_model.objects.get(pk=pk)
		except self.db_model.DoesNotExist:
			if not silent:
				raise ApiServiceExceptions.ResourseDoesNotExists(resource=self.resource_name_value)
		except Exception as e:
			if not silent:
				raise ApiServiceExceptions.RetrieveOperationFailed(resource=self.resource_name_value)
		return None

	def list(self, limit: int = DEFAULT_QUERY_LIMIT, offset: int = DEFAULT_QUERY_OFFSET) -> QuerySet | None:
		try:
			offset = int(offset) if str(offset).isnumeric() else DEFAULT_QUERY_OFFSET
			limit = int(limit) if str(limit).isnumeric() else DEFAULT_QUERY_LIMIT

			fields = [
				i for i in self.db_model._list_field_names
				if (x := getattr(self.db_model, i, None)) and not isinstance(x, property)
			]
			data_set = self.db_model.objects.only(*fields).all()
			return data_set[offset:(limit + offset)] if len(fields) > 0 else None
		except Exception as e:
			raise ApiServiceExceptions.ListOperationFailed(resource=self.resource_name_value)

	def update(self, pk=None, **model_data) -> bool:
		try:
			status = False
			if (pk := self.__decrypt(pk)) is None:
				raise ApiServiceExceptions.InvalidPk(resource=self.resource_name_value)
			model_object = self.db_model.objects.filter(pk=pk)
			if model_object and not (status := model_object.update(**model_data)):
				raise ApiServiceExceptions.UpdateOperationFailed(resource=self.resource_name_value)
			return bool(status)
		except Exception as e:
			raise ApiServiceExceptions.UpdateOperationFailed(resource=self.resource_name_value)

	def delete(self, pk=None) -> bool:
		try:
			status = False

			if (pk := self.__decrypt(pk)) is None:
				raise ApiServiceExceptions.InvalidPk(resource=self.resource_name_value)
			model_object = self.db_model.objects.get(pk=pk)

			if model_object and not (status := model_object.delete()):
				raise ApiServiceExceptions.DeleteOperationFailed(resource=self.resource_name_value)
			return bool(status)
		except Exception as e:
			raise ApiServiceExceptions.DeleteOperationFailed(resource=self.resource_name_value)
