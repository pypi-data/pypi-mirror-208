"""The strFactory function creates random strings of arbitrary length"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from random import choice
import string

from worktoy import maybe


def strFactory(n: int = None, *skipChars, ) -> str:
  """The strFactory function creates random strings of arbitrary length.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  n = maybe(n, 16)
  if not n:
    return ''
  if n < 0:
    msg = 'Expected non-negative integer for length of str, but received:'
    raise ValueError('%s %d!' % (msg, n))
  rawBase = string.ascii_letters + string.digits
  ignoreChars = []
  for word in skipChars:
    for char in word:
      ignoreChars.append(char)
  base = [char for char in rawBase if char not in ignoreChars]
  out = []
  while len(out) < n:
    out.append(choice(base))
  return ''.join(out)
