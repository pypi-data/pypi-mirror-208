# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['msb',
 'msb.apis',
 'msb.auth',
 'msb.cipher',
 'msb.dataclasses',
 'msb.datetime',
 'msb.db',
 'msb.devtools',
 'msb.env',
 'msb.exceptions',
 'msb.files',
 'msb.http',
 'msb.logging',
 'msb.services',
 'msb.testing',
 'msb.validation']

package_data = \
{'': ['*']}

modules = \
['hrin_msb']
install_requires = \
['cerberus>=1.3.4,<2.0.0',
 'cffi>=1.15.1,<2.0.0',
 'cryptography>=38.0.3,<39.0.0',
 'django>=4.1.3,<5.0.0',
 'djangorestframework-simplejwt>=5.2.2,<6.0.0',
 'djangorestframework>=3.14.0,<4.0.0',
 'pandas>=1.5.1,<2.0.0',
 'pdf2docx>=0.5.6,<0.6.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.21.0,<0.22.0',
 'requests>=2.28.1,<3.0.0',
 'xhtml2pdf>=0.2.8,<0.3.0']

setup_kwargs = {
    'name': 'hrin-msb',
    'version': '0.2.48',
    'description': '',
    'long_description': '# hrin-msb\n\n## Pre-requisites for setup\n\n1. `pip install poetry`\n\n## How To Build\n\n1. `poetry build`\n2. `poetry config http-basic.pypi __token__ <access-token>`\n3. `poetry publish`\n\n# Change Log\n\n### Version 0.1.1\n\n***\n\n### Version 0.1.2\n\n***\n\n### Version 0.1.3\n\n***\n\n1. Default serializer added to ApiView\n2. fixed incorrect import in _validators.py\n3. fixed msb_database_router\n4. fixed Config.is_local_env() not working\n5. moved devscripts -> devtools\n6. File Utils Added to utils/files\n7. "app_label" removed from "TestConfig" & "ApiTest" Classes\n8. Fixed Bug : \'LoggingModelManager\' object has no attribute \'_queryset_class\'\n9. Fixed : Logging Model not showing any records\n10. Fixed : str method for base model, & removed current_timestamp method from base model\n\n***\n\n## Version 0.1.4\n\n1. Fixed : ModuleNotFoundError: No module named \'pdf2docx\'\n2. Renamed “FileGenerator“ => “FileFactory”,\n3. Add `create_` Prefix in FileFactory methods\n4. Renamed MsbMetaModel -> MsbModelMetaFields\n5. Added validation decorators, and fixed bulk validation issuses\n6. Modified Logging Configuration Files\n7. removed utils package\n8. moved msb_core.wrappers.exceptions -> msb_exceptions\n9. Fixed : Base ApiViews and Crud Routes\n10. Searchparameter class refactored, search method added in ApiService Class\n\n***\n\n## Version 0.1.41\n\n1. Fixed: Crud operations not working with encrypted id\'s\n2. Package dependencies updated\n3. Validator test cases refactored\n\n***\n\n## Version 0.1.5x\n\n### -- Version 0.1.51\n\n1. dbrouter print statement removed\n2. datetime constants renamed (added _FORMAT to all fof them)\n3. Fixed the default argument in msb_exception which was causing "DESC :" to log even if desc was none\n4. Api service create methdhod not working correctly\n5. file logging handler is not registered in local env by default, we need to pass `emulate_prod=True` to add it\n6. SearchParameter class imported in package.__init__.py\n7. Fixed : test-cases are breaking because of logs databae\n8. added base unittest class, and modified unit_test to inherit djangoTestCase instead of unittest\n9. Added Validation Schema not defined exceptions\n10. Fixed init_django_app error, int datatype instead of str while setting environement variable.\n11. Added use_django decorator to use over classes/functions\n12. Fixed : MsbMetaModel not working\n13. MsbModel meta fields accessor added\n14. Poetry dependencies updated\n15. DMY_DATE_FORMAT added\n16. versioning changed\n\n### -- Version 0.1.52\n\n1. Fixed : MsbMetaFields not working\n2. Fixed : logging model lot of exceptions are thrown if table applicationlogs is not found\n3. Fixed : logging model exceptions file not found\n4. Fixed : db_migration throwing error if no migration dire is found\n5. renamed use_djnago -> use_django, default value for settinfs_dir is added to "app"\n6. renamend _query in msb_model to db_query\n7. field_type, and label added to configuration model\n8. unique_together constraint added to ConfigurationModel\n9. class DjangoMigration creates migration folder if it doesn\'t exists\n10. Added automatic fixture loading\n11. Fixed : msb_model.__str__() was not able to read the primary key value\n12. comma removed from msbMetamodels\n13. Cipher now supports encryption/decryption of list items\n14. SearchParameter modified to supoprt autmatic filter assignment\n15. Refactor `msb_auth` : TokenUser,AuthResult,Constants added\n16. Jwt Token Validation is strict now, it allows only same owner\n\n### -- Version 0.1.521\n\n1. Fixed improper import exception\n\n### -- Version 0.1.522\n\n1. Added Login Required to base viewset\n2. Added Config Object class to msb_dataclasses\n3. Added msb_http to the package\n4. Added MsbDatabaseRouter in init.py\n5. Fixed model.delete() is not working\n\n### -- Version 0.1.611\n\n1. Modified django migration script\n2. Aded devtools to msb_ext\n3. removed `use_django` decorator & added `requires_django` decorator\n4. added default values for metafields\n5. added InputFiled.time in validation schema types\n\n### -- Version 0.2.0\n\n1. Fixed Cipher.decrypt() returning bytes instead of str\n2. Changed `SearchParameter` class implementation.\n3. default offset & limit fixed in `SearchParameter` class\n\n### -- Version 0.2.2\n\n1. default values removed from model metafields\n2. Fixed `ModuleNotFoundError: No module named \'_asymmetric_cipher\'`\n3. Fixed fixtures loaded in wrong sequence\n4. Feature `api_response.exception()` now sends back internal server error for undefined exceptions.\n5. Fixed Token validation error\n6. Added `DefaultJwtAuthSettings()` class, to unify settings across the services\n7. Added automatic fixture loading for test cases.\n\n### -- Version 0.2.3\n\n1. msb_testing refactored\n2. added new package `msb_const`\n3. Optimized imports throughout\n4. Refactored `msb_devtools`, removed `msb_ext.devtools`\n5. `msb_devtools._exceptions` file removed\n6. Added constant to `mab_auth._constants`\n\n### -- Version 0.2.4\n\n1. Refactor : (Optimized Imports,Sonarlint warnings)\n2. Refactor : Moved msb_apis.wrappers -> msb_http\n\n### -- Version 0.2.5\n\n1. Refactor : removed `msb_ext`, as it served no purpose\n2. Fixed : token validation failing due to AUD & ISS claim\n3. Added default fixture paths to `msb_const.paths`\n\n### -- Version 0.2.6\n\n1. renamed the property `db_query` to `rows`, to make it easier to understand.\n2. added a mentod to deteremine if the current environment is either dev or test env\n3. CrudActions.all is now the default parameter value for `.as_view()` method.\n4. Crud routes not working for single fields\n5. Fixed `self.seriallizer` not working with `dict()`\n6. Implemented `list` Api, to return predefined db columns\n7. search parameter added in crud, searchparameters class refatored\n\n### -- Version 0.2.7\n\n1. Fixed : `_list_field_names` not working with properties & relations\n2. Added `search_validation_rules` in DefaultRules\n\n### -- Version 0.2.8\n\n1. Fixed : list api breaking for foreign keys\n2. Fixed : Search parameter not working with fields\n3. Fixed: automatic encryption of db provate fields, now you need to put `DB_ENCRYPT_PRIVATE_FIELDS = True` to achieve that.\n\n### -- Version 0.2.9\n\n1. Fixed: automatic encryption of db primary key fields, now you need to put `DB_PK_IS_PRIVATE_FIELD = True` to achieve\n   that.\n\n### -- Version 0.2.10\n\n1. Fixed : incorrect crud routes for [list,search]\n2. Refactored : msb_http\n3. Implemented : `MsbIntraServiceRequest` class\n4. Implemented : `ApiRouter` class\n\n### -- Version 0.2.11\n\n1. Fixed /<str:id> route not working\n2. Authentication is failing due to jwt-token owner mismatch\n\n### -- Version 0.2.12\n\n1. Fixed: Payload validation is failing for DELETE and UPDATE Request\n\n### -- Version 0.2.13\n\n1. Updated : dependencies\n2. Fixed : crud list was breaking if no list fields are found/declared in model\n3. Refactored : Added _list fields in ConfigurationModel\n\n### -- Version 0.2.14\n\n1. Fixed : env_setup->db_migration requires user input to run\n\n### -- Version 0.2.15\n\n1. Fixed : Crud list api is breaking with None\n\n### -- Version 0.2.16\n\n1. Refactored : owner verification in Jwt token can now be controlled through settings.py file, using following variables"\n   `MSB_JWT_TRUSTED_OWNERS = []`(skips validation for the mentioned ip\'s) and `MSB_JWT_VERIFY_OWNER = False` (turns on/off\n   the owner verification)\n2. Implemented : `MsbIntraServiceRequest` class in msb_http\n3. Update : `ApiService` now has `resource_name` attribute in the class, this helps in better exception messages from\n   default crud operations.\n4. Refactor : `MsbIntraServiceRequest`\n5. Update : default crud api\'s now returns detailed error messages\n6. Update : All api\'s now returns detailed error messages for any exceptions.\n\n### -- Version 0.2.17\n\n1. Update : `ApiService` now automatically takes the resource name if not provided.\n2. Fixed : `MsbIntraServiceRequest` not working through api-gateway\n\n### -- Version 0.2.18\n\n1. Fixed : query parameters not working in `MsbIntraServiceRequest`\n2. Fixed : search parameter query not working in `MsbIntraServiceRequest`\n3. Fixed : limit and offset not working in list Api\n4. Refactor: _dataclasses\n5. Refactor : modified api_view error handler\n\n### -- Version 0.2.19\n\n1. removed Self parameter, due to compatibility issue\n2. Fixed : list/retrieve api bug\n\n### -- Version 0.2.2xx\n\n1. Fixed : UserRole.__init__() got an unexpected keyword argument \'access_type\'\n2. Added: recover method in model\n3. Refactor : moved all constants to `msb_constants`\n',
    'author': 'Prakash Mishra',
    'author_email': 'prakash.mishra@intimetec.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
