"""Testing the maybeType"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import NoReturn
import unittest

from worktoy import maybeType


class TestMaybeType(unittest.TestCase):
  """A class that defines the testcases to check the implementation of
  `maybeType`."""

  def test_maybeType_correct_type(self) -> NoReturn:
    """Test that the function returns the first argument of the specified
    type when it exists."""
    self.assertEqual(maybeType(int, 1, '2', None, 3), 1)
    self.assertEqual(maybeType(str, None, 2, 'hello', {}, []), 'hello')

  def test_maybeType_incorrect_type(self) -> NoReturn:
    """Test that the function returns None when no argument of the
    specified type is found."""
    self.assertEqual(maybeType(float, 1, 2.0, '', None), 2.0)
    self.assertIsNone(maybeType(list, 1, '2', None, {}))
    self.assertIsNone(maybeType(complex, 1, 2.0, '', None))

  def test_maybeType_empty_args(self) -> NoReturn:
    """Test that the function returns None when no arguments are given."""
    self.assertIsNone(maybeType(str))
