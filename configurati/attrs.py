"""
Attribute dictionary
"""
import re

from .exceptions import ConfiguratiException
from .utils import recursive_apply, Missing


class attrs(dict):
  """A dict you can access with dot notation"""

  def __getattr__(self, key):
    if key in self:
      return self[key]
    else:
      raise AttributeError("No attribute: " + str(key))

  def __setattr__(self, key, value):
    self[key] = value
    return self[key]

  def __getitem__(self, key):
    if is_atomic(key):
      return super(attrs, self).__getitem__(key)
    else:
      return get(self, '.' + key)

  def __setitem__(self, key, value):
    value = attrs.from_dict(value)
    if is_atomic(key):
      return super(attrs, self).__setitem__(key, value)
    else:
      return set(self, '.' + key, value, build=True)

  def __contains__(self, key):
    try:
      self[key]
      return True
    except:
      return False

  def to_dict(self):
    f = lambda x: dict(x) if isinstance(x, attrs) else x
    return recursive_apply(self, value_func=f)

  @staticmethod
  def from_dict(d):
    f = lambda x: attrs(x) if isinstance(x, dict) else x
    return recursive_apply(d, value_func=f)


def is_atomic(key):
  """return True is a key is "simple" in the sense of not referring to a nested
  object. e.g., 'a' is simple but 'a.b' is not"""
  return not ('[' in key or '.' in key)


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

