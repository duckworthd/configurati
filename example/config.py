import os

from configuratti import import_config


# import another configuration file's contents
folder = os.path.split(os.path.abspath(__file__))[0]
import_config(os.path.join(folder, "config2.py"))

# this is real python -- use real python!
required_list_variable = list(range(10))
optional_list_variable = list(reversed(range(10)))

### This tuple has the wrong length; This would crash!
# tuple_variable = (1, 2.0, "3", 4)
tuple_variable = (1, 2.0, "3")

dict_variable = {
  'str_key': "I'm a dict variable!",
  'list_key': [], # empty list variable
  'dict_key': {
    'key1': 123,
    # 'key2: 456  # this key is optional
  }
}

# if a variable appears in a config but not in the spec, it
# will not be loaded.
ignored_variable = "wut."
