import unittest

from configurati.validation import *
from configurati.validation import _validate


class ValidateRequiredTests(unittest.TestCase):

  def test_failed_coercion(self):
    self.assertRaises(ValidationError, validate_required, required(type=int), "a")

  def test_missing(self):
    self.assertRaises(ValidationError, validate_required, required(), Missing)

  def test_successful(self):
    self.assertEqual(validate_required(required(type=int), "123"), 123)


class ValidateOptionalTests(unittest.TestCase):

  def test_missing(self):
    o = optional(type=int, default="123")
    self.assertEqual(validate_optional(o, Missing), 123)

  def test_given(self):
    o = optional(type=int, default="123")
    self.assertEqual(validate_optional(o, "456"), 456)

  def test_spec_in_type(self):
    s = optional(
        type={
          'a': required(type=int),
          'b': required(type=str),
        },
        default={
          'a': "1",
          'b': "two"
        }
      )

    # if Missing, then full default is used
    self.assertEqual(validate_optional(s, Missing), {'a': 1, 'b': "two"})

    # if not missing, then apply spec
    self.assertRaises(ValidationError, validate_optional, s, {"a": "1"})


class ValidateDictTests(unittest.TestCase):

  def test_optional_children(self):
    s = {
        'a': optional(default=1),
        'b': {
          'ba': optional(default=2),
          'bb': optional(default=3)
        }
      }
    o = {
        'b': {
          'bb': -3
        }
      }
    r = {
        'a': 1,
        'b': {
          'ba': 2,
          'bb': -3,
        }
      }
    r2 = {
        'a': 1,
        'b': {
          'ba': 2,
          'bb': 3
        }
      }

    # nested substitution with defaults
    self.assertEqual(validate_dict(s, o), r)

    # complete substitution with Missing
    self.assertEqual(validate_dict(s, Missing), r2)

  def test_required_children(self):
    s = {
        'a': required(),
        'b': {
          'ba': required(),
          'bb': optional(default=3)
        }
      }
    o = {
        'b': {
          'ba':  1,
          'bb': -3
        }
      }

    # missing first level required
    self.assertRaises(ValidationError, validate_dict, s, o)

    # missing second level required
    o['a'] = 1
    del o['b']['ba']
    self.assertRaises(ValidationError, validate_dict, s, o)

    # all required fulfilled, no optionals
    o['b']['ba'] = 2
    del o['b']['bb']
    r = {
        'a': 1,
        'b': {
          'ba': 2,
          'bb': 3
        }
      }
    self.assertEqual(validate_dict(s, o), r)

  def test_invalid_config_type(self):
    # only Missing_ or dict are acceptable config types
    self.assertRaises(ValidationError, validate_dict, {}, "asdf")

  def test_non_spec_objects_in_spec(self):
    s = {
        'a': 1,
        'b': {
          'ba': optional(type=int, default=2),
          'bb': required(type=int)
        }
      }
    o = {
        'a': "one",
        'b': {
          'bb': 3
        }
      }
    r = {
        'b': {
          'ba': 2,
          'bb': 3,
        }
      }
    self.assertEqual(validate_dict(s, o), r)


class ValidateListTests(unittest.TestCase):

  def test_too_many_content_specs(self):
    s = [required(type=int), required(type=str)]
    self.assertRaises(ValidationError, validate_list, s, [])

  def test_missing(self):
    s = [required(type=int)]
    self.assertEqual(validate_list(s, Missing), [])

  def test_invalid_config(self):
    s = [required(type=int)]
    o = [1, 2, "ha"]
    self.assertRaises(ValidationError, validate_list, s, o)

  def test_invalid_config_type(self):
    self.assertRaises(ValidationError, validate_list, [], 1)

  def test_successful(self):
    s = [required(type=int)]
    o = [1, 2.0, "3"]
    self.assertEqual(validate_list(s, o), [1, 2, 3])
    for i in validate_list(s, o):
      self.assertIsInstance(i, int)


class ValidateTupleTests(unittest.TestCase):

  def test_too_long(self):
    s = (required(), required())
    self.assertRaises(ValidationError, validate_tuple, s, (1, 2, 3))

  def test_too_short(self):
    s = (required(), optional(default=2))
    self.assertEquals(validate_tuple(s, (1,)), (1, 2))


  def test_optional_children(self):
    s = (optional(type=int, default=1), optional(type=int, default=2))
    o = (Missing, "-2")
    self.assertEqual(validate_tuple(s, o), (1, -2))
    self.assertEqual(validate_tuple(s, Missing), (1, 2))

  def test_required_children(self):
    s = (required(type=int), optional(type=int, default=2))
    o = (Missing, "-2")
    self.assertRaises(ValidationError, validate_tuple, s, o)

    o = (1, Missing)
    self.assertEqual(validate_tuple(s, o), (1, 2))

  def test_invalid_config_type(self):
    s = (required(type=int),)
    self.assertRaises(ValidationError, validate_tuple, s, 1)


class ValidateTests(unittest.TestCase):

  def setUp(self):
    import os
    self.s = {
        'os': os,
        'version': (
          optional(type=int, default=0),
          optional(type=str, default="SNAPSHOT")
        ),
        'node': optional(
          type={
            'host': required(type=str),
            'port': optional(type=int, default=8888),
          },
          default={
            'host': 'localhost'
          }
        ),
        'sns': [
          {
            'topic': required(type=str),
            'enabled': optional(type=bool, default=False)
          }
        ],
      }

  def test_empty(self):
    o = {}
    r = {
        'version': (0, "SNAPSHOT"),
        'node': { 'host': 'localhost', 'port': 8888 },
        'sns': []
      }
    self.assertEqual(_validate(self.s, o), r)

  def test_invalid_list_entry(self):
    o = {
        'sns': [
          {'topic': 'one', 'enabled': True},
          {'topic': 'two'},
          {},
        ]
      }

    self.assertRaises(ValidationError, _validate, self.s, o)

  def test_missing_in_tuple(self):
    o = {
        'version': (Missing, 'RELEASE')
      }
    self.assertEqual(_validate(self.s, o)['version'], (0, "RELEASE"))

  def test_nonspec_in_spec(self):
    r = _validate(self.s, {})
    self.assertNotIn('os', r)

  def test_extra_config(self):
    r = _validate(self.s, {'unimportant': True})
    self.assertNotIn('unimportant', r)

  def test_no_validator(self):
    self.assertRaises(ValidationError, _validate, 1, Missing)
