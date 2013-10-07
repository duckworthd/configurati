import unittest

from configurati.utils import *


class UpdateTests(unittest.TestCase):

  def setUp(self):
    self.o2 = {
        'a': {
          'b': [1,2,3],
          'c': ('x', 'y', {'a': 'a'}),
        },
        'd': "zyx"
    }

  def test_simple(self):
    o = update({'d': "abc"}, self.o2)
    assert o['d'] == 'abc'

  def test_nested(self):
    o = update({'a': {'b': 'abc'}}, self.o2)
    assert o['a']['b'] == 'abc'

  def test_super_nested(self):
    o = update({'a': {'c': (Missing, Missing, {'b': 'b'})}}, self.o2)
    assert o['a']['c'][2]['a'] == 'a'   # dictionaries are overlaid
    assert o['a']['c'][2]['b'] == 'b'
    assert o['a']['c'][1]      == 'y'

  def test_short_list(self):
    o = update({'a': {'b': [8,Missing,Missing,5]}}, self.o2)
    assert o['a']['b'][0] == 8  # over-written
    assert o['a']['b'][1] == 2  # Missing, so not overwritten
    assert o['a']['b'][3] == 5  # list was extended

  def test_new_keys(self):
    o = update({'a': {'z': 'zyx'}}, self.o2)
    assert o['a']['z'] == 'zyx'
