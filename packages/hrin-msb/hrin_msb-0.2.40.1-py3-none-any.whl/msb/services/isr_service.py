from msb.dataclasses import Singleton
from msb.http import IntraServiceRequestFactory


class IntraServiceRequestService(IntraServiceRequestFactory, metaclass=Singleton):
	pass
