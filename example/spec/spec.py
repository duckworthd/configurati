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
# import_spec("other_spec.py", relative_to_caller=True)
# other_spec = load_spec("other_other_spec.py", relative_to_caller=True)
