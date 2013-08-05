import os

from configurati import import_config, load_config


# import another configuration file's contents
import_config('config2.py')

# or load it in directory
other_config = load_config('config2.py', relative_to_caller=True)

# this is real python -- use real python!
required_list_variable = list(range(10))
optional_list_variable = list(reversed(range(10)))

### This tuple has the wrong length; This would crash!
# tuple_variable = (1, 2.0, "3", 4)
tuple_variable = (1, 2.0, "3")

dict_variable = {
  # hyphens in keys are converted to underscores
  'str-key': "I'm a dict variable!",
  'list_key': [], # empty list variable
  'dict_key': {
    'key1': 123,
    # 'key2: 456  # this key is optional
  }
}

# if a variable appears in a config but not in the spec, it
# will not be loaded.
ignored_variable = "wut."
