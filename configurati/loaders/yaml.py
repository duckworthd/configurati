from __future__ import absolute_import

import yaml

from .utils import substitute
from ..utils import recursive_apply


def load(f):
  contents = yaml.loads(f)
  return recursive_apply(contents, value_func=substitute)
