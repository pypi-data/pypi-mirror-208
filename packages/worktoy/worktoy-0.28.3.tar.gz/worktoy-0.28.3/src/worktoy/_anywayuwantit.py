"""AnywayUWantIt provides a simplified abstract metaclass"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from _py_abc import ABCMeta
from abc import ABCMeta as ABCMetaLOL
from typing import Any

_modules = [ABCMetaLOL]


class AnywayUWantIt(ABCMeta):
  """AnywayUWantIt provides a simplified abstract metaclass"""

  def __new__(mcls, *args, **kwargs) -> ABCMeta:
    cls = super().__new__(mcls, *args, **kwargs)
    return cls

  def __instancecheck__(cls, instance: Any = None) -> bool:
    """On the subclass, implement a function named 'recognizeInstance' to
    explicitly define if an instance is to be regarded as an instance of
    it."""
    if instance == cls:
      return True
    if instance is None:
      return True
    recognizeInstance = getattr(cls, 'recognizeInstance', None)
    if recognizeInstance is None:
      return super().__instancecheck__(instance)
    return recognizeInstance(instance)
