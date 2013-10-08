import unittest

from configurati.attrs import *


class AttrsTests(unittest.TestCase):

  def setUp(self):
    self.o = {
        'a': 'abc',
        'b': {
          'c': [1,2,3],
          'd': 'zyx',
        }
      }
    self.a = attrs({
        'a': 'abc',
        'b': attrs({
          'c': [1,2,3],
          'd': 'zyx',
        })
      })

  def test_from_dict(self):
    a = attrs.from_dict(self.o)
    self.assertIsInstance(a, attrs)
    self.assertIsInstance(a['b'], attrs)
    self.assertIsInstance(a['b']['c'], list)

  def test_getattr(self):
    self.assertEqual(self.a.b, self.a['b'])

  def test_getattr_nested(self):
    self.assertEqual(self.a.b.c[2], 3)

  def test_setattr(self):
    self.a.c = 1
    self.assertEqual(self.a.c, 1)

  def test_setattr_dict(self):
    self.a.x = {'a': 1, 'b': 2}
    self.assertEqual(self.a.x.a, 1)

  def test_getitem(self):
    self.assertEqual(self.a['b']['c'], [1,2,3])

  def test_getitem_nested(self):
    self.assertEqual(self.a['b.c[2]'], self.a['b']['c'][2])

  def test_setitem(self):
    self.a['b'] = 1
    self.assertEqual(self.a.b, 1)

  def test_setitem_nested(self):
    self.a['x.y.z'] = 1
    self.assertEqual(self.a['x'], attrs.from_dict({'y': {'z': 1}}))


class NextKeyTests(unittest.TestCase):

  def test_period_then_brackets(self):
    assert next_key(".a-b-c123[0]") == ("a_b_c123",  "[0]")

  def test_period_then_period(self):
    assert next_key( ".a-b-c123.b") == ("a_b_c123",   ".b")

  def test_bracket_then_period(self):
    assert next_key(     "[5].abc") == (         5, ".abc")

  def test_bracket_then_bracket(self):
    assert next_key(      "[5][3]") == (         5,  "[3]")


class GetTests(unittest.TestCase):

  def setUp(self):
    self.o = {
      'a': {
        'b': [1, 2, 3],
        'c': (9, 8, 7, 6)
      },
      'd': "def"
    }

  def test_dot(self):
    assert get(self.o, ".d") == "def"

  def test_dot_and_bracket(self):
    assert get(self.o, ".a.b[1]") == 2

  def test_tuple(self):
    assert get(self.o, ".a.c[1]") == 8

  def test_empty_string(self):
    assert get(self.o, "") == self.o

  def test_build(self):
    assert get(self.o, ".a.z", build=True) == {}

  def test_remaining_key(self):
    self.assertRaises(KeyError, get, self.o, ".a.b.c")

  def test_short_list(self):
    self.assertRaises(KeyError, get, self.o, ".a.b[5]")


class SetTests(unittest.TestCase):

  def setUp(self):
    self.o = {
      'a': {
        'b': [1, 2, 3],
        'c': (9, 8, 7, 6)
      },
      'd': "def"
    }

  def test_dot(self):
    set(self.o, ".d", 100)
    assert self.o['d'] == 100

  def test_dot_and_bracket(self):
    set(self.o, ".a.b[2]", 100)
    assert self.o['a']['b'][2] == 100

  def test_tuple(self):
    set(self.o, ".a.c[2]", 100)
    assert self.o['a']['c'][2] == 100

  def test_build(self):
    set(self.o, ".a.d", 100, build=True)
    assert self.o['a']['d'] == 100

  def test_remaining_key(self):
    self.assertRaises(KeyError, set, self.o, ".a.b.c", 1)

  def test_short_list(self):
    set(self.o, ".a.b[5]", 1)
    assert self.o['a']['b'][5] == 1
