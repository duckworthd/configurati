from configuratti import env

# use env to load environment variables
str_variable = env('USER')
int_variable = "1234567890"   # apply type coercion
untyped_variable = lambda: "Hello, World!"

### Default value will be used
# optional_float_variable = "1.23"
