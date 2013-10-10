import argparse
from StringIO import StringIO
import sys
import uuid

import json
import yaml

from .loaders import load


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      "evaluate configurati config file"
    )
  parser.add_argument("format", choices=["yaml", "json"],
      help="Format of config file")
  args = parser.parse_args()

  # write data to file-like object
  s = StringIO()
  s.write(sys.stdin.read())
  s.seek(0)
  s.name = str(uuid.uuid4()) + "." + args.format

  # load and evaluate config
  config = load(s)

  # write it back out

  if args.format == 'yaml':
    print yaml.dump(config)
  elif args.format == 'json':
    print json.dumps(config)
