from django.test import LiveServerTestCase

from .core import (LiveServerThreadWithReuse, TestConfig, const)


class UnitTestConfig(TestConfig):
	pass


class UnitTest(LiveServerTestCase, UnitTestConfig):
	databases = const.DEFAULT_TEST_DATABASES
	port = const.DEFAULT_TEST_SERVER_PORT
	server_thread_class = LiveServerThreadWithReuse

	def __init__(self, *args, **kwargs):
		LiveServerTestCase.__init__(self, *args, **kwargs)
		UnitTestConfig.__init__(self)
