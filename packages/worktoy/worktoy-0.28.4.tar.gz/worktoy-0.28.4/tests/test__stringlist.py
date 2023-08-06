"""Testing stringList function """
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import NoReturn
from unittest import TestCase

from loremify import lorem

from worktoy import stringList


class TestStringList(TestCase):
  """Testing stringList function
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  def testBasics(self) -> NoReturn:
    """Testing the basic functionalities"""
    base = stringList('one, two, three, four')
    self.assertEqual(base, ['one', 'two', 'three', 'four'])

  def testIgnore(self) -> NoReturn:
    """Testing the use of the ignore flags"""
    base = stringList('one, two@, three, four')
    self.assertEqual(base, ['one', 'two, three', 'four'])

  def testIgnoreLorem(self) -> NoReturn:
    """Testing the number of commas compared to length of resulting list."""
    base = lorem()
    baseList = stringList(base, )
    self.assertEqual(base.count(','), len(baseList) - 1)

  def testIgnoreSingle(self, ) -> NoReturn:
    """Testing one character separator and ignores"""
    base = stringList('One | Two | Three @| Seven Halves | Four', '|', '@')
    self.assertEqual(base, ['One ', ' Two ', ' Three | Seven Halves ',
                            ' Four', ])

  def testIgnoreSingleIgnoreMultiSplit(self, ) -> NoReturn:
    """Testing single character ignore flag with multi character separator"""
    base = stringList('One | Two | Three@ | Seven Halves | Four', ' | ', '@')
    self.assertEqual(base, ['One', 'Two', 'Three | Seven Halves', 'Four', ])

  def testIgnoreMultiIgnoreSingleSplit(self, ) -> NoReturn:
    """Testing multi character ignore flag with single character
    separator."""
    base = stringList('A<>1<>B<>2@<>C<>3', '<>', '@')
    res = ['A', '1', 'B', '2<>C', '3']
    self.assertEqual(base, res)
