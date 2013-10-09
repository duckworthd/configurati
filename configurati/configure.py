"""
The `configure` command
"""
import sys

from .loaders import load
from .commands import load_config, load_spec
from .globals import CONFIG
from .utils import update
from .validation import validate


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
