"""The stringList function provides an easier way to write lists of
strings. Instead of wrapping each item in ticks, write on long string with
consistent separators, and stringList will convert it to a list of
strings.
Instead of: numbers = ['one', 'two', 'three', 'four']
Use stringList: numbers = stringList('one, two, three, four')"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from worktoy import searchKeys, maybeTypes, maybe
from worktoy.mockdata import strFactory


def stringList(*args, **kwargs) -> list[str]:
  """The stringList function provides an easier way to write lists of
  strings. Instead of wrapping each item in ticks, write on long string with
  consistent separators, and stringList will convert it to a list of
  strings.
  Instead of: numbers = ['one', 'two', 'three', 'four']
  Use stringList: numbers = stringList('one, two, three, four')
  Please note that all white space around each separator will be removed.
  Meaning that ', ' and ',' will produce the same outcome when used as
  separators on the same text.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  strArgs = maybeTypes(str, *args, padLen=3, padChar=None)
  sourceKwarg = searchKeys('source', 'src', 'txt') @ str >> kwargs
  separatorKwarg = searchKeys('separator', 'splitHere') @ str >> kwargs
  ignoreKwarg = searchKeys('ignoreChar', 'ignore') @ str >> kwargs
  sourceArg, separatorArg, ignoreArg = strArgs
  sourceDefault, separatorDefault, ignoreDefault = None, ', ', '@'
  source = maybe(sourceKwarg, sourceArg, sourceDefault)
  separator = maybe(separatorKwarg, separatorArg, separatorDefault, )
  # separator = separator.replace(' ', '')
  ignore = maybe(ignoreKwarg, ignoreArg, ignoreDefault)
  if source is None:
    msg = 'stringList received no string!'
    raise ValueError(msg)
  # if ignore == 'LOL':
  #   print(ignore)
  ignoreSeparator = '%s%s' % (ignore, separator)
  tempIgnore = '___%s___' % (strFactory(16))
  source = source.replace(ignoreSeparator, tempIgnore)
  # preSpace = ' %s' % separator
  # postSpace = '%s ' % separator
  # while preSpace in source:
  #   source = source.replace(preSpace, separator)
  # while postSpace in source:
  #   source = source.replace(postSpace, separator)
  out = source.split(separator)
  return [word.replace(tempIgnore, separator) for word in out]
