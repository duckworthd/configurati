"""
Commands to load a configuration
"""
import codecs
import os
import sys

from .attrs import attrs
from .exceptions import ValidationError
from .globals import CONFIG
from .loaders import load
from .utils import normalize_keys
from .validation import validate, is_spec


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
  with codecs.open(path, 'r', 'UTF-8') as f:
    return attrs.from_dict(normalize_keys(load(f)))


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


def configure(args=None, config=None, spec=None):
  # load command line arguments
  if args is None:
    args = sys.argv[1:]
  if args is not None:
    args = load(args)
  else:
    args = {}

  # load configuration file
  if config is None and 'config' in args:
    config = args['config']
  if config is not None:
    result = update(args, load_config(config))
  else:
    result = args

  # apply config spec
  if spec is None and 'spec' in args:
    spec = args['spec']
  if spec is not None:
    result = validate(load_spec(spec), result)

  # set globally and return
  CONFIG(result)
  return CONFIG()


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
