"""Testing the strFactory function"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

import string
from typing import NoReturn
from unittest import TestCase

from worktoy.mockdata import strFactory


class TestStrFactory(TestCase):
  """Testing the strFactory function
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  @staticmethod
  def getAllChars() -> list[str]:
    """Getter-function for all chars"""
    return [char for char in string.ascii_letters + string.digits]

  @staticmethod
  def getAllExcept(*char: str) -> list[str]:
    """Getter-function for a list all characters except those given."""
    allChars = TestStrFactory.getAllChars()
    return [c for c in allChars if c not in [cc for cc in char]]

  def testStrFactory(self, ) -> NoReturn:
    """Testing the length of words"""
    for i in range(24):
      if not i:
        self.assertFalse(strFactory(i))
      else:
        self.assertEqual(len(strFactory(i)), i)

  def testException(self) -> NoReturn:
    """Testing the exception raised by passing strFactory a negative
    number"""
    self.assertRaises(ValueError)

  def testIgnoreChars(self) -> NoReturn:
    """Testing that strFactory correctly ignores given characters. """
    allChars = TestStrFactory.getAllChars()
    for char in allChars:
      ignoreChars = self.getAllExcept(char)
      testSample = strFactory(8, ignoreChars)
      for testChar in testSample:
        self.assertEqual(char, testChar)
