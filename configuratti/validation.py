"""
Tools for validating a configuration spec
"""


class variable(object):
  def __init__(self, name=None, type=str, help=None):
    self.name = name
    self.type = type
    self.help = help

  def __repr__(self):
    return str(self)


class optional(variable):
  def __init__(self, name=None, type=str, help=None, default=None):
    super(optional, self).__init__(name, type, help)
    self.default = default

  def __str__(self):
    return (
        "optional(name=%s, type=%s, help=%s, default=%s)" %
        (self.name, self.type, self.help, self.default)
    )


class required(variable):
  def __init__(self, name=None, type=str, help=None):
    super(required, self).__init__(name, type, help)

  def __str__(self):
    return (
        "required(name=%s, type=%s, help=%s)" %
        (self.name, self.type, self.help)
    )


def is_required(obj):
  return is_collection(obj) \
      or isinstance(obj, required)


def is_spec(obj):
  return is_collection(obj) \
      or isinstance(obj, variable)


def is_collection(obj):
  return isinstance(obj, dict) \
      or isinstance(obj, list) \
      or isinstance(obj, tuple)


def validate(spec, config):
  """Validate a configuration against a spec"""
  if is_required(spec):
    assert config is not None, "Missing required argument: %s" % str(spec)

  # unpack optional collection
  if isinstance(spec, variable) and is_collection(spec.type):
    if isinstance(spec, optional):
      if config is None:
        return spec.default
      else:
        spec = spec.type
    elif isinstance(spec, required):
      spec = spec.type
    else:
      raise TypeError()

  if isinstance(spec, dict):
    if not isinstance(config, dict):
      raise TypeError()
    result = {}
    for k, v in spec.items():
      result[k] = validate(v, config.get(k, None))
    return result

  if isinstance(spec, list):
    if not isinstance(config, list):
      raise TypeError()
    return [validate(spec[0], v) for v in config]

  if isinstance(spec, tuple):
    if not (isinstance(config, tuple) and len(spec) == len(config)):
      raise TypeError()
    return tuple([validate(s, v) for s, v in zip(spec, config)])

  if isinstance(spec, required):
    return spec.type(config)

  if isinstance(spec, optional):
    if spec is None:
      return spec.default
    else:
      return spec.type(config)
