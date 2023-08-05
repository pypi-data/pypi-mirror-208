from typing import (List, Dict)

from msb.dataclasses import SearchParameterRequest, Singleton
from msb.env import (Config, MsbConfigNames, NameConst)
from .client import (ApiRequest)
from .dataclasses import (MsbApiResponse)


class IntraServiceRequest(ApiRequest):
	"""
	Mdified version of the request class to enable Intra Service requests.
	"""
	_service_name: str = 'IntraServiceRequest'

	def __init__(self, version: int = 1, **kwargs):
		_api_host = "{}/v{}".format(self.msb_intra_service_host, version)
		super(IntraServiceRequest, self).__init__(api_host=_api_host, **kwargs)
		self.set_authorization(token=self.msb_intra_service_request_token)

	@property
	def msb_intra_service_host(self) -> str:
		return Config.get(f"{self._service_name}_URL").as_str(default='')

	@property
	def msb_intra_service_request_token(self) -> str:
		return Config.get(MsbConfigNames.MSB_ISR_TOKEN).as_str(default='')

	def get_result(self) -> MsbApiResponse:
		return self._execute().as_msb_api_response()

	def retrieve(self, endpoint: str, pk: str | int = None) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).GET(query_params=[pk]).get_result()

	def list(self, endpoint: str, limit: int = -1, offset: int = 0) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).GET(query_params=dict(limit=limit, offset=offset)).get_result()

	def create(self, endpoint: str, data: [List | Dict] = None) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).POST(data=data).get_result()

	def search(self, endpoint: str, params: SearchParameterRequest) -> MsbApiResponse:
		return self.set_endpoint(endpoint=f"{endpoint.strip('/')}/search").POST(data=params.__dict__).get_result()

	def update(self, endpoint: str, pk: str | int = None, data: Dict = None) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).PUT(data=data, query_params=[pk]).get_result()

	def bulk_update(self, endpoint: str, data: List[Dict] = None) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).PUT(data=data).get_result()

	def delete(self, endpoint: str, pk: str | int = None) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).DELETE(query_params=[pk]).get_result()

	def bulk_delete(self, endpoint: str, data: List[Dict]) -> MsbApiResponse:
		return self.set_endpoint(endpoint=endpoint).DELETE(data=data).get_result()


class UserServiceApiRequest(IntraServiceRequest, metaclass=Singleton):
	"""
	User Service Api Request Class
	"""

	_service_name = NameConst.USER_SERVICE_NAME


class EmployeeServiceApiRequest(IntraServiceRequest, metaclass=Singleton):
	"""
	Employee Service Api Request Class
	"""
	_service_name = NameConst.EMPLOYEE_SERVICE_NAME


class LeaveServiceApiRequest(IntraServiceRequest, metaclass=Singleton):
	"""
	Leave Service Api Request Class
	"""
	_service_name = NameConst.LEAVE_SERVICE_NAME


class ProjectServiceApiRequest(IntraServiceRequest, metaclass=Singleton):
	"""
	Project Service Api Request Class
	"""

	_service_name = NameConst.PROJECT_SERVICE_NAME


class AutoPilotServiceApiRequest(IntraServiceRequest, metaclass=Singleton):
	"""
	Autopilot Service Api Request Class
	"""
	_service_name = NameConst.AUTOPILOT_SERVICE_NAME


class NotificationServiceApiRequest(IntraServiceRequest, metaclass=Singleton):
	"""
	Notification Service Api Request Class
	"""
	_service_name = NameConst.NOTIFICATION_SERVICE_NAME


class IntraServiceRequestFactory(object):
	"""
	Intra Service Request Factory
	"""

	@staticmethod
	def get_intra_service_request(version: int = 1, **kwargs) -> IntraServiceRequest:
		return IntraServiceRequest(version=version, **kwargs)

	@staticmethod
	def get_user_service_api(version: int = 1, **kwargs) -> UserServiceApiRequest:
		return UserServiceApiRequest(version=version, **kwargs)

	@staticmethod
	def get_employee_service_api(version: int = 1, **kwargs) -> EmployeeServiceApiRequest:
		return EmployeeServiceApiRequest(version=version, **kwargs)

	@staticmethod
	def get_leave_service_api(version: int = 1, **kwargs) -> LeaveServiceApiRequest:
		return LeaveServiceApiRequest(version=version, **kwargs)

	@staticmethod
	def get_project_service_api(version: int = 1, **kwargs) -> ProjectServiceApiRequest:
		return ProjectServiceApiRequest(version=version, **kwargs)

	@staticmethod
	def get_autopilot_service_api(version: int = 1, **kwargs) -> AutoPilotServiceApiRequest:
		return AutoPilotServiceApiRequest(version=version, **kwargs)

	@staticmethod
	def get_notification_service_api(version: int = 1, **kwargs) -> NotificationServiceApiRequest:
		return NotificationServiceApiRequest(version=version, **kwargs)


__all__ = [  # noqa: WPS410
	'IntraServiceRequestFactory',
]
