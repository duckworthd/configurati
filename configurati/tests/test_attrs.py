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

  def test_init(self):
    a1 = attrs({'a': 1, 'b': 2})
    a2 = attrs([('a', 1), ('b', 2)])
    a3 = attrs(a=1, b=2)
    a = attrs()
    a['a'] = 1
    a['b'] = 2
    self.assertEqual(a1, a)
    self.assertEqual(a2, a)
    self.assertEqual(a3, a)

  def test_invalid_init(self):
    # keys must be strings
    self.assertRaises(KeyError, attrs, {123: 1})

    # keys cannot start with non-letters
    self.assertRaises(KeyError, attrs, {"1a": 1})
    self.assertRaises(KeyError, attrs, {"-a": 1})

  def test_from_dict(self):
    # dicts converted to attrs, others left alone
    a = attrs.from_dict(self.o)
    self.assertIsInstance(a, attrs)
    self.assertIsInstance(a['b'], attrs)
    self.assertIsInstance(a['b']['c'], list)

    # validate keys on from_dict
    self.assertRaises(KeyError, attrs.from_dict, {"a": {123: 2}})

  def test_getattr(self):
    self.assertEqual(self.a.b, self.a['b'])

  def test_getattr_nested(self):
    self.assertEqual(self.a.b.c[2], 3)

  def test_setattr(self):
    self.a.c = 1
    self.assertEqual(self.a.c, 1)

  def test_setattr_dict(self):
    # dicts get converted to attrs
    self.a.x = {'a': 1, 'b': { 'c': 2 }}
    self.assertEqual(self.a.x.a, 1)
    self.assertEqual(self.a.x.b.c, 2)

    # validate keys on setattr
    def f():
      self.a.y = {1: 2}
    self.assertRaises(KeyError, f)

  def test_getitem(self):
    # atomic keys
    self.assertEqual(self.a['b']['c'], [1,2,3])

  def test_getitem_nested(self):
    # dot and bracket notation
    self.assertEqual(self.a['b.c[2]'], self.a['b']['c'][2])

  def test_setitem(self):
    self.a['b'] = 1
    self.assertEqual(self.a.b, 1)

  def test_setitem_nested(self):
    # attrs, list construction
    self.a['x.y[1].z'] = 1
    self.assertEqual(self.a['x'], attrs.from_dict({'y': [Missing, {'z': 1}]}))

    # list extension
    self.a['b.c[5]'] = 10
    self.assertEqual(self.a['b']['c'], [1, 2, 3, Missing, Missing, 10])

  def test_contains(self):
    self.assertIn('a', self.a)
    self.assertNotIn('c', self.a)

  def test_contains_nested(self):
    self.assertIn('b.c[2]', self.a)
    self.assertNotIn('b.c.2', self.a)   # .2 isn't a valid identifier
    self.assertNotIn('b.c[3]', self.a)  # list too short
    self.assertNotIn('b.e', self.a)     # missing dict key


class NextKeyTests(unittest.TestCase):

  def test_period_then_brackets(self):
    assert next_key(".a-b-c123[0]") == ("a_b_c123",  "[0]")

  def test_period_then_period(self):
    assert next_key( ".a-b-c123.b") == ("a_b_c123",   ".b")

  def test_bracket_then_period(self):
    assert next_key(     "[5].abc") == (         5, ".abc")

  def test_bracket_then_bracket(self):
    assert next_key(      "[5][3]") == (         5,  "[3]")

  def test_invalid_key(self):
    self.assertRaises(KeyError, next_key, "a.b")

  def test_invalid_attrs_key(self):
    self.assertRaises(KeyError, next_key, ".1.a")


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

  def test_short_tuple(self):
    self.assertRaises(KeyError, set, self.o, ".a.c[4]", 1)


class ValidKeyTests(unittest.TestCase):

  def setUp(self):
    self.a = attrs({
        'a': 'abc',
        'b': attrs({
          'c': [1,2,3],
          'd': 'zyx',
        })
      })

  def test_simple(self):
    self.assertTrue(valid_key("a"))

  def test_nested(self):
    self.assertTrue(valid_key("a.b.c"))

  def test_brackets(self):
    self.assertTrue(valid_key("a[1].c"))

  def test_leading_digit(self):
    self.assertFalse(valid_key("1a"))

  def test_leading_bracket(self):
    self.assertFalse(valid_key("[1]"))

  def test_leading_period(self):
    self.assertFalse(valid_key(".a"))

  def test_non_integer_in_bracket(self):
    self.assertFalse(valid_key(".a[ha]"))
