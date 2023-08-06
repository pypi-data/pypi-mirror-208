#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

import unittest

from worktoy import maybeTypes


class TestMaybeTypes(unittest.TestCase):
  """A class that defines the testcases to check the implementation of
  `maybeTypes`."""

  def testMaybeTypesCorrectType(self):
    """Test that the function correctly returns a list of all arguments of
    the specified type."""
    self.assertEqual(maybeTypes(int, 1, '2', None, 3), [1, 3])
    self.assertEqual(maybeTypes(str, None, 2, 'hello', {}, []), ['hello'])

  def testMaybeTypesEmptyArgs(self):
    """Test that the function returns an empty list when no arguments are
    given."""
    self.assertEqual(maybeTypes(int), [])

  def testMaybeTypesPadLenNone(self):
    """Test that the function returns the full list when padLen is None."""
    self.assertEqual(maybeTypes(int, 1, 2, 3), [1, 2, 3])

  def testMaybeTypesPadLenCorrectLength(self):
    """Test that the function returns a list of correct length when padLen
    is specified."""
    self.assertEqual(maybeTypes(int, 1, '2', None, 3, padLen=3),
                     [1, 3, None])

  def testMaybeTypesPadLenShorterList(self):
    """Test that the function returns the full list when padLen is less
    than the number of elements in the list."""
    self.assertEqual(maybeTypes(int, 1, 2, 3, 4, padLen=3), [1, 2, 3])

  def testMaybeTypesPadChar(self):
    """Test that the function pads the list correctly with the specified
    padding character when padLen is greater than the number of elements
    in the list."""
    self.assertEqual(maybeTypes(int, 1, 2, padLen=4, padChar=0),
                     [1, 2, 0, 0])
