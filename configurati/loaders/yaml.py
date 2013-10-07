from __future__ import absolute_import

try:
  import yaml
except ImportError:
  import sys
  sys.stderr.write("Unable to import `yaml`. Install with `pip install PyYAML`\n")
  sys.exit(1)

from .utils import substitute
from ..utils import recursive_apply


def load(f):
  contents = yaml.load(f)
  return recursive_apply(contents, value_func=substitute)
