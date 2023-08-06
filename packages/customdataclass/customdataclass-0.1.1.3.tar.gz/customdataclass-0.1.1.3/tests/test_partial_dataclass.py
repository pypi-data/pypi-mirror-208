import unittest

from src.customdataclass import Dataclass


class PartialDataclass(Dataclass, partial=True):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class PartialMutableDataclass(Dataclass, partial=True, frozen=False):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class TestPartialDataclass(unittest.TestCase):
    def testCreation(self):
        p = PartialDataclass(int_var=1, float_var=1.0, str_var="1")
        self.assertEqual(p.int_var, 1)
        self.assertEqual(p.float_var, 1.0)
        self.assertEqual(p.str_var, "1")

        self.assertIsInstance(p.int_var, int)
        self.assertIsInstance(p.float_var, float)
        self.assertIsInstance(p.str_var, str)

    def testMutable(self):
        p = PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1")
        self.assertEqual(p.int_var, 1)
        self.assertEqual(p.float_var, 1.0)
        self.assertEqual(p.str_var, "1")

        self.assertIsInstance(p.int_var, int)
        self.assertIsInstance(p.float_var, float)
        self.assertIsInstance(p.str_var, str)

        p.int_var = 2
        p.float_var = 2.0
        p.str_var = "2"

        self.assertEqual(p.int_var, 2)
        self.assertEqual(p.float_var, 2.0)
        self.assertEqual(p.str_var, "2")

        self.assertIsInstance(p.int_var, int)
        self.assertIsInstance(p.float_var, float)
        self.assertIsInstance(p.str_var, str)

        p.bool_var = True
        self.assertEqual(p.bool_var, True)

    def testEquality(self):
        p1 = PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1")
        p2 = PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1")

        self.assertEqual(p1, p2)

        p1.bool_var = True

        self.assertNotEqual(p1, p2)

        p2.bool_var = True

        self.assertEqual(p1, p2)

    def testEqualityMissingAttributes(self):
        p1 = PartialMutableDataclass(int_var=1)
        p2 = PartialMutableDataclass(float_var=1.0)
        self.assertNotEqual(p1, p2)
        p2.float_var = None
        p2.int_var = 1
        self.assertEqual(p1, p2)

    def testRepr(self):
        p = PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1")

        self.assertEqual(
            repr(p),
            'PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1")',
        )

        p.bool_var = True

        self.assertEqual(
            repr(p),
            'PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1", '
            "bool_var=True)",
        )

        p.bool_var = None

        self.assertEqual(
            repr(p),
            'PartialMutableDataclass(int_var=1, float_var=1.0, str_var="1")',
        )
