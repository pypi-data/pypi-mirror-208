"""The intFactory generates random integers"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from random import randint
from typing import NoReturn

from worktoy import maybeTypes, maybe


class _IntFactory:
  """The intFactory generates random integers
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  _singleTon = None
  _numbers = []

  @classmethod
  def intFactory(cls, *args, **kwargs) -> _IntFactory:
    """Integer factory function"""
    if _IntFactory._singleTon is None:
      _IntFactory._singleTon = cls(*args, **kwargs)
      return _IntFactory.intFactory()
    lower, upper = _IntFactory._parseLimits(*args, **kwargs)
    _IntFactory._singleTon.setUpper(upper)
    _IntFactory._singleTon.setLower(lower)
    return _IntFactory._singleTon

  @staticmethod
  def _parseLimits(*args, **kwargs) -> tuple[int, int]:
    """Parses the arguments to upper and lower limits"""
    intArgs = maybeTypes(int, *args, padLen=2, padChar=None)
    lowerKwarg = kwargs.get('lower', **kwargs)
    upperKwarg = kwargs.get('upper', **kwargs)
    lowerArg, upperArg = intArgs
    lowerDefault, upperDefault = 0, 2 ** 16 - 1
    _lower = maybe(lowerKwarg, lowerArg, lowerDefault)
    _upper = maybe(upperKwarg, upperArg, upperDefault)
    return (_lower, _upper)

  @staticmethod
  def gcd(a: int, b: int) -> int:
    """Greatest common divisor"""
    if max([a, b]) % min([a, b]):
      return _IntFactory.gcd(min([a, b]), max([a, b]) % min(a, b))
    else:
      return min([a, b])

  def __init__(self, *args, **kwargs) -> None:
    self._lower, self._upper = self._parseLimits(*args, **kwargs)

  def _getUpper(self) -> int:
    """Getter-function for upper limit"""
    return self._upper

  def setUpper(self, upper: int) -> NoReturn:
    """Setter-function for upper limit"""
    self._upper = upper

  def _getLower(self) -> int:
    """Getter-function for lower limit"""
    return self._lower

  def setLower(self, lower: int) -> NoReturn:
    """Setter-function for lower limit"""
    self._lower = lower

  def coPrimeTest(self, n: int = None) -> float:
    """Collects n unique instances. """
    n = maybe(n, 16)
    while len(self._numbers) < n:
      self.getNumber()
    coPrime = 0
    notCoPrime = 0
    count = 0
    for innerNumber in sorted(self._numbers):
      for outerNumber in sorted(self._numbers):
        if innerNumber < outerNumber:
          count += 1
          if self.gcd(innerNumber, outerNumber) == 1:
            coPrime += 1
          else:
            notCoPrime += 1
    return coPrime / max([count, 0])

  def getNumber(self) -> int:
    """Getter-function for number"""
    number = randint(self._getLower(), self._getUpper())
    self._numbers.append(number)
    return number

  def __rshift__(self, other: tuple | list) -> int:
    """Returns a single new number in the given range"""
    intArgs = maybeTypes(int, *other, padLen=2, padChar=None)
    a, b = intArgs
    a = maybe(a, self._getLower())
    b = maybe(b, self._getUpper())
    return randint(a, b)

  def __len__(self, ) -> int:
    """The length of the instance is taken to mean the length of the list
    of numbers so far obtained."""
    return len(self._numbers)

  def __call__(self, *args, **kwargs) -> list[int]:
    """Calling the instance returns a sample of sampleSize given as a
    positional argument or at the keyword argument sampleSize."""


_intFactory = _IntFactory.intFactory
