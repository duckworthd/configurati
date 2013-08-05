import pprint
import os

from configurati import configure


directory   = os.path.split(os.path.abspath(__file__))[0]
config_path = os.path.join(directory, 'config.py')
spec_path   = os.path.join(directory, 'spec.py')

# load a configuration with a spec
config      = configure(config_path=config_path, spec_path=spec_path)
pprint.pprint(config)

# load a configuration without a spec. Will contain all variables in
# config.py's environment.
config2     = configure(config_path=config_path)
pprint.pprint(config2)
