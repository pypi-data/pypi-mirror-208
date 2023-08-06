def singleton(class_):
	instances = {}

	def getinstance(*args, **kwargs):
		if class_ not in instances:
			instances[class_] = class_(*args, **kwargs)
		return instances[class_]

	return getinstance


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class VirtualDataClass:
	__fields: dict = dict()
	_request_data: dict = dict()
	_resource_function = None

	@property
	def fields(self) -> dict:
		return self.__fields

	def get(self, key, cast_to: any = str) -> any:
		self._fetch_virtual_data()
		return cast_to(self.__fields.get(key))

	def _fetch_virtual_data(self):
		if len(self.__fields.keys()) > 0:
			return
		if callable(self._resource_function):
			self.__fields = self._resource_function(data=self._request_data)
