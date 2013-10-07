from .json import load as load_json
from .yaml import load as load_yaml
from .python import load as load_py
from .commandline import load as load_cl

from ..exceptions import ConfiguratiException


__all__ = [
  'load'
]


def load(f):
  if isinstance(f, list):
    return load_cl(f)
  else:
    n = f.name.lower()
    if n.endswith(".py"):
      return load_py(f)
    elif n.endswith(".yaml"):
      return load_yaml(f)
    elif n.endswith(".json"):
      return load_json(f)
    else:
      raise ConfiguratiException("Unrecognized file type {}".format(n))
