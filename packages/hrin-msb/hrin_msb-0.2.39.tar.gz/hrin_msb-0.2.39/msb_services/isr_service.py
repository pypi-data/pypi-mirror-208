from msb_dataclasses import Singleton
from msb_http import IntraServiceRequestFactory


class IntraServiceRequestService(IntraServiceRequestFactory, metaclass=Singleton):
	pass
