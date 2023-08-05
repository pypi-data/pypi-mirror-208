class AuthResult:
	auth_type: str = None
	userid: str
	username: str
	email: str

	def __getitem__(self, item):
		return self.auth_data.get(item)

	def __init__(self, auth_username: str, auth_userid: str | int, email=None, auth_type: str = None, **kwargs):
		self.userid = auth_userid
		self.username = auth_username
		self.email = email
		self.auth_type = auth_type

	@property
	def id(self):
		return self.userid

	@property
	def user(self):
		return self.id

	@property
	def is_authenticated(self) -> bool:
		return (self.username is not None and self.userid is not None)

	@property
	def auth_data(self):
		_auth_data = dict()
		_auth_data['auth_type'] = self.auth_type
		_auth_data['userid'] = self.id
		_auth_data['username'] = self.username
		_auth_data['is_authenticated'] = self.is_authenticated
		return _auth_data

	def set_auth_type(self, auth_type: str):
		self.auth_type = auth_type
		return self

	def set_userid(self, userid: str):
		self.userid = userid
		return self

	def set_username(self, username: str):
		self.username = username
		return self

	def set_email(self, email: str):
		self.email = email
		return self
