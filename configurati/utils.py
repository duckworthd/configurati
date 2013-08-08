import re


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
