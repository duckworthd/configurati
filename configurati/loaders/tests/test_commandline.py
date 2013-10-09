import unittest

from configurati.loaders.commandline import *
from configurati.utils import Missing


class NextTests(unittest.TestCase):

  def test_space_separated(self):
    assert next(["--key", "value"]) == ("key", "value", [])

  def test_equals_separated(self):
    assert next(["--key=value"]) == ("key", "value", [])

  def test_json_value(self):
    assert next(["--key", '{"a": 1}']) == ("key", {'a': 1}, [])


class LoadTests(unittest.TestCase):

  def test_simple(self):
    assert load(["--a", "1"]) == {"a": 1}

  def test_multiple(self):
    assert load(["--a", "1", "--b=cde"]) == {"a": 1, "b": "cde"}

  def test_nested_object(self):
    assert load(["--a.b", "1"]) == {"a": {"b": 1}}

  def test_nested_object2(self):
    # XXX shouldn't this be {"a": {"b": [Missing, 1]}} ?
    assert load(["--a.b[1]", "1"]) == {"a": {"b": [Missing, 1]}}
