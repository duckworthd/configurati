"""
Attribute dictionary
"""

class attrs(dict):
  """A dict you can access with dot notation"""

  def __getattr__(self, key):
    return self[key]

  @staticmethod
  def from_dict(d):
    if isinstance(d, dict):
      result = attrs( (k, attrs.from_dict(v)) for (k, v) in d.items() )
    elif isinstance(d, list):
      result = [attrs.from_dict(v) for v in d]
    elif isinstance(d, tuple):
      result = tuple([attrs.from_dict(v) for v in d])
    else:
      result = d
    return result
