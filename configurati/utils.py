import itertools
import re
import sys


def identity(x):
  return x


def recursive_apply(obj, key_func=identity, value_func=identity):
  """Recursively apply a function to the keys and values of a nested object"""
  if isinstance(obj, dict):
    result = {}
    for k, v in obj.items():
      k = key_func(k)
      result[k] = recursive_apply(v, key_func, value_func)
    return value_func(result)
  elif isinstance(obj, list):
    result = []
    for v in obj:
      result.append(recursive_apply(v, key_func, value_func))
    return result
  elif isinstance(obj, tuple):
    result = []
    for v in obj:
      result.append(recursive_apply(v, key_func, value_func))
    return tuple(result)
  else:
    return value_func(obj)


def normalize_keys(obj):
  """replace list-variable with list_variable"""

  def key_func(k):
    return re.sub("([a-zA-Z])-([a-zA-Z])", r"\1_\2", k)

  return recursive_apply(obj, key_func=key_func)


def update(o1, o2):
  """Overlay `o1` over `o2`"""

  def update_dict(o1, o2):
    if not isinstance(o2, dict):
      o2 = {}
    for k, v in o1.items():
      o2[k] = update(o1[k], o2.get(k, {}))
    return o2

  def update_list(o1, o2):
    if not isinstance(o2, list):
      o2 = []
    if len(o1) > len(o2):
      o2 = o2 + [Missing] * (len(o1) - len(o2))
    for i in range(len(o1)):
      o2[i] = update(o1[i], o2[i])
    return o2


  if isinstance(o1, dict):
    return update_dict(o1, o2)
  elif isinstance(o1, list):
    return update_list(o1, o2)
  elif isinstance(o1, tuple):
    return tuple(update_list(o1, list(o2)))
  else:
    if isinstance(o1, Missing_):
      return o2
    else:
      return o1


class Missing_(object):
  """Represents an unspecified value in a list or tuple"""
  pass


Missing = Missing_()

def previous_frame():
  """Find the first frame in the call stack not originating from this module"""
  for i in itertools.count():
    name = sys._getframe(i).f_globals.get('__name__', '')
    if name.split(".")[0] != __name__.split(".")[0]:
      return sys._getframe(i)


def add_globals(**kwargs):
  """Update global dictionary of whoever is using this module"""
  # get first stack frame not in this module
  # update environment of said frame
  glob = previous_frame().f_globals
  glob.update(kwargs)
