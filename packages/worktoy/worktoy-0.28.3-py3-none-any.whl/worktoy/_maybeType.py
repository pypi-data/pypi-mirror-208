"""The maybeType function finds the first argument of a particular type"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import Any


def maybeType(type_: type, *args) -> Any:
  """The maybeType function finds the first argument of a particular type
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  for arg in args:
    if arg is not None:
      if isinstance(arg, type_):
        return arg
  return None
