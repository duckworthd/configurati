import os

from configuratti import optional, required


# define required variables with type coercion
str_variable = required(type=str, help="A string variable")
int_variable = required(type=int, help="An integer variable")

# if type is unspecified, no type coercion occurs
untyped_variable = required(help="This variable won't be coerced")

# variables can be made optional with default values
optional_float_variable = optional(type=float, default=1.0, \
                          help="A floating point variable")

# collections (dict, tuple, list) are assumed required by default.
# A list variable contains one or more objects matching the same variable
# specification.
required_list_variable = [
    required(type=int, help="An element of a list variable")
]
optional_list_variable = optional(
    type=[required(type=int)],
    default=[1, 2, 3]
)


# a tuple variable contains a fixed number of objects, each with its own
# specification.
tuple_variable = (
    required(type=int, help="first tuple variable"),
    required(type=float, help="second tuple variable"),
    required(type=str, help="third tuple variable"),
)

# a dict variable contains keys to variables, potentially with nesting.
dict_variable = {
    'str_key': required(type=str),
    'list_key': [required(type=int)],
    'dict_key': {
      'key1': required(),
      'key2': optional(type=int, default=-1),
    }
}
