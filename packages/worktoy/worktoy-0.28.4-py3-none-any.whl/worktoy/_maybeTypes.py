"""The maybeTypes function finds all arguments of given type"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from typing import Any

from worktoy import searchKeys


def maybeTypes(type_, *args, **kwargs) -> list[Any]:
  """The maybeTypes function finds all arguments of given type"""
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen

  out = []
  for arg in args:
    if isinstance(arg, type_):
      out.append(arg)

  padLen = searchKeys('pad', 'padLen') @ int >> kwargs
  if padLen is None or padLen == len(out):
    return out
  if padLen < len(out):
    return out[:padLen]
  padChar = searchKeys('padChar') >> kwargs
  while len(out) < padLen:
    out.append(padChar)
  return out
