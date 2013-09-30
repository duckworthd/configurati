"""
Commands to load a configuration
"""
import imp
import json
import os
import re
import sys
import uuid

from .attrs import attrs
from .validation import validate, is_spec, ValidationError
from .utils import normalize_keys


# global configuration object. When `configure` is called, the config is placed
# here as well as returned.
_CONFIG = attrs()


def CONFIG():
  return _CONFIG


def load_config(path, relative_to_caller=False):
  """Load a config module as a dict

  Parameters
  ----------
  path : str
      path to configuration file
  relative_to_caller : bool
      if path isn't an absolute file path, interpret it as relative to the file
      from which this method is called.
  """
  if relative_to_caller and not os.path.abspath(path) == path:
    previous_fname  = previous_frame().f_globals['__file__']
    previous_fname  = os.path.abspath(previous_fname)
    previous_folder = os.path.split(previous_fname)[0]
    path            = os.path.join(previous_folder, path)
  modname = str(uuid.uuid4())
  module = imp.load_source(modname, path)
  variables = {
      k:getattr(module, k) for k in dir(module)
      if not '__' in k
  }
  return normalize_keys(variables)


def load_spec(path, relative_to_caller=False):
  """Load a configuration specification"""
  spec = load_config(path, relative_to_caller=relative_to_caller)
  spec = { k:v for k,v in spec.items()
           if is_spec(v) }
  return spec


def import_config(path, relative_to_caller=True):
  """Load contents of another configuration file into the environment

  Parameters
  ----------
  path : str
      path to configuration file
  relative_to_caller : bool
      if path isn't an absolute file path, interpret it as relative to the file
      from which this method is called.
  """
  variables = load_config(path, relative_to_caller=relative_to_caller)
  _add_globals(**variables)


def import_spec(path, relative_to_caller=True):
  """Import another specification's contents into the environment"""
  variables = load_spec(path, relative_to_caller=relative_to_caller)
  _add_globals(**variables)


def env(variable_name):
  """Load an environment variable

  Parameters
  ----------
  variable_name : str
      environment variable name
  """
  return os.environ[variable_name]


def update_config(old, new):
  def _split(k):
    # .a.b.c -> (a, b.c)
    # .1.b.c -> (1, b.c)
    # [1].b[2].c -> (1, .b[2].c)
    # .a -> (a, '')
    # [1] -> (1, '')
    if len(k) == 0:
      return []
    elif k.startswith('['):
      match = re.search(r'^\[([-+]?\d+?)\]', k)
      start = int(match.group(1))
      rest  = k[match.end():]
      rest = _split(rest)
      return [start] + rest
    elif k.startswith('.'):
      match = re.search(r'[.](.+?)(\[|[.]|$)', k)
      start = match.group(1)
      if match.end() == len(k):
        rest = k[match.end():]
      else:
        rest = k[match.end()-1:]
      rest = _split(rest)
      try:
        start = int(start)
      except ValueError:
        pass
      return [start] + rest
    else:
      wtf

  def _reconstruct(keys, v):
    if len(keys) == 0:
      return v
    else:
      start, rest = keys[0], keys[1:]
      if isinstance(start, int):
        raise ValueError("Unable to reconstruct command line argument with array indices")
      else:
        return {start: _reconstruct(rest, v)}

  def _update(o, keys, v):
    if len(keys) == 0:
      return v
    else:
      if o is None:
        return _reconstruct(keys, v)
      else:
        start, rest = keys[0], keys[1:]
        if isinstance(start, int):
          if isinstance(o, list):
            o[start] = _update(o[start], rest, v)
          elif isinstance(o, tuple):
            o = list(o)
            o[start] = _update(o[start], rest, v)
            return tuple(o)
        elif isinstance(start, basestring):
          o[start] = _update(o.get(start, None), rest, v)
        else:
          wtf
        return o

  for (k, v) in new.items():
    old = _update(old, _split('.' + k), v)
  return old


def configure(args=None, config_path=None, spec_path=None):
  """Initialize configuration"""
  # load configuration file, if one was specified
  if config_path is not None:
    config = load_config(config_path)
  else:
    config = {}

  # override config file with command line args
  args   = _eat_command_line_arguments(args)
  config = update_config(config, args)

  # validate the config
  if spec_path:
    spec   = load_spec(spec_path)
    config = validate(spec, config)

  # load config into global object
  global _CONFIG
  _CONFIG = attrs.from_dict(config)
  return CONFIG()


def _eat_command_line_arguments(args=None):
  """Turn command line args into key-value pairs

  Assume command line args are of the form
    --key1 value1 --key2 value2 ...

  values must be valid python expressions
  """
  result = {}
  if args is None:
    args = sys.argv[1:]
  i = 0
  while i < len(args):
    assert args[i].startswith('--'), \
        'Command line options must be of the form "--key value"'
    key = args[i][2:]
    if '=' in key:
      key, value = key.split('=', 1)
      i += 1
    elif i+1 < len(args):
      value = args[i+1]
      i += 2
    else:
      raise Exception("No value for key: %s" % key)
    try:
      value = eval(value)
    except NameError:
      pass
    except SyntaxError:
      pass
    result[key] = value
  return normalize_keys(result)


def _add_globals(**kwargs):
  """Update global dictionary of whoever is using this module"""
  # get first stack frame not in this module
  # update environment of said frame
  glob = previous_frame().f_globals
  glob.update(kwargs)


def previous_frame():
  """Find the first frame in the call stack not originating from this module"""
  i = 0
  while sys._getframe(i).f_globals['__name__'] == __name__:
    i += 1
  return sys._getframe(i)
