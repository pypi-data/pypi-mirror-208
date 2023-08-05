from functools import wraps

from rest_framework import (request as _request, decorators)

from msb_auth.users import TokenUser
from .exceptions import MsbAuthExceptions

require_permission = decorators.permission_classes
require_authentication = decorators.authentication_classes


def management_api(_func):
	@wraps(_func)
	def wrapper(klass, request: _request.Request, **kwargs):
		_user: TokenUser = request.user
		if not _user.has_management_access:
			raise MsbAuthExceptions.UnauthorizedAccess

		return _func(klass, request, **kwargs)

	return wrapper
