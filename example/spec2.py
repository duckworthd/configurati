from configurati import optional, required

# a dict variable contains keys to variables, potentially with nesting.
dict_variable = {
    'str_key': required(type=str),
    'list_key': [required(type=int)],
    'dict_key': {
      'key1': required(),
      'key2': optional(type=int, default=-1),
    }
}
