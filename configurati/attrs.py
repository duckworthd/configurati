"""
Attribute dictionary
"""

from .utils import recursive_apply

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

  def to_dict(self):
    f = lambda x: dict(x) if isinstance(x, attrs) else x
    return recursive_apply(self, value_func=f)

  @staticmethod
  def from_dict(d):
    f = lambda x: attrs(x) if isinstance(x, dict) else x
    return recursive_apply(d, value_func=f)
