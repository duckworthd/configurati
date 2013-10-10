import os
import sys

import json
import yaml

from .configure import configure
from .exceptions import ConfiguratiException


def die(message=None):
  if message:
    sys.stderr.write(message)
  sys.stderr.write("Usage: python -m configurati.interpolate <config file>\n")
  sys.exit(1)


if __name__ == '__main__':
  if len(sys.argv) != 2:
    die()
  fname = sys.argv[1]
  ext = os.path.splitext(fname)[1].lower()

  config = configure(args=[], config=sys.argv[1])

  if ext == '.yaml':
    print yaml.dump(config)
  elif ext == '.json':
    print json.dumps(config)
  else:
    die("Unknown file format: {}".format(ext))
