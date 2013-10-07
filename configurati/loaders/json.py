from __future__ import absolute_import

import json

from .utils import substitute
from ..utils import recursive_apply


def load(f):
  contents = json.load(f)
  return recursive_apply(contents, value_func=substitute)
