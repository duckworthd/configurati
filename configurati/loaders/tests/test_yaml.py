from __future__ import absolute_import

import unittest
import yaml

from configurati.loaders.yaml import *
from configurati.loaders.tests import LoadTests


class YamlLoadTest(LoadTests, unittest.TestCase):

  def setUp(self):
    self.loadfunc  = load
    self.dumpfunc  = yaml.dump
    self.extension = "yaml"
