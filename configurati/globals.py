"""
Global way to access configuration.
"""

from .attrs import attrs


# globally accessible configuration object.
# accessible via CONFIG()
_CONFIG = attrs()


def CONFIG(config=None):
  if config is not None:
    global _CONFIG
    _CONFIG = attrs.from_dict(config)
  return _CONFIG
