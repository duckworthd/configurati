"""
Commands for
"""
import imp
import json
import os
import sys

from .attrs import attrs
from .validation import validate, is_spec, ValidationError


def load_config(path):
  """Load a config module as a dict"""
  module = imp.load_source(os.path.split(path)[1], path)
  variables = {
      k:getattr(module, k) for k in dir(module)
      if not '__' in k
  }
  return variables


def load_spec(path):
  spec = load_config(path)
  spec = { k:v for k,v in spec.items()
           if is_spec(v) }
  return spec


def import_config(path):
  """Load contents of another configuration file into the environment

  Parameters
  ----------
  path : str
      path of other configuration file
  """
  variables = load_config(path)
  _add_globals(variables)


def env(variable_name, type=str):
  """Load an environment variable

  Parameters
  ----------
  variable_name : str
      environment variable name
  type : function
      convert variable to correct type
  """
  return type(os.environ[variable_name])


def configure(config_path='config.py', spec_path='spec.py'):
  """Initialize configuration"""
  # load configuration file, if one was specified
  config = load_config(config_path)

  # override config file with command line args
  args = _eat_command_line_arguments()
  config.update(args)

  # validate the config
  spec   = load_spec(spec_path)
  config = validate(spec, config)

  return attrs.from_dict(config)


def _eat_command_line_arguments():
  """Turn command line args into key-value pairs

  Assume command line args are of the form
    --key1 value1 --key2 value2 ...

  values must be valid JSON
  """
  result = {}
  args   = sys.argv[1:]
  i      = 0
  while i < len(args):
    assert args[i].startswith('--'), \
        'Command line options must be of the form "--key value'
    key = args[i][2:]
    try:
      value = json.loads(args[i+1])
    except ValueError:
      value = args[i+1]
    result[key] = value
    i += 2
  return result


def _add_globals(**kwargs):
  """Update global dictionary of whoever is using this module"""
  # get first stack frame not in this module
  i = 0
  while sys._getframe(i).f_globals['__name__'] == __name__:
    i += 1

  # update environment of said frame
  glob = sys._getframe(i).f_globals
  glob.update(d)
