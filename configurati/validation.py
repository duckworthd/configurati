"""
Tools for validating a configuration spec
"""

from .attrs import attrs
from .exceptions import ValidationError
from .utils import identity, Missing


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
                         type=str, \
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

  >>> version = required(type=str, \
                         help="Version of this application")

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


def one_of(*options):
  """is this object one of these options?"""
  def type(obj):
    if not obj in options:
      raise ValueError("%s isn't one of %s" % (obj, options))
    return obj
  return type


def is_spec(obj):
  """Is this a valid specification for an object?"""
  return any(test(obj) for test, _ in VALIDATORS)


def validate_required(spec, config):
  if config is Missing:
    raise ValidationError("Missing required argument")
  if hasattr(spec.type, '__call__'):
    try:
      return spec.type(config)
    except ValueError:
      raise ValidationError('failed to convert "{}" with "{}"'.format(config, spec))
  else:
    # a spec, rather than a function, was used as the type.
    return _validate(spec.type, config)


def validate_optional(spec, config):
  if config is Missing:
    config = spec.default
  return _validate(required(type=spec.type), config)


def validate_dict(spec, config):
  if config is Missing:
    # if config is missing, replace it with an empty dict. if any of the spec's
    # contents are required, this will throw a ValidationError later; on the
    # other hand, if they're all optional, they'll be replaced sensibly.
    config = {}

  if not isinstance(config, dict):
    raise ValidationError('spec calls for type dict; found "{}" instead'.format(config))

  # for each key-value pair, replace with validated bit or what's already in
  # the config IF the value is in fact a spec definition
  result = {}
  for k, v in spec.items():
    if is_spec(v):
      result[k] = _validate(v, config.get(k, Missing))
  return result


def validate_list(spec, config):
  if len(spec) > 1:
    raise ValidationError('spec for list "{}" contains multiple definitions for its contents')
  elif len(spec) == 0:
    # no spec for contents, so just take it as everything is OK
    spec = [required(type=identity)]

  if config is Missing:
    # lists are always optional; if unspecified, an empty list is used
    config = []

  if not isinstance(config, list):
    raise ValidationError('spec calls for type list; found "{}" instead'.format(config))

  return [_validate(spec[0], c) for c in config]


def validate_tuple(spec, config):
  if config is Missing:
    # if config is missing, replace it a tuple of all missing values. if all of
    # this spec's fields are optional, then they'll be replaced reasonable;
    # otherwise, a ValidationError will be thrown, as expected.
    config = tuple([Missing] * len(spec))

  if not isinstance(config, tuple):
    if hasattr(config, '__iter__'):
      # coerce into a tuple. when using command line arguments
      # like '--a[1]', it's impossible to tell if a should be
      # a list or a tuple. this gives validation some leniency.
      config = tuple(config)
    else:
      raise ValidationError('spec calls for type tuple; found "{}" instead'.format(config))

  # extend config with Missing's if necessary
  if len(config) < len(spec):
    config = tuple(list(config) + [Missing] * (len(spec) - len(config)))

  # XXX what if spec and config have different lengths?
  if len(spec) != len(config):
    raise ValidationError('length of spec "{}" doesn\'t match config "{}"'.format(spec, config))

  return tuple( _validate(s, c) for s, c in zip(spec, config) )


VALIDATORS = [
    (lambda x: isinstance(x,required),validate_required),
    (lambda x: isinstance(x,optional),validate_optional),
    (lambda x: isinstance(x,    dict),    validate_dict),
    (lambda x: isinstance(x,    list),    validate_list),
    (lambda x: isinstance(x,   tuple),   validate_tuple),
  ]

def _validate(spec, config):
  for (test, func) in VALIDATORS:
    if test(spec):
      return func(spec, config)
  raise ValidationError('No validator for spec: "{}"'.format(spec))


def missing_required_keys(spec, config):
  result = []
  for k, v in spec.unroll().items():
    if isinstance(v, required) and k not in config:
      result.append(k)
  return result


def validate(spec, config):
  missing = missing_required_keys(spec, attrs.from_dict(config))
  if len(missing) > 0:
    text = "Missing required fields: " + ", ".join(missing)
    raise ValidationError("".join(text))

  return _validate(spec, config)
