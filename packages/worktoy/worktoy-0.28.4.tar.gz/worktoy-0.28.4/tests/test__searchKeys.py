"""Testing the searchKeys"""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from random import randint, sample, choice, random
import string
from typing import NoReturn, Callable, Any
from unittest import TestCase

from worktoy import searchKeys, CallMeMaybe


def _someFunc() -> NoReturn:
  """Hi there, I'm a function!"""
  return None


class TestSearchKeys(TestCase):
  """Testing the searchKeys
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  @staticmethod
  def newTuple(n: int = None) -> tuple:
    """Creates single new tuple"""
    n = randint(0, 8) if n is None else n
    out = ()
    while n:
      out = (out,)
      n -= 1
    return out

  @staticmethod
  def newFloat(a: float = None, b: float = None) -> float:
    """Creates single new float"""
    if a is None:
      a, b = 0., 1.
    if b is None:
      b = 0.
    a, b = float(min([a, b])), float(max([a, b]))
    return random() * (b - a) + a

  @staticmethod
  def newInt(a: int = None, b: int = None) -> int:
    """Creates single new integer"""
    if a is None:
      a, b = 0, 255
    if b is None:
      b = 0
    a, b = min([a, b]), max([a, b])
    return randint(a, b)

  @staticmethod
  def newKey() -> str:
    """Creates a single new key"""
    base = [char for char in string.ascii_letters + string.digits]
    n = randint(4, 6)
    return ''.join(sample(base, n))

  @staticmethod
  def getKeys(n: int = None) -> list[str]:
    """Getter-function for random collection of goodKeys"""
    n = 16 if n is None else n
    out = []
    while len(out) < n:
      key = TestSearchKeys.newKey()
      if key not in out:
        out.append(key)
    return out

  @staticmethod
  def getType(**kwargs) -> (Callable, type) | list[(Callable, type)]:
    """Returns a random type"""
    full = kwargs.get('full', False)
    which = kwargs.get('index', None)
    types = [
      (str, TestSearchKeys.newKey),
      (int, TestSearchKeys.newInt),
      (float, TestSearchKeys.newFloat),
      (tuple, TestSearchKeys.newTuple),
    ]
    if full:
      return types
    if which is not None:
      if isinstance(which, int):
        return types[which % len(types)]
    return choice(types)

  @staticmethod
  def getRandomValues(n: int = None) -> tuple[list[type], list[Any]]:
    """Getter-function for random values for use with dictionaries"""
    n = 16 if n is None else n
    types = []
    values = []
    while len(types) + len(values) < 2 * n:
      t, f = TestSearchKeys.getType()
      types.append(t)
      values.append(f())
    return (types, values)

  def setUp(self) -> NoReturn:
    """Setting up the tests"""
    n = 16
    self.goodKeys = self.getKeys(n)
    self.badKeys = self.getKeys(n)
    self.types, self.values = TestSearchKeys.getRandomValues(n)
    self.typeDicts = {}
    self.valueDicts = {}
    for (key, (type_, val)) in zip(self.goodKeys,
                                   zip(self.types, self.values)):
      self.typeDicts |= {key: type_}
      self.valueDicts |= {key: val}
    self.defVal = {
      tuple: self.newTuple(3),
      int  : 69420,
      float: .1337,
      str  : 'lol',
    }

  def testCallMeMaybe(self) -> NoReturn:
    """Testing if searchKeys can handle searching for callables"""
    testKwarg = {'here': _someFunc, 'lol': 77777, 'blabla': 777777777}
    res = searchKeys('here', 'there') @ CallMeMaybe >> testKwarg
    self.assertEqual(res, _someFunc)

  def testSimpleKeys(self) -> NoReturn:
    """Testing good keys. The simplest case"""
    allKeys = self.goodKeys + self.badKeys
    allKeys = [*allKeys, *[key.lower() for key in allKeys]]
    for key in allKeys:
      if key in self.goodKeys:
        trueVal = self.valueDicts.get(key, None)
        if trueVal is not None:
          searchVal = searchKeys(key) >> self.valueDicts
          self.assertEqual(trueVal, searchVal, )
      if key in self.badKeys:
        defSearch = searchKeys(key) >> (self.valueDicts, 'lol')
        self.assertEqual(defSearch, 'lol')

  def testTypeKeys(self) -> NoReturn:
    """Testing good keys, but bad types"""
    intVal = searchKeys(*self.goodKeys) @ int >> self.valueDicts
    self.assertIsInstance(intVal, int)
    tupleVal = searchKeys(*self.goodKeys) @ tuple >> self.valueDicts
    self.assertIsInstance(tupleVal, tuple)
    floatVal = searchKeys(*self.goodKeys) @ float >> self.valueDicts
    self.assertIsInstance(floatVal, float)
    strVal = searchKeys(*self.goodKeys) @ str >> self.valueDicts
    self.assertIsInstance(strVal, str)

  def testSingleTypeMultiKey(self) -> NoReturn:
    """Testing good keys, but bad combinations of types"""
    for k1 in self.goodKeys:
      for k2 in [key for key in self.goodKeys if key != k1]:
        for (type_, defVal) in self.defVal.items():
          t1, t2 = [self.typeDicts.get(k, None) for k in [k1, k2]]
          typeVal = searchKeys(k1, k2) @ type_ >> (self.valueDicts, defVal)
          v1, v2 = [searchKeys(k) >> self.valueDicts for k in [k1, k2]]
          if t1 is type_:
            self.assertEqual(typeVal, v1)
          elif t2 is type_:
            self.assertEqual(typeVal, v2)
          else:
            self.assertEqual(typeVal, defVal)

  def testMultiTypeMultiKey(self) -> NoReturn:
    """Testing multiple keys and multiple types"""
    for k1 in self.goodKeys:
      keyType1 = self.typeDicts.get(k1, None)
      keyVal1 = self.valueDicts.get(k1, None)
      self.assertIsNotNone(keyType1)
      self.assertIsNotNone(keyVal1)
      for k2 in self.goodKeys:
        keyType2 = self.typeDicts.get(k2, None)
        keyVal2 = self.valueDicts.get(k2, None)
        self.assertIsNotNone(keyType2)
        self.assertIsNotNone(keyVal2)
        for (t1, dV1) in self.defVal.items():
          for (t2, dV2) in self.defVal.items():
            val = searchKeys(k1, k2) @ (t1, t2) >> (self.valueDicts, dV1)
            if keyType1 in (t1, t2):
              self.assertEqual(keyVal1, val)
            elif keyType2 in (t1, t2):
              self.assertEqual(keyVal2, val)
            else:
              self.assertEqual(val, dV1)
