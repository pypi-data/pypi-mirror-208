"""This abstract metaclass registers any callable object as an instance."""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import Any, NoReturn

from worktoy import AnywayUWantIt, searchKeys, maybeType, maybe


class CallMeMaybe(metaclass=AnywayUWantIt):
  """This abstract metaclass registers any callable object as an instance."""

  _explicits = []
  _callables = []
  _unCallables = []

  @staticmethod
  def recognizeInstance(instance: Any = None) -> bool:
    """Recognizing anything callable as an instance"""
    callableFlag = getattr(instance, '__isCallable__', None)
    if callableFlag is not None:
      if not callableFlag:
        return False
    if isinstance(instance, (int, float, str, complex)):
      return False
    if isinstance(instance, (tuple, dict, list, set)):
      return False
    for callableType in CallMeMaybe._callables:
      if isinstance(instance, callableType):
        return True
    for callableType in CallMeMaybe._unCallables:
      if isinstance(instance, callableType):
        return False
    if instance is None:
      return False
    classId = getattr(instance, '__class__', None)
    instanceName = getattr(instance, '__name__', None)
    if instanceName is None:
      e = """Unable to recognize instance name"""
      raise ValueError(e)
    if classId is None:
      e = """Unable to recognize class of instance"""
      raise ValueError(e)
    className = getattr(classId, '__name__', None)
    if className is None:
      e = """Unable to recognize name of instance class"""
      raise ValueError(e)
    if className == 'builtin_function_or_method':
      return True
    if className == 'function':
      return True
    callFunc = getattr(instance, '__call__', None)
    if callFunc is None:
      return False
    if callFunc is not None:
      return True

  @classmethod
  def registerUnCallable(cls, other: type) -> NoReturn:
    """Registers other type as being explicitly not callable"""
    cls._unCallables.append(other)

  @classmethod
  def registerCallable(cls, other: type) -> NoReturn:
    """Registers other type as being explicitly callable"""
    cls._callables.append(other)

  def __init__(self, *args, **kwargs) -> None:
    callableKwarg = searchKeys('callable', 'callMeMaybe') @ bool >> kwargs
    callableArg = maybeType(str, *args)
    if callableArg is not None:
      if callableArg == 'callable':
        callableArg = True
      elif callableArg in ['Not-callable', 'not callable']:
        callableArg = False
    callableDefault = True
    self._callableFlag = maybe(callableKwarg, callableArg, callableDefault)

  def __call__(self, func: Any) -> Any:
    """Use as a function decorator. By default, the decorated function are
    regarded as callable. Change this by setting keyword argument
    'callable' to False so that a decorated function will not be regarded
    as a callable. """
    if isinstance(func, type):
      if maybe(self._callableFlag, True):
        CallMeMaybe.registerCallable(func)
        return func
      CallMeMaybe.registerUnCallable(func)
      return func
    setattr(func, '__isCallable__', maybe(self._callableFlag, True))
    return func
