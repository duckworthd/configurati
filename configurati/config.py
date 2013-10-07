import re

from .attrs import attrs
from .exceptions import ConfiguratiException
from .utils import Missing


class Config(attrs):
  """A configuration object"""

  def __init__(self, contents={}):
    self._contents = attrs.from_dict(contents)

  def __setitem__(self, key, value):
    return set(self._contents, key, value, build=True)

  def __getitem__(self, key):
    return get(self._contents, key)

  def __getattr__(self, key):
    return self[key]

  def __setattr__(self, key, value):
    self[key] = value
    return self


def get(obj, key, build=False):
  """Retrieve a key from a nested object"""
  if len(key) == 0:
    return obj
  else:
    key, rest = next_key(key)
    if isinstance(obj, dict):
      if build and key not in obj:
        obj[key] = {}
      return get(obj[key], rest, build)
    elif isinstance(obj, list) or isinstance(obj, tuple):
      if not isinstance(key, int):
        raise KeyError('Attempting to use non-integer index "{}" on list or tuple'.format(key))
      if key >= len(obj):
        raise KeyError('Attempting to access index {} but only {} available'.format(key, len(obj)))
      return get(obj[key], rest, build)
    else:
      raise KeyError('Still have additional key components "{}" but have already reached terminal node {}'.format(key, obj))


def set(obj, key, value, build=False):
  """Set a key to a value in a nested object"""
  if len(key) == 0:
    return value
  else:
    key, rest = next_key(key)

    def set_dict(obj, key, value):
      if build and key not in obj:
        obj[key] = {}
      obj[key] = set(obj[key], rest, value, build)
      return obj

    def set_list(obj, key, value):
      if not isinstance(key, int):
        raise KeyError('Attempting to use non-integer index "{}" on list or tuple'.format(key))
      if key >= len(obj):
        obj = obj + [Missing] * (key + 1 - len(obj))
      obj[key] = set(obj[key], rest, value, build)
      return obj


    if isinstance(obj, dict):
      return set_dict(obj, key, value)
    elif isinstance(obj, list):
     return set_list(obj, key, value)
    elif isinstance(obj, tuple):
      return tuple(set_list(list(obj), key, value))
    else:
      raise KeyError('Still have additional key components "{}" but have already reached terminal node {}'.format(key, obj))


def next_key(s):
  if s.startswith('.'):
    # get "key_1" from ".key_1[0]" or ".key_1.key_2"
    match = re.search("""[.]([^.[]+)""", s)
  elif s.startswith('['):
    # get "5" from "[5].key_1" or "[5][3]"
    match = re.search("""\[([^[.]+)\]""", s)
  else:
    match = None

  if match is not None:
    key, rest = match.group(1), s[match.end():]
    return parse_key(key), rest
  else:
    raise ConfiguratiException("Unable to parse key: {}".format(s))


def parse_key(s):
  if '-' in s:
    s = s.replace("-", "_")
  try:
    s = int(s)
  except ValueError:
    pass
  return s

