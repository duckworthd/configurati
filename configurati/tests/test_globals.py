import unittest

from configurati.globals import *


class GlobalsTest(unittest.TestCase):

  def test_CONFIG(self):
    o = {
        'a': 'abc',
        'b': {
          'c': [1,2,3],
          'd': 'zyx',
        }
      }

    CONFIG(o)

    self.assertEqual(o, CONFIG())
