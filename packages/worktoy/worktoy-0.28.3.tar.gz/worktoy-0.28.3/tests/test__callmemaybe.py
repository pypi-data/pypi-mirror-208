"""Testing CallMeMaybe"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from math import sin
from typing import NoReturn
from unittest import TestCase

from worktoy import CallMeMaybe


def func() -> NoReturn:
  """General function"""


class WishInWell:
  """Parent-class for sample class"""

  def __init__(self, *__, **_) -> None:
    self._name = None

  def _getName(self) -> str:
    """Getter-function for name"""
    return self._name

  def _setName(self, name: str) -> NoReturn:
    """Setter-function for name"""
    self._name = name
    setattr(self, '__name__', name)

  def _delName(self, *_) -> NoReturn:
    """Illegal deleter-function"""
    raise TypeError('Read only error!')

  name = property(_getName, _setName, _delName)

  def __str__(self) -> str:
    """String representation"""
    return self.name

  def __repr__(self) -> str:
    """Code representation"""
    return '%s()' % getattr(self, '__name__', 'nameLess')


class HereIsMyNumber(WishInWell):
  """This is a callable class"""

  def __init__(self, *args, **kwargs) -> None:
    WishInWell.__init__(self, *args, **kwargs)
    WishInWell._setName(self, 'I\'m callable!')

  def __call__(self, *args, **kwargs) -> NoReturn:
    """Implementation of the call"""
    print(self)


class ThisIsCrazy(WishInWell):
  """Not callable!"""

  def __init__(self, *args, **kwargs) -> None:
    WishInWell.__init__(self, *args, **kwargs)
    WishInWell._setName(self, 'I\'m not callable!')


@CallMeMaybe(callable=False)
def inCognitoFunction() -> NoReturn:
  """Callable function explicitly marked as unCallable"""


@CallMeMaybe(callable=False)
class InCognitoClass:
  """Class implementing __call__, but explicitly set to not being
  recognized by CallMeMaybe"""

  def __call__(self, *args, **kwargs) -> NoReturn:
    """f... da police!"""
    return 'f... da police!'


class TestCallMeMaybe(TestCase):
  """Testing CallMeMaybe
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  def setUp(self) -> NoReturn:
    """Sets up the tests"""
    self.callMeMaybe = CallMeMaybe()
    self.callable = HereIsMyNumber()
    self.notCallable = ThisIsCrazy()
    self.inCognitoClassInstance = InCognitoClass()
    self.inCognitoFunction = inCognitoFunction

  def testCallables(self) -> NoReturn:
    """Testing the type name of print"""
    callables = [print, func, sin, self.callable, ]
    for item in callables:
      self.assertTrue(self.callMeMaybe.recognizeInstance(item))

  def testUnCallables(self) -> NoReturn:
    """Testing objects that are not callable"""
    for item in [7, 0.7, 1 + 1j, (((),), ()), [7, 7], ]:
      self.assertFalse(self.callMeMaybe.recognizeInstance(item),
                       getattr(item, '__name__', str(item)))

    for item in [self.notCallable,
                 self.inCognitoClassInstance,
                 self.inCognitoFunction]:
      self.assertFalse(self.callMeMaybe.recognizeInstance(item),
                       getattr(item, '__name__', '%s' % item))
