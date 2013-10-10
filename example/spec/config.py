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
server =  {
  'host': '127.0.0.1'
}

caches = [
  {},                       # {"host": "localhost", "backend":     "redis"}
  {"backend": "memcached"}, # {"host": "localhost", "backend": "memcached"}
]

