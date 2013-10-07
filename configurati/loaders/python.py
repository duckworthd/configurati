import imp
import os
import uuid


def load(f):
  modname = str(uuid.uuid4())
  module = imp.load_source(modname, os.path.abspath(f.name))
  variables = {
    k:getattr(module, k) for k in dir(module)
    if not '__' in k
  }

  return variables
