import unittest

from configurati.loaders.utils import *


class SubstituteTest(unittest.TestCase):

  def test_no_substitution(self):
    assert substitute("abc") == "abc"

  def test_substitution(self):
    assert substitute("`1`2") == "12"

  def test_substitution_with_module(self):
    import os
    assert substitute("`import os; os.getcwd()`") == os.getcwd()
