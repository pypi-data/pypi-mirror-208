"""Testing the maybe function"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import NoReturn
import unittest

from worktoy import maybe


class TestMaybe(unittest.TestCase):
  def testMaybeReturnsNoneIfAllArgsAreNone(self) -> NoReturn:
    """Test that the maybe function returns None if all input arguments
    are None."""

    self.assertIsNone(maybe(None, None, None))

  def testMaybeReturnsFirstArgNotNone(self) -> NoReturn:
    """Test that the maybe function returns the first non-None argument."""

    self.assertEqual(maybe(None, "foo", "bar"), "foo")
    self.assertEqual(maybe(None, None, "baz", None), "baz")
    self.assertEqual(maybe(0, 1, None), 0)
