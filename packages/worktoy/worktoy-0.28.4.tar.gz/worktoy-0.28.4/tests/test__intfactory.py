"""Testing the integer factory"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from cmath import pi
from typing import NoReturn
from unittest import TestCase

from worktoy.mockdata import intFactory


class TestIntFactory(TestCase):
  """Testing the integer factory"""

  def setUp(self, ) -> NoReturn:
    """Sets up the tests"""
    self.factory = intFactory()

  def testBasic(self) -> int:
    """Tests for basic functionality"""
    val = self.factory >> (2 ** 31, 2 ** 32 - 1)
    self.assertLess(val, 2 ** 32 - 1)
    self.assertGreaterEqual(val, 2 ** 31)

  def testCoPrime(self) -> NoReturn:
    """This test ensures that the integers returned are in fact randomly
    distributed.
    The probability that two stochastic variables of unbounded scale
    and uniform distribution across the positive integers are co-prime,
    that is, having greatest common divisor equal to 1, is equal to:
      6 / pi**2.
    This value is the value of the Riemann Zeta-function evaluated at 2"""
    p = self.factory.coPrimeTest(100)
    self.assertLess((p - 6 / pi / pi) ** 2, 0.05)
