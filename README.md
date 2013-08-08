`configurati`
============

`configurati` is a configuration file library for python,

+ config files are just normal Python modules
+ command-line overrides of configuration file variables
+ configuration file verification, including optional variables, type coercion,
  and collections

Installation
------------

`configurati` can be install from [PyPi](https://pypi.python.org/pypi/configurati/0.1) via `pip` or `easy_install`

```bash
$ easy_install configurati
$ pip install configurati
```

Config Format
-------------

Configuration files are just normal Python modules. All variables in the
configuration file's namespace will be loaded.

`config.py`

```python
from configurati import env

int_variable          = 1234567890
function_variable     = lambda: "Hello, World!"
environment_variable  = env("USER")   # use a bash environment variable
dict_variable = {
  'str_key'  : "I'm a dict variable!",
  'list_key' : [1,2,3,4,5],
  'dict_key' : {
    'key1' : 123,
    'key2'  : (0, 1, 'SNAPSHOT'),
  }
}
```

Configuration files are loaded with `configurati.configure` and access with
dot and bracket notation,

`application.py`

```python
import configurati
from configurati import configure

config = configure(config_path='config.py')
config.int_variable                     # 1234567890
config.dict_variable.list_key[-1]       # 5
config['dict_variable']['list_key'][-1] # 5

config = configurati.CONFIG()           # same config as before
```

Command Line Overrides
----------------------

You can override parts of configuration files directly from the command line,
even in nested collections, with any valid python expression,

`config.py`

```python
int_variable      = 1234567890
function_variable = lambda: "Hello, World!"
list_variable = [
  { 'key': 'value1' },
  { 'key': 'value2' },
]
```

`application.py`

```python
from configurati import configure

config = configure(config_path='config.py')
config.int_variable       # 0
config.list_variable[1]   # {'key': 'new value'}
```

`command line`

```bash
$ python application.py '--int_variable' '0' '--list_variable[1].key' '"new value"'
```

Merging configs
---------------

Combine multiple configuration files by importing their entire contents into
the calling configuration file,

`config.py`

```python
from configurati import import_config

import_config('other_config.py')
```

or by importing other configuration files as `dict`s,

`config.py`

```python
from configurati import load_config

other_config = load_config('other_config.py')
```

Validation
----------

Defining a configuration format specification allows one several benefits,

+ type coercion
+ default values for optional variables
+ removing un-specified variables from configuration file (e.g. imports,
  temporary variables, etc)

`spec.py`

```python
from configurati import optional, required, load_spec, import_spec

# required variables
int_variable = required(type=int, help="An integer variable")
untyped_variable = required(help="This variable won't be coerced")

# optional variables with default values
optional_float_variable = optional(type=float, default=1.0, \
                          help="A floating point variable")

# if not explicitly made optional, collections are required
dict_variable = {
    'str_key': required(type=str),

    # lists contains 0 or more objects of the same type. This list_key is optional.
    'list_key': optional(type=[required(type=int)], default=[]),

    'dict_key': {
      # tuples contains a fixed number of variables, each with its own
      # specfiication
      'inner_dict_key': (required(type=int), required(type=str)),
    }
}

### import another specification file's contents
# import_spec('spec2.py')
# spec2 = load_spec('spec2.py')
```

`config.py`

```python
# int_variable will be coerced to an int
int_variable = '123'
untyped_variable = 'abc'

### default value will be used
# optional_float_variable = 2.0

dict_variable = {
  'str_key': 'string',

  ### default value will be used
  # 'list_key': [1,2,3]

  'dict_key': {
    'str_key': 'string2',
    'inner_dict_key': (1, 'hello')
  }
}
```

`application.py`

```
from configurati import configure

config = configure(config_path='config.py', spec_path='spec.py')
config.int_variable            # 123
config.optional_float_variable # 1.0
config.dict_variable.list_key  # []
```
