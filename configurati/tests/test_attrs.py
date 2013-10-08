import unittest

from configurati.attrs import attrs


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

  def test_setattr(self):
    self.a.c = 1
    self.assertEqual(self.a.c, 1)

  def test_getitem(self):
    self.assertEqual(self.a['b']['c'], [1,2,3])

  def test_setitem(self):
    self.a['b'] = 1
    self.assertEqual(self.a.b, 1)
