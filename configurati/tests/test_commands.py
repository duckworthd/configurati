from contextlib import contextmanager
from tempfile import NamedTemporaryFile as NTF
import unittest

from configurati.commands import *
from configurati.validation import required, optional


class CommandsTest(unittest.TestCase):

  def setUp(self):
    self.config_text = "\n".join([
        """a = 1.0""",
        """# b = 2.0""",
        """c = {""",
        """    'd': 'abc',""",
        """    'e': []""",
        """}""",
      ])

    self.spec_text = "\n".join([
        """from configurati import required, optional""",
        """a = required(type=int)""",
        """b = optional(type=float, default=1.0)""",
        """c = {""",
        """  'd': required(type=str),""",
        """  'e': [required(type=str)]""",
        """}""",
      ])

  def test_env(self):
    import os
    os.environ["TEST"] = "yeah"

    config_text = "\n".join([
      """from configurati import env""",
      """a = env("TEST")"""
    ])

    with save(config_text) as config:
      self.assertEqual(config.a, "yeah")

  def test_load_config(self):
    with save(self.config_text, loadfunc=load_config) as config:
      self.assertEqual(config.a, 1)
      self.assertEqual(config.c.d, 'abc')
      self.assertEqual(config.c.e, [])

  def test_import_config(self):
    with NTF(suffix='.py') as f:
      f.write(self.config_text)
      f.flush()
      import_config(f.name)

      self.assertEqual(a, 1)
      self.assertEqual(c.d, 'abc')
      self.assertEqual(c.e, [])

  def test_load_spec(self):
    with save(self.spec_text, load_spec) as spec:
      self.assertEqual(spec.a, required(type=int))
      self.assertEqual(spec.b, optional(type=float, default=1.0))
      self.assertEqual(spec.c.d, required(type=str))
      self.assertEqual(spec.c.e, [required(type=str)])

  def test_import_spec(self):
    with NTF(suffix='.py') as f:
      f.write(self.spec_text)
      f.flush()
      import_spec(f.name)

      self.assertEqual(a, required(type=int))
      self.assertEqual(b, optional(type=float, default=1.0))
      self.assertEqual(c.d, required(type=str))
      self.assertEqual(c.e, [required(type=str)])


@contextmanager
def save(text, loadfunc=load_config):
  """Write and load configuration file"""
  with NTF(suffix=".py") as f:
    f.write(text)
    f.flush()
    yield loadfunc(f.name)
