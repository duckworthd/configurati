import tempfile
import os

from nose.tools import raises

import configurati
from configurati import ValidationError, required, optional


def write_and_load(args=[], config_text=None, spec_text=None):
  """Write config/spec files to disk and run configure"""
  def remove_leading_spaces(text):
    if text:
      return "\n".join(line.strip() for line in text.split("\n"))

  def write(text):
    if text is not None:
      file = tempfile.NamedTemporaryFile(delete=False)
      file.write(text)
      file.flush()
      return file.name

  # remove leading spaces
  config_text = remove_leading_spaces(config_text)
  spec_text   = remove_leading_spaces(spec_text)

  # write config, spec file to disk
  config_path = write(config_text)
  spec_path   = write(spec_text)

  # run configuration
  config = configurati.configure(
      args,
      config_path=config_path,
      spec_path=spec_path
  )

  # cleanup
  if config_path:
    os.remove(config_path)
  if spec_path:
    os.remove(spec_path)

  return config


def test_basic_config():
  config_text = (
    """
    a = 1     # int
    b = "2"   # str
    c = 3.14  # float
    """
  )

  config = write_and_load(config_text=config_text)

  assert config.a == 1
  assert config.b == "2"
  assert config.c == 3.14


def test_global_config():
  config_text = (
    """
    a = 1     # int
    b = "2"   # str
    c = 3.14  # float
    """
  )

  write_and_load(config_text=config_text)
  config = configurati.CONFIG()

  assert config.a == 1
  assert config.b == "2"
  assert config.c == 3.14


def test_collection_config():
  config_text = (
    """
    a = [1,2,3]
    b = (3,4,5)
    c = {"six": 6, "seven": 7, "eight-nine": 89}
    """
  )

  config = write_and_load(config_text=config_text)

  assert config.a == [1,2,3]
  assert config.b == (3,4,5)
  assert config.c.six == 6
  assert config.c.seven == 7
  assert config.c.eight_nine == 89


def test_env():
  os.environ["TEST"] = "yeah"
  config_text = (
    """
    from configurati import env
    a = env("TEST")
    """
  )

  config = write_and_load(config_text=config_text)

  assert config.a == "yeah"


def test_command_line_override():
  config_text = (
    """
    a = 1     # int
    b = {
      'c': [1,2,3],
      'd': 'hello'
    }
    """
  )

  config = write_and_load(["--a", "2", "--b.c[-1]", "5", "--b.c.-2", "100"], config_text=config_text)

  assert config.a == 2
  assert config.b.c[-1] == 5
  assert config.b.c[-2] == 100


def test_variable():
  spec_text = (
      """
      from configurati import required, optional

      a = required(type=int)
      b = optional(type=float, default=1.0)
      """
  )
  config_text = (
      """
      a = 1
      b = "2.0"
      """
  )
  config = write_and_load(config_text=config_text, spec_text=spec_text)

  assert config.a == 1
  assert config.b == 2.0


@raises(configurati.ValidationError)
def test_missing_required():
  spec_text = (
      """
      from configurati import required, optional

      a = required(type=int)
      b = optional(type=float, default=1.0)
      """
  )
  config_text = (
      """
      # a = 1
      b = "2.0"
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)


def test_missing_optional():
  spec_text = (
      """
      from configurati import required, optional

      a = required(type=int)
      b = optional(type=float, default=1.0)
      """
  )
  config_text = (
      """
      a = 1
      # b = "2.0"
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)

  assert config.a == 1
  assert config.b == 1.0


def test_list_spec():
  spec_text = (
      """
      from configurati import required, optional

      a = [required(type=int)]
      """
  )
  config_text = (
      """
      a = [1, "2", 3.0]
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)

  assert config.a == [1,2,3]


def test_tuple_spec_correct():
  spec_text = (
      """
      from configurati import required, optional

      a = (required(type=int), required(type=str))
      """
  )
  config_text = (
      """
      a = (1, 2)
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)

  assert config.a == (1, "2")


@raises(ValidationError)
def test_tuple_spec_invalid_length():
  spec_text = (
      """
      from configurati import required, optional

      a = (required(type=int), required(type=str))
      """
  )
  config_text = (
      """
      a = (1, 2, 3)
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)


def test_dict_correct():
  spec_text = (
      """
      from configurati import required, optional

      a = {
        'b': required(type=str),
        'c': optional(type=float, default=-1.0),
      }
      """
  )
  config_text = (
      """
      a = {
        'b': 1.0,
        'c': "2.0"
      }
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)

  assert config.a == {'b': "1.0", 'c': 2.0}


@raises(ValidationError)
def test_dict_missing_required_key():
  spec_text = (
      """
      from configurati import required, optional

      a = {
        'b': required(type=str),
        'c': optional(type=float, default=-1.0),
      }
      """
  )
  config_text = (
      """
      a = {
        # 'b': 1.0,
        'c': "2.0"
      }
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)


def test_dict_missing_optional_key():
  spec_text = (
      """
      from configurati import required, optional

      a = {
        'b': required(type=str),
        'c': optional(type=float, default=-1.0),
      }
      """
  )
  config_text = (
      """
      a = {
        'b': 1.0,
        # 'c': "2.0"
      }
      """
  )

  config = write_and_load(config_text=config_text, spec_text=spec_text)

  assert config.a.b == "1.0"
  assert config.a.c == -1.0


def test_load_config():
  config = configurati.load_config(
      'sample_config.py',
      relative_to_caller=True
  )
  assert config['a'] == 1
  assert config['c']['d'] == 'abc'
  assert config['c']['e'] == []


def test_import_config():
  configurati.import_config('sample_config.py')

  assert a == 1
  assert c['d'] == 'abc'
  assert c['e'] == []


def test_load_spec():
  spec = configurati.load_spec(
      'sample_spec.py',
      relative_to_caller=True
  )

  assert spec['a'] == required(type=int)
  assert spec['b'] == optional(type=float, default=1.0)
  assert spec['c']['d'] == required(type=str)
  assert spec['c']['e'] == [required(type=str)]


def test_import_spec():
  configurati.import_spec(
      'sample_spec.py',
      relative_to_caller=True
  )

  assert a == required(type=int)
  assert b == optional(type=float, default=1.0)
  assert c['d'] == required(type=str)
  assert c['e'] == [required(type=str)]
