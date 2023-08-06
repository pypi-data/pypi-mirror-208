import unittest

from src.customdataclass import Dataclass


class DefaultValue(Dataclass):
    int_val: int = 4
    float_val: float = 4.0


class TestDefaultValueDataclass(unittest.TestCase):
    def testCreate(self):
        d = DefaultValue()
        self.assertEqual(d.int_val, 4)
        self.assertEqual(d.float_val, 4.0)

    def testCreateWithValues(self):
        d = DefaultValue(int_val=5, float_val=5.0)
        self.assertEqual(d.int_val, 5)
        self.assertEqual(d.float_val, 5.0)

    def testCreateWithWrongValues(self):
        with self.assertRaises(TypeError):
            DefaultValue(int_val="5", float_val="5.0")

    def testCreateWithMixedValues(self):
        d = DefaultValue(int_val=6)
        self.assertEqual(d.int_val, 6)
