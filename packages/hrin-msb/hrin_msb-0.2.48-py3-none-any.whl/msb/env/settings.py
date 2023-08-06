import os
import sys

from msb.auth.defaults import DefaultJwtAuthSettings, DefaultJwtConfig
from msb.env import (Config, PathConst, EnvDefaults)
from msb.logging import LogConfig

sys.path.extend(PathConst.SYS_PATH_LIST)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = PathConst.BASE_DIR_PATH

# load configuration from env file
Config.load(env_path=BASE_DIR.__str__(), main_file='.env', local_file='.env.local', )

# Enviroment name
ENVIRONMENT = Config.get('ENVIROMENT').as_str()

# directory where logs will be created
LOGS_DIR = PathConst.LOGS_DIR_PATH

# path where resources are stored
RESOURCE_DIR = PathConst.RESOURCE_DIR_PATH

# path where application will write
WRITABLE_DIR = PathConst.WRITABLE_DIR_PATH

# path where resources are stored
UNITTEST_DATA_DIR = PathConst.TEST_DATA_DIR_PATH

# path where fixtures are stored
FIXTURE_DIRS = PathConst.FIXTURE_DIRS_LIST

# IS DEVELOPEMENT ENVIRONEMR
IS_LOCAL_ENVIRONMENT = Config.is_local_env()

# initailze the default logging configuration
LogConfig.init_default_config(LOGS_DIR, emulate_prod=True)

"""
CORE DJANGO SETTINGS
"""

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = Config.get("SECRET_KEY").as_str(default='')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = Config.get('DEBUG').as_bool(default=False)

ALLOWED_HOSTS = Config.get('ALLOWED_HOSTS').as_list(default=['*'])

"""
BASE PATH & URL CONFIGURATIONS
"""
# allow admin url
ALLOW_ADMIN_URL = Config.get('ALLOW_ADMIN_URL').as_bool(default=False)

# path to access the admin interface
ADMIN_URL_PATH = Config.get('ADMIN_URL_PATH').as_str(default=None)

APPEND_SLASH = Config.get('APPEND_SLASH').as_bool(default=False)

# common application url
BASE_URL = Config.get('BASE_URL').as_str(default='/')

# installed apps
INSTALLED_APPS = [
	'django.contrib.staticfiles',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'corsheaders',
	'rest_framework',
	'rest_framework_simplejwt',
]

# Application definition
MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Templates Configurations
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.backends.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.backends.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.backends.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.backends.password_validation.NumericPasswordValidator',
	},
]

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'app.wsgi.application'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = False

"""
SECURITY CONFIGURATIONS
"""

# Secure csrf cookie
CSRF_COOKIE_SECURE = EnvDefaults.CSRF_COOKIE_SECURE

# Secure session cookie
SESSION_COOKIE_SECURE = EnvDefaults.SESSION_COOKIE_SECURE

# make csrf cokkied http only
CSRF_COOKIE_HTTPONLY = EnvDefaults.CSRF_COOKIE_HTTPONLY

# make csrf cokkied http only
SESSION_COOKIE_HTTPONLY = EnvDefaults.SESSION_COOKIE_HTTPONLY

# secure the ssl redirect
SECURE_SSL_REDIRECT = Config.get('SECURE_SSL_REDIRECT').as_bool(default=False)

# domain for which the session cookie is valid
SESSION_COOKIE_DOMAIN = Config.get('SESSION_COOKIE_DOMAIN').as_str(default='127.0.0.1')

# allow all origins to make requests
CORS_ALLOW_ALL_ORIGINS = Config.get('CORS_ALLOW_ALL_ORIGINS').as_bool(default=True)

# allowed origins
CORS_ALLOWED_ORIGINS = Config.get('CORS_ALLOWED_ORIGINS').as_list()

CORS_ALLOW_METHODS = EnvDefaults.CORS_ALLOW_METHODS

CORS_ALLOW_HEADERS = EnvDefaults.CORS_ALLOW_HEADERS

CORS_PREFLIGHT_MAX_AGE = EnvDefaults.CORS_PREFLIGHT_MAX_AGE

CORS_ALLOW_CREDENTIALS = EnvDefaults.CORS_ALLOW_CREDENTIALS

ALLOW_API_DOCUMENTATION = Config.get("ALLOW_API_DOCUMENTATION").as_bool(default=False)

"""
DJANGO REST FRAMEWORK CONFIGURATIONS
:see https://www.django-rest-framework.org/api-guide/settings/ for details.
"""
REST_FRAMEWORK = dict()
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = "rest_framework.pagination.PageNumberPagination"
REST_FRAMEWORK["PAGE_SIZE"] = 10
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = ('rest_framework.permissions.IsAuthenticated',)
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ["rest_framework.renderers.JSONRenderer", ]
REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = 'json'

if Config.is_local_env():
	REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += ["rest_framework.renderers.BrowsableAPIRenderer"]

JWT_AUTH_CONFIG = DefaultJwtAuthSettings(
	signing_key=Config.get("JWT_TOKEN_SIGNING_KEY").as_str(default=''),
	verifying_key=Config.get("JWT_TOKEN_VERIFY_KEY").as_str(default=''),
	access_token_lifetime=Config.get("JWT_ACCESS_TOKEN_VALIDITY").as_int(default=DefaultJwtConfig.access_token_lifetime),
	refresh_token_lifetime=Config.get("JWT_ACCESS_TOKEN_VALIDITY").as_int(default=DefaultJwtConfig.refresh_token_lifetime),
)

# default classes that will authenticate all requests
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = JWT_AUTH_CONFIG.authentication_classes

# load meme-type configuration
import mimetypes

mimetypes.add_type("text/css", ".css", True)

"""
CELERY CONFIGURATIONS
"""
# Message Broker settings.
CELERY_BROKER_URL = Config.get('CELERY_BROKER_URL').as_str()
# List of modules to import when celery starts.
CELERY_IMPORTS = []
# Using the database to store task state and results.
CELERY_RESULT_BACKEND = Config.get('CELERY_RESULT_BACKEND').as_str()
CELERY_RESULT_EXTENDED = True
# Format in which the tasks are stored
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

"""
MSB CONFIGURATIONS
"""
MSB_DB_ENCRYPT_PRIVATE_FIELDS = EnvDefaults.MSB_DB_ENCRYPT_PRIVATE_FIELDS
MSB_DB_PK_IS_PRIVATE_FIELD = EnvDefaults.MSB_DB_PK_IS_PRIVATE_FIELD
MSB_JWT_TRUSTED_OWNERS = EnvDefaults.MSB_JWT_TRUSTED_OWNERS
MSB_JWT_VERIFY_OWNER = EnvDefaults.MSB_JWT_VERIFY_OWNER
MSB_JWT_VERIFY_SUBSCRIPTIONS = EnvDefaults.MSB_JWT_VERIFY_SUBSCRIPTIONS
MSB_JWT_VERIFY_ENVIRONMENT = EnvDefaults.MSB_JWT_VERIFY_ENVIRONMENT
