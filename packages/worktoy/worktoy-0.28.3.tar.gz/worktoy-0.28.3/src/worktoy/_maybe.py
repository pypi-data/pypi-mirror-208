"""The None-aware 'maybe' implements the null-coalescence behaviour."""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import Any


def maybe(*args) -> Any:
  """The None-aware 'maybe' implements the null-coalescence behaviour.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  for arg in args:
    if arg is not None:
      return arg
  return None
