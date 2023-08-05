# hrin-msb

## Pre-requisites for setup

1. `pip install poetry`

## How To Build

1. `poetry build`
2. `poetry config http-basic.pypi __token__ <access-token>`
3. `poetry publish`

# Change Log

### Version 0.1.1

***

### Version 0.1.2

***

### Version 0.1.3

***

1. Default serializer added to ApiView
2. fixed incorrect import in _validators.py
3. fixed msb_database_router
4. fixed Config.is_local_env() not working
5. moved devscripts -> devtools
6. File Utils Added to utils/files
7. "app_label" removed from "TestConfig" & "ApiTest" Classes
8. Fixed Bug : 'LoggingModelManager' object has no attribute '_queryset_class'
9. Fixed : Logging Model not showing any records
10. Fixed : str method for base model, & removed current_timestamp method from base model

***

## Version 0.1.4

1. Fixed : ModuleNotFoundError: No module named 'pdf2docx'
2. Renamed “FileGenerator“ => “FileFactory”,
3. Add `create_` Prefix in FileFactory methods
4. Renamed MsbMetaModel -> MsbModelMetaFields
5. Added validation decorators, and fixed bulk validation issuses
6. Modified Logging Configuration Files
7. removed utils package
8. moved msb_core.wrappers.exceptions -> msb_exceptions
9. Fixed : Base ApiViews and Crud Routes
10. Searchparameter class refactored, search method added in ApiService Class

***

## Version 0.1.41

1. Fixed: Crud operations not working with encrypted id's
2. Package dependencies updated
3. Validator test cases refactored

***

## Version 0.1.5x

### -- Version 0.1.51

1. dbrouter print statement removed
2. datetime constants renamed (added _FORMAT to all fof them)
3. Fixed the default argument in msb_exception which was causing "DESC :" to log even if desc was none
4. Api service create methdhod not working correctly
5. file logging handler is not registered in local env by default, we need to pass `emulate_prod=True` to add it
6. SearchParameter class imported in package.__init__.py
7. Fixed : test-cases are breaking because of logs databae
8. added base unittest class, and modified unit_test to inherit djangoTestCase instead of unittest
9. Added Validation Schema not defined exceptions
10. Fixed init_django_app error, int datatype instead of str while setting environement variable.
11. Added use_django decorator to use over classes/functions
12. Fixed : MsbMetaModel not working
13. MsbModel meta fields accessor added
14. Poetry dependencies updated
15. DMY_DATE_FORMAT added
16. versioning changed

### -- Version 0.1.52

1. Fixed : MsbMetaFields not working
2. Fixed : logging model lot of exceptions are thrown if table applicationlogs is not found
3. Fixed : logging model exceptions file not found
4. Fixed : db_migration throwing error if no migration dire is found
5. renamed use_djnago -> use_django, default value for settinfs_dir is added to "app"
6. renamend _query in msb_model to db_query
7. field_type, and label added to configuration model
8. unique_together constraint added to ConfigurationModel
9. class DjangoMigration creates migration folder if it doesn't exists
10. Added automatic fixture loading
11. Fixed : msb_model.__str__() was not able to read the primary key value
12. comma removed from msbMetamodels
13. Cipher now supports encryption/decryption of list items
14. SearchParameter modified to supoprt autmatic filter assignment
15. Refactor `msb_auth` : TokenUser,AuthResult,Constants added
16. Jwt Token Validation is strict now, it allows only same owner

### -- Version 0.1.521

1. Fixed improper import exception

### -- Version 0.1.522

1. Added Login Required to base viewset
2. Added Config Object class to msb_dataclasses
3. Added msb_http to the package
4. Added MsbDatabaseRouter in init.py
5. Fixed model.delete() is not working

### -- Version 0.1.611

1. Modified django migration script
2. Aded devtools to msb_ext
3. removed `use_django` decorator & added `requires_django` decorator
4. added default values for metafields
5. added InputFiled.time in validation schema types

### -- Version 0.2.0

1. Fixed Cipher.decrypt() returning bytes instead of str
2. Changed `SearchParameter` class implementation.
3. default offset & limit fixed in `SearchParameter` class

### -- Version 0.2.2

1. default values removed from model metafields
2. Fixed `ModuleNotFoundError: No module named '_asymmetric_cipher'`
3. Fixed fixtures loaded in wrong sequence
4. Feature `api_response.exception()` now sends back internal server error for undefined exceptions.
5. Fixed Token validation error
6. Added `DefaultJwtAuthSettings()` class, to unify settings across the services
7. Added automatic fixture loading for test cases.

### -- Version 0.2.3

1. msb_testing refactored
2. added new package `msb_const`
3. Optimized imports throughout
4. Refactored `msb_devtools`, removed `msb_ext.devtools`
5. `msb_devtools._exceptions` file removed
6. Added constant to `mab_auth._constants`

### -- Version 0.2.4

1. Refactor : (Optimized Imports,Sonarlint warnings)
2. Refactor : Moved msb_apis.wrappers -> msb_http

### -- Version 0.2.5

1. Refactor : removed `msb_ext`, as it served no purpose
2. Fixed : token validation failing due to AUD & ISS claim
3. Added default fixture paths to `msb_const.paths`

### -- Version 0.2.6

1. renamed the property `db_query` to `rows`, to make it easier to understand.
2. added a mentod to deteremine if the current environment is either dev or test env
3. CrudActions.all is now the default parameter value for `.as_view()` method.
4. Crud routes not working for single fields
5. Fixed `self.seriallizer` not working with `dict()`
6. Implemented `list` Api, to return predefined db columns
7. search parameter added in crud, searchparameters class refatored

### -- Version 0.2.7

1. Fixed : `_list_field_names` not working with properties & relations
2. Added `search_validation_rules` in DefaultRules

### -- Version 0.2.8

1. Fixed : list api breaking for foreign keys
2. Fixed : Search parameter not working with fields
3. Fixed: automatic encryption of db provate fields, now you need to put `DB_ENCRYPT_PRIVATE_FIELDS = True` to achieve that.

### -- Version 0.2.9

1. Fixed: automatic encryption of db primary key fields, now you need to put `DB_PK_IS_PRIVATE_FIELD = True` to achieve
   that.

### -- Version 0.2.10

1. Fixed : incorrect crud routes for [list,search]
2. Refactored : msb_http
3. Implemented : `MsbIntraServiceRequest` class
4. Implemented : `ApiRouter` class

### -- Version 0.2.11

1. Fixed /<str:id> route not working
2. Authentication is failing due to jwt-token owner mismatch

### -- Version 0.2.12

1. Fixed: Payload validation is failing for DELETE and UPDATE Request

### -- Version 0.2.13

1. Updated : dependencies
2. Fixed : crud list was breaking if no list fields are found/declared in model
3. Refactored : Added _list fields in ConfigurationModel

### -- Version 0.2.14

1. Fixed : env_setup->db_migration requires user input to run

### -- Version 0.2.15

1. Fixed : Crud list api is breaking with None

### -- Version 0.2.16

1. Refactored : owner verification in Jwt token can now be controlled through settings.py file, using following variables"
   `MSB_JWT_TRUSTED_OWNERS = []`(skips validation for the mentioned ip's) and `MSB_JWT_VERIFY_OWNER = False` (turns on/off
   the owner verification)
2. Implemented : `MsbIntraServiceRequest` class in msb_http
3. Update : `ApiService` now has `resource_name` attribute in the class, this helps in better exception messages from
   default crud operations.
4. Refactor : `MsbIntraServiceRequest`
5. Update : default crud api's now returns detailed error messages
6. Update : All api's now returns detailed error messages for any exceptions.

### -- Version 0.2.17

1. Update : `ApiService` now automatically takes the resource name if not provided.
2. Fixed : `MsbIntraServiceRequest` not working through api-gateway

### -- Version 0.2.18

1. Fixed : query parameters not working in `MsbIntraServiceRequest`
2. Fixed : search parameter query not working in `MsbIntraServiceRequest`
3. Fixed : limit and offset not working in list Api
4. Refactor: _dataclasses
5. Refactor : modified api_view error handler

### -- Version 0.2.19

1. removed Self parameter, due to compatibility issue
2. Fixed : list/retrieve api bug

### -- Version 0.2.2xx

1. Fixed : UserRole.__init__() got an unexpected keyword argument 'access_type'
2. Added: recover method in model
3. Refactor : moved all constants to `msb_constants`
