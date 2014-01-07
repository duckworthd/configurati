"""
Attribute dictionary
"""
import re

from .exceptions import ConfiguratiException
from .utils import recursive_apply, Missing


class adict(dict):
  """A dict you can access with dot notation"""

  def __getattr__(self, key):
    if key in self:
      return self[key]
    else:
      raise AttributeError("No attribute: " + str(key))

  def __setattr__(self, key, value):
    self[key] = value
    return self[key]

  def to_dict(self):
    f = lambda x: dict(x) if isinstance(x, attrs) else x
    return recursive_apply(self, value_func=f)

  @classmethod
  def from_dict(cls, d):
    f = lambda x: cls(x) if isinstance(x, dict) else x
    return recursive_apply(d, value_func=f)

  def unroll(self):
    unrolled = unroll(self)
    return { k[1:]:v for k, v in unrolled.items() }


class attrs(adict):
  """A dictionary/object designed for nested objects"""

  def __init__(self, *args, **kwargs):
    super(attrs, self).__init__()

    # get key, value pairs passed in
    if len(args) == 0:
      a = []
    elif len(args) == 1:
      a = args[0]
      if isinstance(a, dict):
        a = a.items()
    elif len(args) > 1:
      raise TypeError(
          "dict expected at most 1 arguments, got {}".format(len(args))
        )
    a += kwargs.items()

    # add them all, one by one
    for k, v in a:
      self[k] = v

  def __getitem__(self, key):
    if is_atomic(key):
      return super(attrs, self).__getitem__(key)
    else:
      return get(self, '.' + key)

  def __setitem__(self, key, value):
    if not valid_key(key):
      raise KeyError(
          "invalid attrs key: {}".format(key)
        )
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



def is_atomic(key):
  """return True is a key is "simple" in the sense of not referring to a nested
  object. e.g., 'a' is simple but 'a.b' is not"""
  return not ('[' in key or '.' in key)


def unroll(a):
  if isinstance(a, dict):
    result = {}
    for k, v in a.items():
      for k_, v_ in unroll(v).items():
        result["." + k + k_] = v_
    return result
  elif isinstance(a, tuple) or isinstance(a, list):
    result = {}
    for k, v, in enumerate(a):
      for k_, v_ in unroll(v).items():
        result["[{}]{}".format(k, k_)] = v_
    return result
  else:
    return {'': a}


def get(obj, key):
  """Retrieve a key from a nested object"""
  if len(key) == 0:
    return obj
  else:
    key, rest = next_key(key)
    if isinstance(obj, dict):
      return get(obj[key], rest)
    elif isinstance(obj, list) or isinstance(obj, tuple):
      if not isinstance(key, int):
        raise KeyError('Attempting to use non-integer index "{}" on list or tuple'.format(key))
      if key >= len(obj):
        raise KeyError('Attempting to access index {} but only {} available'.format(key, len(obj)))
      return get(obj[key], rest)
    else:
      raise KeyError('Still have additional key components "{}" but have already reached terminal node {}'.format(key, obj))


def set(obj, key, value, build=False):
  """Set a key to a value in a nested object"""
  if len(key) == 0:
    return value
  else:
    def set_dict(obj, key, value):
      obj[key] = set(obj.get(key, Missing), rest, value, build)
      return obj

    def set_list(obj, key, value):
      if not isinstance(key, int):
        raise KeyError('Attempting to use non-integer index "{}" on list or tuple'.format(key))
      if key >= len(obj):
        obj = obj + [Missing] * (key + 1 - len(obj))
      obj[key] = set(obj[key], rest, value, build)
      return obj

    def set_tuple(obj, key, value):
      return tuple(set_list(list(obj), key, value))

    # parse next atomic key
    key, rest = next_key(key)

    # make an object if `build` and object is missing
    if build and obj is Missing:
      if isinstance(key, basestring):
        obj = {}
      elif isinstance(key, int):
        obj = [Missing] * (key + 1)
      else:
        raise KeyError("Unrecognized key type: {}".format(str(type(key))))

    if isinstance(obj, dict):
      return set_dict(obj, key, value)
    elif isinstance(obj, list):
     return set_list(obj, key, value)
    elif isinstance(obj, tuple):
      return set_tuple(obj, key, value)
    else:
      raise KeyError('Still have additional key components "{}" but have already reached terminal node {}'.format(key, obj))


def next_key(s):
  if s.startswith('.'):
    # get "key_1" from ".key_1[0]" or ".key_1.key_2"
    match = re.search("""^[.]([^.[]*)""", s)
    key, rest = match.group(1), s[match.end():]
    if re.search("""^[a-zA-Z][a-zA-Z0-9-_]*$""", key) is None:
      raise KeyError('"{}" is not a attrs key'.format(key))
    return key.replace("-", "_"), rest
  elif s.startswith('['):
    # get "5" from "[5].key_1" or "[5][3]"
    match = re.search("""^\[([^[.]*)\]""", s)
    key, rest = match.group(1), s[match.end():]
    try:
      key = int(key)
    except ValueError:
      raise KeyError('"{}" is not a valid list/tuple key'.format(key))
    return key, rest
  else:
    raise KeyError('"{}" is not a valid attrs key'.format(s))


def valid_key(k):
  if not isinstance(k, basestring):
    return False
  else:
    k = '.' + k
    while len(k) > 0:
      try:
        _, k = next_key(k)
      except KeyError:
        return False
    return True
