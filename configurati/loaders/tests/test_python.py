import os
from tempfile import NamedTemporaryFile as NTF
import unittest

from configurati.loaders.python import load


class PythonLoadTests(unittest.TestCase):

  def test_load(self):
    s = "\n".join([
      "import os",
      "a = os.getcwd()",
      "b = {",
      "   'c': [1,2,3],",
      "   'd': 'abc'",
      "  }",
    ])

    with NTF(suffix='.py') as f:
      # write to file
      f.write(s)
      f.flush()
      f.seek(0)

      # load it
      o2 = load(f)

      assert o2['a'] == os.getcwd()
      assert o2['b'] == {"c": [1,2,3], "d": "abc"}
