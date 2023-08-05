# nexus-utilities<!-- omit in toc -->
This package is meant to hold various useful utilities for functionality I find myself using across multiple projects.  I will try to keep this documentation updated as I expand the toolkit.  Feel free to use these if you find them valuable and I welcome any feedback.

## Table of Contents <!-- omit in toc -->

- [Installation](#installation)
- [config\_utils.py](#config_utilspy)
  - [**read\_config\_file(config\_filepath)**](#read_config_fileconfig_filepath)
- [database\_utils.py](#database_utilspy)
  - [**build\_engine(connect\_type, server\_address, server\_port, server\_name, user\_name, password, schema=None)**](#build_engineconnect_type-server_address-server_port-server_name-user_name-password-schemanone)
  - [**clean\_sql\_statement(sql\_statement)**](#clean_sql_statementsql_statement)
- [datetime\_utils.py](#datetime_utilspy)
  - [**get\_current\_timestamp()**](#get_current_timestamp)
  - [**getDuration(then, now=datetime.datetime.now())**](#getdurationthen-nowdatetimedatetimenow)
- [package\_utils.py](#package_utilspy)
  - [**add\_package\_to\_path()**](#add_package_to_path)
  - [**import\_relative(package\_root\_name, module\_path, import\_name, alias=None)**](#import_relativepackage_root_name-module_path-import_name-aliasnone)
- [password\_utils.py](#password_utilspy)
  - [**get\_password(password\_method, password\_key, account\_name=None, access\_key=None, secret\_key=None, endpoint\_url=None, region\_name=None, password\_path=None, encoding='utf-8')**](#get_passwordpassword_method-password_key-account_namenone-access_keynone-secret_keynone-endpoint_urlnone-region_namenone-password_pathnone-encodingutf-8)
- [string\_utils.py](#string_utilspy)
  - [**cleanse\_string(string, remove\_symbols=True, title\_to\_snake\_case=False, hyphen\_to\_underscore=True, period\_to\_underscore=True, to\_upper=False, to\_lower=True)**](#cleanse_stringstring-remove_symbolstrue-title_to_snake_casefalse-hyphen_to_underscoretrue-period_to_underscoretrue-to_upperfalse-to_lowertrue)
- [About the Author](#about-the-author)

---

## Installation

```python
pip3 install nexus-utilities
```

After installation, use "import nexus_utils" to access the various functions.

---

## config_utils.py

This module contains functions for working with configuration files.  Currently limited to using configparser to read .ini files.

### **read_config_file(config_filepath)**

Arguments:
 * ***config_filepath (str):*** File path to the .ini file to be read

Returns:
 * ***config (ConfigParser Class):*** ConfigParser Class containing the read configuration data

Takes a path to a specific .ini file and reads it.  Will also check if there is a "_local" version and uses that instead if found.  Eg. if you pass in "/path/to/file/database_config.ini", it will check for the presence of "/path/to/file/database_config_local.ini" and use it instead

---

## database_utils.py

This module contains functions for working with databases and related functions.

### **build_engine(connect_type, server_address, server_port, server_name, user_name, password, schema=None)**

Arguments:
 * ***connect_type (str):*** SQLAlchemy connection type, Eg. "postgresql" or "postgresql+psycopg2"
 * ***server_address (str):*** Database server address
 * ***server_port (str):*** Database port
 * ***server_name (str):*** Database name
 * ***user_name (str):*** Username
 * ***password (str):*** Password
 * ***schema (str):*** Default database schema (optional)

Returns:
 * ***engine (sqlalchemy.engine.Engine Class):*** SQLAlchemy Engine Class for interacting with the database

Creates a SQLAlchemy Engine Class object for interacting with your database.

### **clean_sql_statement(sql_statement)**

Arguments:
 * ***sql_statement (str):*** SQL script to be cleansed

Returns:
 * ***sql_statements_output (list):*** List of cleansed SQL statements in the order they appeared in the provided script

The primary purpose of this function is to remove comments from a SQL script.  Any lines prefixed with "--" and all text surrounded by "/*" and "*/" will be removed.  Will also separate each distinct statement in the script to its own list item for iterating though.

---

## datetime_utils.py

This module contains functions for working with dates and times.

### **get_current_timestamp()**

Arguments:
 * None

Returns:
 * ***current_timestamp (datetime Class):*** Datetime Class object - Used for difference calculations
 * ***filename_timestamp (str):*** Timestamp string formated 'YYYY-MM-DD_HHMMSS' - Used for filenames
 * ***log_timestamp (str):*** Timestamp string formated 'YYYY-MM-DD HH:MM:SS' - Used for logs

Calculates the current time in UTC timezone and returns 3 variations to be used for different purposes.

### **getDuration(then, now=datetime.datetime.now())**

Arguments:
 * ***then (datetime Class):*** Datetime Class object representing the lower limit of a time comparison
 * ***now (datetime Class):*** Datetime Class object representing the upper limit of a time comparison

Returns:
 * ***days_between (int):*** Days between two timestamps
 * ***hours_between (int):*** Hours between two timestamps
 * ***minutes_between (int):*** Minutes between two timestamps
 * ***seconds_between (int):*** Seconds between two timestamps
 * ***duration_string (str):*** String representation of difference between two timestamps

Calculates the difference between two timestamps.  Provides absolute number of total days, hours, minutes, and seconds, as well as a string representation of the normalized difference, Eg. "5 days, 4 hours, 3 minutes, 2 seconds" or "32 seconds"

---

## package_utils.py

This module contains functions for working with Python packages.

### **add_package_to_path()**

Arguments:
 * None

Returns:
 * ***package_root_dir (str):***  Full path leading up to the parent-level package folder
 * ***package_root_name (str):***  Name of the parent-level package folder

Programmatically determines the most likely root folder of the current running program, adds the parent folder to the system PATH, and returns the root folder name.  This can be helpful for resolving package-relative paths, particularly for programs with multiple possible entry points.  It achieves this by starting from the current working directory, and traversing upwards, counting the instances of the below files and folders:

```python
["src", "tests", "templates", "docs", "dist", "build", "readme.md", "license.txt", ".gitignore", "pyproject.toml", "requirements.txt", "poetry.lock", "setup.py", "manifest.in", ".editorconfig"]
```

In the case of a tie, it takes the folder deeper into the path.  The returned "package_root_name" is meant to be used with the "import_relative()" function below, while the "package_root_dir" can be useful for dertermining absolute-paths relative to the application.

### **import_relative(package_root_name, module_path, import_name, alias=None)**

Example:  
***/app/flat_file_loader/src/utils/config_reader.py***

***import_relative('flat_file_loader', 'src.utils', 'config_reader', alias='cr')***

Arguments:
 * ***package_root_name (str):*** Folder name of package root folder.  Meant to be used with the output of the "add_package_to_path()" function
 * ***module_path (str):*** Dot-separated path from the package root to the library to be imported
 * ***import_name (str):*** Name of the object to be imported.  Can be a ".py" file name, or a function within a ".py" file (in the latter case, make sure the ".py" file name is part of the "module_path" above)
* ***alias (str):*** Optional alias for the imported library or function

Allows for importing package-relative libraries or functions given a programmatically-determined package root folder.  Useful for programs with multiple entry points and utilities called from multiple libraries.

***Important note: Pylance will show an error since the imports are done at runtime.  These can be avoided by attaching "# type: ignore" to any line using one of these relative imports.***

---

## password_utils.py

This module contains functions for working with passwords and other sensitive information.

### **get_password(password_method, password_key, account_name=None, access_key=None, secret_key=None, endpoint_url=None, region_name=None, password_path=None, encoding='utf-8')**

Arguments:
 * ***password_method (str):*** Desired password method.  Options include:
     * keyring:  Use the "keyring" python library
     * ssm:  Use the AWS Parameter Store method
     * secretsmanager:  Use the AWS Secrets Manager method
 * ***password_key (str):*** Unique identifier of the password or secret
 * ***account_name (str):*** Account name associated with the password (primarily used by keyring)
 * ***access_key (str):*** AWS access key
 * ***secret_key (str):*** AWS secret key
 * ***endpoint_url (str):*** AWS endpoint url
 * ***region_name (str):*** AWS region name
 * ***password_path (str):*** AWS path to secret (primarily used by AWS Parameter Store)
 * ***encoding (str):*** Password encoding.  Supports the following, but uses utf-8 as the default: 'utf-8', 'ascii', 'latin-1', 'utf-16'

Returns:
 * ***secret_value (str):*** Secret in plain text

Allows multiple methods of retrieving sensitive information.

Note:  If you prefer to use environment variables instead of passing the sensitive information directly, you can use the below.  They will be used in place of the function arguments when present:

```python
AWS Parameter Store:
access_key = 'AWS_SSM_ACCESS_KEY_ID'
secret_key = 'AWS_SSM_SECRETACCESS_KEY_ID'
endpoint_url = 'AWS_SSM_ENDPOINT_URL'
region_name = 'AWS_SSM_REGION_NAME'
password_path = 'AWS_SSM_PASSWORD_PATH'

AWS Secrets Manager:
access_key = 'AWS_SM_SECRET_ACCESS_KEY'
secret_key = 'AWS_SM_ACCESS_KEY_ID'
endpoint_url = 'AWS_SM_ENDPOINT_URL'
region_name = 'AWS_SM_REGION_NAME'
password_key = 'AWS_SM_PASSWORD_KEY'
```

---

## string_utils.py

This module contains functions for working with strings.

### **cleanse_string(string, remove_symbols=True, title_to_snake_case=False, hyphen_to_underscore=True, period_to_underscore=True, to_upper=False, to_lower=True)**

Arguments:
 * ***string (str):*** String to be cleansed
 * ***remove_symbols (bool):*** Remove some symbols, and replace others with "_"
 * ***title_to_snake_case (bool):*** Convert TitleCase to Snake_Case
 * ***hyphen_to_underscore (bool):*** Change hypehens to underscores
 * ***period_to_underscore (bool):*** Change periods to underscores
 * ***to_upper (bool):*** Change string to uppercase
 * ***to_lower (bool):*** Change string to lowercase

Returns:
 * ***string (str):*** Transformed string value

Below is additional details about what each transformation does:
 * ***remove_symbols*** - Removes or converts to "_" based on the below rules.  Will also attempt to preserve multiple underscores in the original field without adding to them (using the '†' symbol).  Eg. "Field__(Name)" will become "Field__Name", not "Field___Name"
     * characters_to_replace_with_underscore  
' ', ':', ';', '&', '@', '^', '+', '=', '~', '/', '\\', '|', '(', '{', '[', '<'
     * characters_to_remove  
',', '`', '#', '$', '%', '*', ''', '"', '?', '!', ')', '}', ']', '>'
 * ***title_to_snake_case*** - Convert TitleCase to SnakeCase.  Attempts to account for clusters of uppercase letters.  For example, "SalesForNBCUniversal" will return "sales_for_nbc_universal"
 * ***hyphen_to_underscore*** - Converts "-" to "_", otherwise leaves them alone
 * ***period_to_underscore*** - Converts "." to "_", otherwise leaves them alone
 * ***to_upper*** - Converts string to UPPERCASE
 * ***to_lower*** - Converts string to lowercase, takes precedence over "to_upper"

## About the Author

My name is James Larsen, and I have been working professionally as a Business Analyst, Database Architect and Data Engineer since 2007.  While I specialize in Data Modeling and SQL, I am working to improve my knowledge in different data engineering technologies, particularly Python.

[https://www.linkedin.com/in/jameslarsen42/](https://www.linkedin.com/in/jameslarsen42/)