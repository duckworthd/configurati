"""
Tools for validating a configuration spec
"""

from utils import identity


class variable(object):
  def __init__(self, type=str, help=None):
    self.type = type
    self.help = help

  def __repr__(self):
    return str(self)

  def __eq__(self, other):
    return isinstance(other, variable) and \
        other.type == self.type and \
        other.help == self.help


class optional(variable):
  """An optional variable

  Used in a spec file to denote a variable that has a default value and may be
  left unspecified in a config file.

  >>> version = optional(default="1.0-SNAPSHOT", \
                         help="Version of this application")

  Parameters
  ----------
  type : function
      function to coerce argument to desired type
  help : str
      long description of this variable
  default : object
      default value to use if this variable isn't in the config.
  """
  def __init__(self, type=identity, help=None, default=None):
    super(optional, self).__init__(type, help)
    self.default = default

  def __str__(self):
    return (
        "optional(type=%s, help=%s, default=%s)" %
        (self.type, self.help, self.default)
    )

  def __eq__(self, other):
    return super(optional, self).__eq__(other) and \
        isinstance(other, optional) and \
        other.default == self.default


class required(variable):
  """A required variable

  Used in a spec file to denote a variable that must be in a valid config file.
  If a required variable is not in a config file, validation will fail.

  Parameters
  ----------
  type : function
      function to coerce argument to desired type
  help : str
      long description of this variable
  """
  def __init__(self, type=identity, help=None):
    super(required, self).__init__(type, help)

  def __str__(self):
    return (
        "required(type=%s, help=%s)" %
        (self.type, self.help)
    )

  def __eq__(self, other):
    return super(required, self).__eq__(other) and \
        isinstance(other, required)


def is_required(obj):
  """Is this a required variable?"""
  return is_collection(obj) \
      or isinstance(obj, required)


def is_spec(obj):
  """Is this a valid specification variable?"""
  return is_collection(obj) \
      or isinstance(obj, variable)


def is_collection(obj):
  return isinstance(obj, dict) \
      or isinstance(obj, list) \
      or isinstance(obj, tuple)


class ValidationError(Exception):
  def __init__(self, msg, path=''):
    super(ValidationError, self).__init__("%s (%s)" % (msg, path[1:]))
    self.msg  = msg
    self.path = path

  def extend_path(self, path):
    return ValidationError(path=(path + self.path), msg=self.msg)


def validate(spec, config):
  """Validate a configuration file against a spec"""
  if is_required(spec) and config is None:
    raise ValidationError("Missing required argument")

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
      raise ValidationError(msg="Unrecognized variable type: %s" % str(type(spec)))

  if isinstance(spec, dict):
    if not isinstance(config, dict):
      raise ValidationError("Improper object type (expected dict)")
    result = {}
    for k, v in spec.items():
      try:
        result[k] = validate(v, config.get(k, None))
      except ValidationError as e:
        raise e.extend_path(".%s" % k)
    return result

  if isinstance(spec, list):
    if not isinstance(config, list):
      raise ValidationError("Improper object type (expected list)")
    result = []
    for i, v in enumerate(config):
      try:
        result.append(validate(spec[0], v))
      except ValidationError as e:
        raise e.extend_path("[%d]" % i)
    return result

  if isinstance(spec, tuple):
    if not isinstance(config, tuple):
      raise ValidationError("Improper object type (expected tuple)")
    if not len(spec) == len(config):
      raise ValidationError("Incorrect tuple length (expected %d; found %d)" % \
          (len(spec), len(config)))
    result = []
    for i, (s, v) in enumerate(zip(spec,config)):
      try:
        result.append(validate(s, v))
      except ValidationError as e:
        raise e.extend_path("[%d]" % i)
    return tuple(result)

  if isinstance(spec, required):
    if config is None:
      raise ValidationError("Missing required argument")
    else:
      try:
        return spec.type(config)
      except ValueError as e:
        raise ValidationError("Type conversion failure")

  if isinstance(spec, optional):
    if config is None:
      return spec.default
    else:
      try:
        return spec.type(config)
      except ValueError as e:
        raise ValidationError("Type conversion failure")


def one_of(**options):
  """is this object one of these options?"""
  def type(obj):
    if not obj in options:
      raise ValueError("%s isn't one of %s" % (obj, options))
    return obj
  return type
