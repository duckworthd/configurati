from __future__ import absolute_import

import json
import unittest

from configurati.loaders.json import *
from configurati.loaders.tests import LoadTests


class JsonLoadTests(LoadTests, unittest.TestCase):

  def setUp(self):
    self.loadfunc  = load
    self.dumpfunc  = json.dump
    self.extension = "json"
