from contextlib import contextmanager
from tempfile import NamedTemporaryFile as NTF
import unittest

from configurati.configure import *
from configurati.utils import Missing


class ConfigureTests(unittest.TestCase):

  def setUp(self):
    self.s = "\n".join([
      ])

    self.s = """
import os

from configurati import *

version = (
  optional(type=int, default=0),
  optional(type=str, default="SNAPSHOT")
)
node = optional(
  type={
    'host': required(type=str),
    'port': optional(type=int, default=8888),
  },
  default={
    'host': 'localhost'
  }
)
sns = [
  {
    'topic': required(type=str),
    'enabled': optional(type=bool, default=False)
  }
]
"""
    self.o = """
from configurati import *

version = (Missing, "RELEASE")
sns = [
    { "topic": "one", "enabled": True },
    { "topic": "two"}
  ]
"""
    self.a = [
        "--sns[1].enabled", "true",
        "--node.host", "127.0.0.1"
      ]

  def test_configure_option(self):
    with write(self.o) as (f_config, f_spec):
      c = configure(["--config", f_config.name])
      c_ = {
          'version': (Missing, "RELEASE"),
          'sns': [
            {'topic': "one", "enabled": True},
            {'topic': "two"},
          ],
          'config': f_config.name
        }
      self.assertEqual(c['version'], c_['version'])
      self.assertEqual(    c['sns'],     c_['sns'])
      self.assertEqual( c['config'],  c_['config'])

  def test_args(self):
    c = configure(self.a)
    c_ = {
        'node': {
          'host': '127.0.0.1',
        },
        'sns': [
          Missing,
          {"enabled": True}
        ]
      }
    self.assertEqual(c, c_)

  def test_args_config(self):
    with write(self.o) as (f_config, f_spec):
      c = configure(["--config", f_config.name] + self.a)
      c_ = {
          'version': (Missing, "RELEASE"),
          'node': {'host': '127.0.0.1'},
          'sns': [
            {'topic': "one", "enabled": True},
            {'topic': "two", "enabled": True},
          ],
          'config': f_config.name,
        }

      self.assertEqual(c['version'], c_['version'])
      self.assertEqual(    c['sns'],     c_['sns'])
      self.assertEqual(   c['node'],    c_['node'])
      self.assertEqual( c['config'],  c_['config'])

  def test_spec(self):
    with write(self.o, self.s) as (f_config, f_spec):
      c = configure(["--config", f_config.name, "--spec", f_spec.name])
      c_ = {
          'version': (0, "RELEASE"),
          'node': {'host': 'localhost', 'port': 8888},
          'sns': [
            {'topic': "one", "enabled": True},
            {'topic': "two", "enabled": False},
          ]
        }
      self.assertEqual(c, c_)

  def test_args_config_spec(self):
    with write(self.o, self.s) as (f_config, f_spec):
      c = configure(self.a + ["--config", f_config.name, "--spec", f_spec.name])
      c_ = {
          'version': (0, "RELEASE"),
          'node': {'host': '127.0.0.1', 'port': 8888},
          'sns': [
            {'topic': "one", "enabled": True},
            {'topic': "two", "enabled": True},
          ]
        }
      self.assertEqual(c, c_)


@contextmanager
def write(config="", spec=""):
  with NTF(suffix=".py") as f_config:
    with NTF(suffix=".py") as f_spec:
      f_config.write(config)
      f_config.flush()
      f_config.seek(0)

      f_spec.write(spec)
      f_spec.flush()
      f_spec.seek(0)

      yield (f_config, f_spec)
