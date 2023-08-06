import os


class EmailConfigData(object):
	_smtp_host: str = 'localhost'
	_smtp_port: int = 25
	_smtp_user: str = ''
	_smtp_password: str = ''
	_smtp_use_tls: bool = False
	_smtp_use_ssl: bool = False
	_smtp_timeout: int = 0
	_smtp_ssl_keyfile: str = ''
	_smtp_ssl_certfile: str = ''

	def __init__(self, namespace=None):
		namespace = str(namespace).upper()
		self._smtp_host = os.environ.get(f'{namespace}_SMTP_HOST', default='')
		self._smtp_port = os.environ.get(f'{namespace}_SMTP_PORT', default='')
		self._smtp_username = os.environ.get(f'{namespace}_SMTP_USER', default='')
		self._smtp_password = os.environ.get(f'{namespace}_SMTP_PASSWORD', default='')
		self._smtp_use_tls = (int(os.environ.get(f'{namespace}_SMTP_USE_TLS', default=0)) == 1)
		self._smtp_use_ssl = (int(os.environ.get(f'{namespace}_SMTP_USE_SMTP', default=0)) == 1)
		self._smtp_timeout = int(os.environ.get(f'{namespace}_SMTP_TIMEOUT', default=30))
		self._smtp_ssl_keyfile = os.environ.get(f'{namespace}_SMTP_SSL_KEY_FILE', default=None)
		self._smtp_ssl_certfile = os.environ.get(f'{namespace}_SMTP_SSL_CERTIFICATE', default=None)

	def __str__(self):
		return str(self.__dict__)

	@property
	def host(self):
		return self._smtp_host

	@property
	def port(self):
		return self._smtp_port

	@property
	def user(self):
		return self._smtp_user

	@property
	def password(self):
		return self._smtp_password

	@property
	def timeout(self):
		return self._smtp_timeout

	@property
	def use_ssl(self):
		return self._smtp_use_ssl

	@property
	def use_tls(self):
		return self._smtp_use_tls

	@property
	def ssl_key(self):
		return self._smtp_ssl_keyfile

	@property
	def ssl_cert(self):
		return self._smtp_ssl_certfile


class EmailConfig():
	__config = dict()

	def __init__(self, *namespace_list):
		for namespace in namespace_list:
			self.__config[str(namespace).lower()] = EmailConfigData(namespace=namespace)

	def get(self, namespace: str = 'default') -> EmailConfigData:
		return self.__config.get(namespace.lower())
