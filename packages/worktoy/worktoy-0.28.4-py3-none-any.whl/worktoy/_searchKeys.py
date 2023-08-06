"""The searchKeys function provides a flexible way of extracting values
from keyword arguments."""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import Any, NoReturn


class _SearchKeys:
  """The searchKeys function provides a flexible way of extracting values
  from keyword arguments.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  @classmethod
  def searchKeys(cls, *keys: str) -> _SearchKeys:
    """Creates a new instance on the given keys"""
    out = cls()
    out._setKeys(*keys)
    return out

  def __init__(self, ) -> None:
    self._keys = []
    self._types = []
    self._defVal = None

  def _clearKeys(self) -> NoReturn:
    """Deleter-function for the instance keys"""
    while self._keys:
      self._keys.pop()

  def _setKeys(self, *keys: str) -> NoReturn:
    """Setter-function for the instance keys"""
    self._clearKeys()
    for key in keys:
      if isinstance(key, str):
        self._keys.append(key)

  def _clearTypes(self) -> NoReturn:
    """Clears the type list"""
    while self._types:
      self._types.pop()

  def _setType(self, *type_: type) -> NoReturn:
    """Setter-function for type """
    self._clearTypes()
    for arg in type_:
      if isinstance(arg, type):
        self._types.append(arg)

  def _resetDefaultValue(self) -> NoReturn:
    """Deleter-function for default value"""
    self._defVal = None

  def _setDefaultValue(self, dV: Any) -> NoReturn:
    """Setter-function for the default value"""
    self._defVal = dV

  def _getDefaultValue(self) -> Any:
    """Getter-function for the default value"""
    return self._defVal

  def _validateByType(self, arg: Any) -> Any:
    """Returns the argument if it matches instance type. If instance type
    is None, any argument is returned."""
    if arg is None:
      return None
    if not self._types:
      return arg
    for type_ in self._types:
      if isinstance(arg, type_):
        return arg
    return None

  def _invoke(self, **kwargs) -> Any:
    """Invokes the function"""
    for key in self._keys:
      val = self._validateByType(kwargs.get(key, None))
      if val is not None:
        return val
      val = self._validateByType(kwargs.get(key.lower(), None))
      if val is not None:
        return val
    return self._getDefaultValue()

  def __matmul__(self, other: tuple[type, ...] | type) -> _SearchKeys:
    """Sets the types for this instance"""
    if isinstance(other, type):
      self._setType(other)
      return self
    self._setType(*other)
    return self

  def __rshift__(self, other: tuple[dict, Any] | dict) -> Any:
    """Evaluates the keyword arguments given. If a tuple is given,
    the first member of it are assumed to be the keyword argument
    dictionary and the second member is the default value. If a dict is
    given, no default value can be given, and the dict is processed
    directly."""
    self._resetDefaultValue()
    if isinstance(other, tuple):
      kwargs = other[0]
      if len(other) > 1:
        self._setDefaultValue(other[1])
      return self._invoke(**kwargs)
    return self._invoke(**other)


searchKeys = _SearchKeys.searchKeys
