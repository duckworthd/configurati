from __future__ import absolute_import

import json

from ..attrs import set
from ..exceptions import ConfiguratiException


def load(args):
  """Construct configuration object from command line arguments alone"""
  result = {}
  if args is None:
    args = sys.argv[1:]
  while len(args) > 0:
    k, v, args = next(args)
    set(result, "." + k, v, build=True)
  return result


def next(args):
  """Get next key-value pair from arguments"""
  a = args[0]
  if not a.startswith('--'):
    raise ConfiguratiException('Arguments must be of the form "--key value" or "--key=value"')

  a = a[2:]
  if '=' in a:
    # "--key=value"
    key, value = a.split("=", 1)
    remaining = args[1:]
  else:
    # "--key" "value"
    if not len(args) >= 2:
      raise ConfiguratiException('Found key but no value: "{}"'.format(args))
    key, value = a, args[1]
    remaining = args[2:]

  return key, parse_value(value), remaining


def parse_value(s):
  """Parse a value expression"""
  # XXX should this be any Python expression?
  try:
    s = json.loads(s)
  except ValueError:
    pass
  return s
