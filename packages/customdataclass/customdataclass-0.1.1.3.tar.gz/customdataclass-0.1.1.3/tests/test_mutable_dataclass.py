import unittest

from src.customdataclass import Dataclass


class MutableDataclass(Dataclass, frozen=False):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class TestNotFrozenClass(unittest.TestCase):
    def _createDataclass(self) -> tuple[MutableDataclass, MutableDataclass]:
        s1 = MutableDataclass(int_var=1, float_var=1.0, str_var="1", bool_var=True)
        s2 = MutableDataclass(int_var=2, float_var=2.0, str_var="2", bool_var=False)

        return s1, s2

    def testCreation(self):
        s, _ = self._createDataclass()
        self.assertEqual(s.int_var, 1)
        self.assertEqual(s.float_var, 1.0)
        self.assertEqual(s.str_var, "1")
        self.assertEqual(s.bool_var, True)

        self.assertIsInstance(s.int_var, int)
        self.assertIsInstance(s.float_var, float)
        self.assertIsInstance(s.str_var, str)
        self.assertIsInstance(s.bool_var, bool)

        self.assertFalse(s.frozen)

    def testEquality(self):
        s1, _ = self._createDataclass()
        s2, _ = self._createDataclass()
        self.assertEqual(s1, s2)

    def testMutation(self):
        s1, s2 = self._createDataclass()
        s1.int_var = 2
        s1.float_var = 2.0
        s1.str_var = "2"
        s1.bool_var = False

        self.assertEqual(s1.int_var, 2)
        self.assertEqual(s1.float_var, 2.0)
        self.assertEqual(s1.str_var, "2")
        self.assertEqual(s1.bool_var, False)

        self.assertEqual(s1, s2)

    def testFreeze(self):
        s, _ = self._createDataclass()
        s.freeze()
        self.assertTrue(s.frozen)
        with self.assertRaises(AttributeError):
            s.int_var = 2
