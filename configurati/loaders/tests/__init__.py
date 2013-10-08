from StringIO import StringIO
import os
import unittest


class LoadTests(object):
  """Test a load-from-file module"""

  def test_load(self):
    o = {
      'a': "`import os; os.getcwd()`",
      'b': {
        'c': [1,2,3],
        'd': "abc"
      }
    }

    # write to fake file
    s = StringIO()
    s.name = "test." + self.extension
    self.dumpfunc(o, s)
    s.seek(0)

    # load from file
    o2 = self.loadfunc(s)

    assert o2['a'] == os.getcwd()
    assert o2['b'] == o['b']
