# `configurati`

`configurati` is a configuration file library for python,

+ configuration files json, yaml, or python modules
+ command-line overrides of configuration file
+ configuration including optional variables, type coercion, and collections

# Installation

`configurati` can be install from
[PyPi](https://pypi.python.org/pypi/configurati/0.1) via `pip` or
`easy_install`

```bash
$ easy_install configurati
$ pip install configurati
```

# Quick Start

I want to configure my awesome app with details about my cats. I'll begin by
writing my configuration file in Python,

`config.py`

```Python
from datetime import datetime

cats = [
  {'name' : 'Mittens', 'age' : 18},
  {'name' :     'Bob', 'age' :  4}
]

owner = {
  'name'     : 'Config Uratii',
  'address'  : '1234 Python Dr.',
  'birthday' : datetime(1970, 1, 1).isoformat()
}
```

To use this configuration, all I need to do is call `configurati.configure` in
my application...

`application.py`

```Python
from pprint import pprint
from configurati import configure

if __name__ == '__main__':
  pprint(configure())
```

...and tell it which configuration file to use from the command line,

```bash
$ python application.py \
  --config config.py
```

But that's not quite right. I misspelled my name, and today is Bob's birthday!

```bash
$ python application.py         \
  --config config.py            \
  "--owner.name" "Config Urati" \
  "--cats[1].age" "5"
```

Oh, and I forgot about my dogs!

```bash
$ python application.py         \
  --config config.py            \
  "--owner.name" "Config Urati" \
  "--cats[1].age" "5"           \
  "--dogs[0]" '{"name": "Sir Barks-a-lot", "age": 15}'
```

Actually, I don't like defining configuration files in Python. Let me do it in
a more language-agnostic format,

`config.yaml`

```yaml
cats:
- name: "Mittens"
  age: 18
- name: "Bob"
  age: 4

owner:
  name: "Config Uratii"
  address: "1234 Python Dr."
  "birthay": "`from datetime import datetime; datetime(1970, 1, 1).isoformat()`"
```

When I load this file with configurati, all text in backticks will be
evaluated, but what if I want to use it in another language? I need to see the
evaluated config file!

```bash
$ cat config.yaml | python -m configurati.interpolate > clean_config.yaml
```

Finally! Configuration complete. Now Let's actually use it!

`application.py`

```Python
from configurati import configure

if __name__ == '__main__':
  c = configure()

  # using bracket notation
  c['cats'][0]['age']   # 18

  # ...dot notation
  c.dogs[0].name        # "Sir Barks-a-lot"

  # ...fancy bracket notation
  c['cats[0].age']      # guess what...18
```

...and that's `configurati`!


# Defining a Configuration

`configurati` is designed with flexibility in mind. You should be able to
express everything you want in a config without being restricted by
configuration format or data type. Furthermore, mixing, matching, and
overriding parts of configs should be simple.

In `configurati`, you can specify a config in YAML, JSON, Python, or from the
command line. Command line parameters directly override a config file's
contents, so you can easily test out variations without generating a host of
different files.

## Python

The most direct way to specify a config is as a Python module. Nearly all valid
Python modules are also valid configurations (caveat: dict keys must be valid
python identifiers). `configurati` does not restrict the types available in
configuration, so modules, functions, and objects are all fair game.

```Python
import datetime
import os
from configurati import *

# merge multiple config files by importing them into the current space. Notice
# that you can import any configuration file that `configurati` understands.
import_config("environment_config.yaml")

# alternatively, load them as dicts
server = load_config("server_config.json")

# retrieve environment variables
environment = "dev" if env("ENVIRONMENT") is None else env("ENVIRONMENT")

# collection data types
collection_config = {
  'list_config': [1, 2, 3],
  'tuple_config': ('a', 'b', 'c'),
  'dict_config': {'a': 1, 'b': 2}
}

# python-only objects
date = datetime.datetime.now()

# valid config names have to start start with a letter and can only contain
# letters, numbers, and underscores. This variable will be ignored.
_ignored = True
```

## YAML & JSON

YAML and JSON are two common language-agnostic data formats which allow one to
express common atomic (numbers, strings) and collection (mapping, list) data
types natively. `configurati` extends these formats via string interpolation to
allow for the expression of arbitrary Python objects.

At this time, `import_config` does not work in these formats. Use `from
configurati import *; load_config("other_config.yaml").to_dict()` instead.

```yaml
collection_config:
  list_config: [1, 2, 3]
  tuple_config: "`('a', 'b', 'c')`"
  dict_config:
    a: 1
    b: 2

date: "`import datetime; datetime.datetime.now()`"

server: "`from configurati import *; load_config(\"server_config.json\").to_dict()"
```

# Loading and Using a Configuration

Configuration files can be loaded in one of two ways,

1. By calling `configurati.configure()` in your code and passing in `--config
   <path to config file>` from the command line
2. By explicitly using `configurati.configure(config="/path/to/config.py")`

A configuration object is an instance of `configurati.attrs.attrs`, a dict-like
object designed to make accessible attributes easier.

```
from configurati.attrs import attrs
from configurati import Missing

config = attrs.from_dict(
    {
      'collection_config': {
        'list_config': [1, 2, 3],
        'tuple_config': ('a', 'b', 'c'),
        'dict_config': { 'a': 1, 'b': 2 }
      },
    }
  )

# dot notation access
config.collection_config.list_config[2]           # 3

# nested dicts are also attrs instances
dict_config = config.collection_config.dict_config
dict_config.a                                     # 1

# bracket notation access
config['collection_config']['dict_config']['a']   # 1

# fancy bracket notation access
config['collection_config.tuple_config[2]']       # 'c'

# ...used in modifying values
config['collection_config.tuple_config[2]'] = 100
config.collection_config.tuple_config[2]          # 100

# ...and constructing new ones
config['x.y[2].z'] = "Hello"
config.x.y[2]                                     # { "z": "hello" }
config.x.y[0] is Missing                          # True
```

# Defining Configuration Specifications

When writing a program to be configured by a user, it is helpful to validate
said configuration and supply useful defaults. `configurati` allows one to
define configuration specifications as a Python module.

`spec.py`

```Python
from configurati import *

# variables in a spec are either required or optional. both take an optional
# `type` argument -- a function used to coerce the entered value to the desired
# type. `optional` variables also take an optional `default` argument -- the
# value to use if no value is entered.
name = required(type=str)
description = optional(type=str, default="")

# tuples are used to convey a fixed-length list of values. If all of its
# contents are optional, a tuple is as well; otherwise, it is required.
version = (
    required(type=int, help="major version"),
    optional(type=str, default="SNAPSHOT")
  )

# valid config keys must start with a letter and can only contain letters,
# numbers, and underscores. keys starting with an underscore are a good way of
# defining reusable, partial specs.
_server = {
    'host': optional(type=str, default="localhost"),
    "port": optional(type=int, default=8888)
  }

# like tuples, dicts are optional if all their contents are optional.
server = _server

# as the `password` field is required, the config must specificy a database
# object.
database = {
    'username': optional(type=str, default=env("USER")),
    'password': required(type=str),
  }
database.update(_server)

# lists represent an unknown number of objects of the same type. specs for
# lists are specified by entering a single spec in its contents.
caches = [
    {
      "host"    : optional(type=str, default="localhost"),
      "backend" : optional(type=one_of("redis", "memcached"), default="redis")
    }
  ]

# as with configs, you can import or load other specs. If
# `relative_to_caller=True` (the default), then the path is assumed to be
# relative to this file, rather than the caller
import_spec("other_spec.py", relative_to_caller=True)
other_spec = load_spec("other_other_spec.py", relative_to_caller=True)

```

Below is an (incomplete) sample configuration

`config.py`

```Python
from configurati import *

# `ignored` isn't specified in the specification, so it won't show up in the
# loaded config
ignored = True

# since description is unspecified, its value will be the default -- ""
name = 'sample'

# since database.password is unspecified, attempts at loading this config
# without additional command line arguments will throw a ValidationError
# database = { 'password': 'PASSWORD' }

# to use default values in a tuple, use `Missing`
version = (1, Missing)

# server.host is unspecified, so its default value will be used -- 8888
server = {
  'host': '127.0.0.1'
}

caches = [
  {},                       # {"host": "localhost", "backend":     "redis"}
  {"backend": "memcached"}, # {"host": "localhost", "backend": "memcached"}
]
```

As with configuration files, you may choose a spec in one of two ways,

1. via `configurati.configure(spec="/path/to/spec.py")`
2. via command line arguments, "--spec <path to spec>"

`application.py`

```Python
from pprint import pprint
from configurati import configure

pprint(configure(config='config.py', spec='spec.py'))
```

To complete the config, we'll specify the database password from the command
line,

```bash
$ python application.py '--database.password' 'PASSWORD'
{'caches': [{'backend': 'redis', 'host': 'localhost'},
            {'backend': 'memcached', 'host': 'localhost'}],
 'database': {'host': 'localhost',
              'password': 'PASSWORD',
              'port': 8888,
              'username': 'duckworthd'},
 'description': '',
 'name': 'sample',
 'server': {'host': '127.0.0.1', 'port': 8888},
 'version': (1, 'SNAPSHOT')}
```
