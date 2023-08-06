import unittest

from src.customdataclass import Dataclass


class IncompleteDataclass(Dataclass):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: False


class MutableIncompleteDataclass(Dataclass, frozen=False):
    """Test class."""

    int_var: False


class TestIncompleteDataclass(unittest.TestCase):
    def testCreation(self):
        i = IncompleteDataclass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        self.assertEqual(i.int_var, 1)
        self.assertEqual(i.float_var, 1.0)
        self.assertEqual(i.str_var, "1")
        self.assertEqual(i.bool_var, True)

        self.assertIsInstance(i.int_var, int)
        self.assertIsInstance(i.float_var, float)
        self.assertIsInstance(i.str_var, str)
        self.assertIsInstance(i.bool_var, bool)

    def testTypeChange(self):
        i = MutableIncompleteDataclass()
        i.int_var = 1
        self.assertEqual(i.int_var, 1)

    def testEquality(self):
        i1 = IncompleteDataclass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        i2 = IncompleteDataclass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        self.assertEqual(i1, i2)

    def testRepresentation(self):
        i = IncompleteDataclass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        self.assertEqual(
            repr(i),
            'IncompleteDataclass(int_var=1, float_var=1.0, str_var="1", bool_var=True)',
        )
