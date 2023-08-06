from django.db.models import QuerySet
from msb.auth import (Permissions, api_permissions)
from msb.dataclasses import SearchParameter
from msb.http import (RestResponse)
from msb.services import ApiService
from msb.validation import DefaultRules

from .api_view import ApiView
from .constants import (CrudActions, CRUD_URL_PK_NAME)
from .funcs import ApiCrudRoutes


class ApiViewset(ApiView, ApiCrudRoutes):
	service_class: ApiService = None
	validation_schema_class = None
	search_parameter_class: SearchParameter = SearchParameter
	pk_name: str = CRUD_URL_PK_NAME

	def dispatch(self, request, *args, **kwargs):

		if (pk := kwargs.get(self.pk_name, None)) is not None:
			kwargs.update({self.pk_name: self.cipher.decrypt(pk), })
		return super().dispatch(request, *args, **kwargs)

	@api_permissions(Permissions.Management, override=False)
	def create(self, *args, **kwargs) -> RestResponse:
		try:
			is_bulk = not isinstance(self.payload, dict)
			self._validate_api_input(CrudActions.create, inp=self.payload, unknown=False, bulk=is_bulk)
			_create_payload = [self.payload] if not is_bulk else self.payload

			self.service_class.create(*_create_payload)
			return self.api_response.success()

		except Exception as e:
			return self.api_response.exception(e)

	@api_permissions(Permissions.Management, override=False)
	def retrieve(self, *args, **kwargs) -> RestResponse:
		try:
			self._validate_api_input(CrudActions.retrieve, inp=kwargs)
			_pk = kwargs.get(self.pk_name)
			result = self.service_class.retrieve(pk=_pk, silent=False)
			if type(result) not in [list, dict]:
				result = result.dict() if hasattr(result, "dict") else []
			return self.api_response.success(data=result)
		except Exception as e:
			return self.api_response.exception(e=e)

	@api_permissions(Permissions.Management, override=False)
	def list(self, *args, **kwargs) -> RestResponse:
		try:
			limit = self.params.get('limit')
			offset = self.params.get('offset')
			query_data = self.service_class.list(limit=limit, offset=offset)
			_data = []
			if isinstance(query_data, QuerySet):
				_data = [data.list_fields for data in query_data if hasattr(data, 'list_fields')]
			else:
				_data = query_data
			return self.api_response.success(data=_data)
		except Exception as e:
			return self.api_response.exception(e=e)

	@api_permissions(Permissions.Management, override=False)
	def update(self, *args, **kwargs) -> RestResponse:
		try:
			_rule = DefaultRules.pk_validation_rule(self.pk_name)
			_pk = kwargs.get(self.pk_name)
			_update_data = self.payload
			self._validate_api_input(CrudActions.update, inp=kwargs, rule=_rule)
			self._validate_api_input(CrudActions.update, inp=_update_data)
			self.service_class.update(pk=_pk, **_update_data)
			return self.api_response.success()
		except Exception as e:
			return self.api_response.exception(e=e)

	@api_permissions(Permissions.Management, override=False)
	def bulk_update(self, *args, **kwargs) -> RestResponse:
		try:
			_payload_list = [self.payload] if isinstance(self.payload, dict) else self.payload
			self._validate_api_input(CrudActions.update, inp=_payload_list, bulk=True)
			for _payload in _payload_list:
				if (_pk := _payload.get(self.pk_name)) is not None:
					del _payload[self.pk_name]
					self.service_class.update(pk=_pk, **_payload)
			return self.api_response.success()
		except Exception as e:
			return self.api_response.exception(e=e)

	@api_permissions(Permissions.Management, override=False)
	def delete(self, *args, **kwargs) -> RestResponse:
		try:
			_rule = DefaultRules.pk_validation_rule(self.pk_name)
			_pk = kwargs.get(self.pk_name)
			self._validate_api_input(CrudActions.delete, inp=kwargs, rule=_rule)
			self.service_class.delete(pk=_pk)
			return self.api_response.success()
		except Exception as e:
			return self.api_response.exception(e=e)

	@api_permissions(Permissions.Management, override=False)
	def bulk_delete(self, *args, **kwargs) -> RestResponse:
		try:
			_rule = DefaultRules.pk_validation_rule(self.pk_name)
			_payload = [self.payload] if isinstance(self.payload, dict) else self.payload
			self._validate_api_input(CrudActions.delete, inp=_payload, rule=_rule, bulk=True)
			for pk_details in _payload:
				_pk = pk_details.get(self.pk_name)
				self.service_class.delete(pk=_pk)
			return self.api_response.success()
		except Exception as e:
			return self.api_response.exception(e=e)

	@api_permissions(Permissions.Management, override=False)
	def search(self, *args, **kwargs):
		try:
			_rule = DefaultRules.search_validation_rule()
			self._validate_api_input(CrudActions.search, inp=self.payload, rule=_rule)

			_search_parameters = self.search_parameter_class(**self.payload)
			result = self.service_class.search(params=_search_parameters)
			return self.api_response.success(data=result)
		except Exception as e:
			return self.api_response.exception(e)
