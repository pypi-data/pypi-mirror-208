from django.conf import settings
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from msb_auth.users import TokenUser
from msb_http import RequestWrapper
from .exceptions import MsbAuthExceptions


class JwtTokenValidator(JWTTokenUserAuthentication):
	"""
	This class overrides the "JWTTokenUserAuthentication", so that we can implement
	custom authentication rules over the default system

	"""

	_request: RequestWrapper = None

	def _validate_token_owner(self, token_user: TokenUser = None) -> bool:
		if settings.MSB_JWT_VERIFY_OWNER and not token_user.is_intra_service_requester:
			if self._request.ip in settings.MSB_JWT_TRUSTED_OWNERS:
				return True
			return f"{self._request.user_agent}@{self._request.ip}" == token_user.owner
		return True

	def _validate_subscription(self, token_user: TokenUser = None) -> bool:
		if settings.MSB_JWT_VERIFY_SUBSCRIPTIONS:
			_request_path = self._request.path.strip("/").split('/')[0]
			return token_user.has_access_to(path=_request_path)
		return True

	def _validate_environment(self, token_user: TokenUser = None) -> bool:
		if settings.MSB_JWT_VERIFY_ENVIRONMENT:
			return token_user.env.casefold() == settings.ENVIRONMENT.casefold()
		return True

	def authenticate(self, request):
		try:
			self._request = RequestWrapper(request=request)

			# authenticate the request from parent class
			if auth_result := super().authenticate(request=request):
				token_user: TokenUser = auth_result[0]

				# check if the token_user is authenticated
				if not token_user.is_authenticated:
					raise MsbAuthExceptions.AuthenticationFailed

				# check if the token belongs to the same environment as the current one
				if not self._validate_environment(token_user=token_user):
					raise MsbAuthExceptions.InvalidTokenEnvironment

				# check if the token owner is valid
				if not self._validate_token_owner(token_user=token_user):
					raise MsbAuthExceptions.InvalidTokenOwner

				# check if the user is subscribed to the service he is trying to access
				if not self._validate_subscription(token_user=token_user):
					raise MsbAuthExceptions.InvalidSubscriptionAccess

				# update the token user properties
				token_user.set_validation_status(True)

			# return the authentication result
			return auth_result
		except Exception as e:
			raise e
			return None
