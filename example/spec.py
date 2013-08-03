from configuratti import optional, required, import_config
# TODO these end up in the loaded config


name        = required(help='Name of project')
version     = required(help='Version of project')
description = optional(default='missing...')
age         = required(type=int)

database = optional(
    type={
      'address' : required(),
      'port'    : required(type=int),
    },
    default={
      'address' : 'localhost',
      'port'    : 22,
    }
)

selectors = [
  {
    'uri': required(),
    'gold': {
      'price': required(type=float),
      'product_name': required(),
    },
    'version': (required(), required(type=int))
  }
]
