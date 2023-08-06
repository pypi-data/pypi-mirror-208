import unittest
from typing import Any

from src.customdataclass import Dataclass


class SampleClass(Dataclass):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class DifferentSampleClass(Dataclass):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class TestSampleClass(unittest.TestCase):
    def _createSampleClass(self):
        return SampleClass(int_var=1, float_var=1.0, str_var="1", bool_var=True)

    def testCreation(self):
        s = self._createSampleClass()
        self.assertEqual(s.int_var, 1)
        self.assertEqual(s.float_var, 1.0)
        self.assertEqual(s.str_var, "1")
        self.assertEqual(s.bool_var, True)

        self.assertIsInstance(s.int_var, int)
        self.assertIsInstance(s.float_var, float)
        self.assertIsInstance(s.str_var, str)
        self.assertIsInstance(s.bool_var, bool)

    def testEquality(self):
        s1 = self._createSampleClass()
        s2 = self._createSampleClass()
        self.assertEqual(s1, s2)

    def testInequality(self):
        s1 = SampleClass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        s2 = SampleClass(int_var=2, float_var=1.0, str_var="1", bool_var=True)
        self.assertNotEqual(s1, s2)

    def testHash(self):
        s1 = self._createSampleClass()
        s2 = self._createSampleClass()
        self.assertEqual(hash(s1), hash(s2))

    def testRepr(self):
        s = self._createSampleClass()
        s_repr = 'SampleClass(int_var=1, float_var=1.0, str_var="1", bool_var=True)'
        self.assertEqual(repr(s), s_repr)
        self.assertEqual(str(s), s_repr)

    def testIn(self):
        s = self._createSampleClass()
        self.assertTrue("int_var" in s)
        self.assertTrue("float_var" in s)
        self.assertTrue("str_var" in s)
        self.assertTrue("bool_var" in s)
        self.assertTrue("other_var" not in s)

    def testIter(self):
        s = self._createSampleClass()
        self.assertEqual(
            list(s),
            [("int_var", 1), ("float_var", 1.0), ("str_var", "1"), ("bool_var", True)],
        )

    def testMissingParameters(self):
        with self.assertRaises(AttributeError):
            SampleClass(int_var=1, float_var=1.0, str_var="1")

    def testExtraParameters(self):
        with self.assertRaises(AttributeError):
            SampleClass(
                int_var=1, float_var=1.0, str_var="1", bool_var=True, other_var=1
            )

    def testFreeze(self):
        s = self._createSampleClass()
        with self.assertRaises(AttributeError):
            s.int_var = 2

    def testAttributes(self):
        attributes = {
            "int_var": 1,
            "float_var": 1.0,
            "str_var": "1",
            "bool_var": True,
        }

        s = SampleClass(**attributes)
        self.assertEqual(s.attributes, list(attributes.keys()))

    def testSerializeDeserialize(self):
        s1 = self._createSampleClass()
        s2 = SampleClass.from_dict(s1.to_dict)
        self.assertEqual(s1, s2)

        s3 = SampleClass.from_json(s1.to_json)
        self.assertEqual(s1, s3)

        s4 = SampleClass.from_json(s1.to_json_pretty)
        self.assertEqual(s1, s4)

        s5 = SampleClass.from_toml(s1.to_toml)
        self.assertEqual(s1, s5)

        s6 = SampleClass.from_yaml(s1.to_yaml)
        self.assertEqual(s1, s6)

    def testDifferentClassesEquality(self):
        s1 = self._createSampleClass()
        s2 = DifferentSampleClass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        self.assertNotEqual(s1, s2)


class EmptyClass(Dataclass):
    pass


class TestEmptyClass(unittest.TestCase):
    def testCreation(self):
        s = EmptyClass()
        self.assertEqual(s.attributes, [])

    def testRepresentation(self):
        s = EmptyClass()
        self.assertEqual(repr(s), "EmptyClass()")


class AnyClass(Dataclass):
    """Test class."""

    any_var: Any


class TestAnyClass(unittest.TestCase):
    def testCreation(self):
        s = AnyClass(any_var=1)
        self.assertEqual(s.any_var, 1)

    def testEquality(self):
        s1 = AnyClass(any_var=1)
        s2 = AnyClass(any_var=1)
        self.assertEqual(s1, s2)

    def testRepresentation(self):
        s = AnyClass(any_var=1)
        self.assertEqual(repr(s), "AnyClass(any_var=1)")
