# `configurati`

`configurati` is a configuration file library for python,

+ configuration files json, yaml, or python modules
+ command-line overrides of configuration file
+ configuration including optional variables, type coercion, and collections

# Installation

`configurati` can be install from [PyPi](https://pypi.python.org/pypi/configurati/0.1) via `pip` or `easy_install`

```bash
$ easy_install configurati
$ pip install configurati
```

# Quick Start

Let's say I want to configure my awesome app with details about my cats. I could write a config file like follows,

`config.py`

```Python
from datetime import datetime

cats = [
  {'name' : 'Mittens', 'age' : 18},
  {'name' :     'Bob', 'age' :  4}
]

owner = {
  'name'     : 'Config Uratii',
  'address'  : "1234 Python Dr.",
  'birthday' : datetime(1970, 1, 1).isoformat()
}
```

To use this configuration, all I need to do is call `configurati.configure` in
my code...

`application.py`

```Python
from pprint import pprint
from configurati import configure

if __name__ == '__main__':
  pprint(configure())
```

...and tell it which configuration file to use from the command line,

```bash
$ python application.py \
  --config config.py
```

But that's not quite right. I misspelled my name, and today is Bob's birthday!

```bash
$ python application.py         \
  --config config.py            \
  "--owner.name" "Config Urati" \
  "--cats[1].age" "5"
```

Oh, and I forgot about my dogs!

```bash
$ python application.py         \
  --config config.py            \
  "--owner.name" "Config Urati" \
  "--cats[1].age" "5"           \
  "--dogs[0]" '{"name": "Sir Barks-a-lot", "age": 15}'
```

Actually, I don't like defining configuration files in Python. Let me do it in
a more language-agnostic format,

`config.yaml`

```yaml
cats:
- name: "Mittens"
  age: 18
- name: "Bob"
  age: 4

owner:
  name: "Config Uratii"
  address: "1234 Python Dr."
  "birthay": "`from datetime import datetime; datetime(1970, 1, 1).isoformat()`"
```

When I load this file with configurati, all text in backticks will be
evaluated, but what if I want to use it in another language? I need to see the
real output!

```bash
$ python -m configurati.interpolate config.yaml > clean_config.yaml
```

Finally! Configuration complete. Now Let's actually use it!

`application.py`

```Python
from configurati import configure

if __name__ == '__main__':
  c = configure()

  # using bracket notation
  c['cats'][0]['age']   # 18

  # ...dot notation
  c.dogs[0].name        # "Sir Barks-a-lot"

  # ...fancy bracket notation
  c['cats[0].age']      # guess what...18
```

...and that's `configurati`!


# Configuration Files

# Configuration Specifications

# `configurati.attrs`
