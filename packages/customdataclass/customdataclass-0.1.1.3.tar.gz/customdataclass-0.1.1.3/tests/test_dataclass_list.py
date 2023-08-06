import unittest

from src.customdataclass import Dataclass


class SampleClass(Dataclass):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class ListClass(Dataclass):
    """Test class."""

    int_list: list[int]
    float_list: list[float]
    str_list: list[str]
    bool_list: list[bool]


class TestSampleClass(unittest.TestCase):
    def _createSampleClass(self, val: int = 0):
        return SampleClass(
            int_var=int(val),
            float_var=float(val),
            str_var=str(val),
            bool_var=(val % 2 == 0),
        )

    def testCreation(self):
        class_list = []
        for i in range(100):
            n = self._createSampleClass(i)
            self.assertNotIn(n, class_list)
            class_list.append(n)

    def testEquality(self):
        for i in range(100):
            s1 = self._createSampleClass(i)
            s2 = self._createSampleClass(i)
            self.assertEqual(s1, s2)

    def testInequality(self):
        s1 = self._createSampleClass(1)
        s2 = self._createSampleClass(2)
        self.assertNotEqual(s1, s2)


class TestListClass(unittest.TestCase):
    def _createListClass(self, val: int = 0):
        return ListClass(
            int_list=[val for _ in range(10)],
            float_list=[float(val) for _ in range(10)],
            str_list=[str(val) for _ in range(10)],
            bool_list=[(val % 2 == 0) for _ in range(10)],
        )

    def testCreation(self):
        class_list = []
        for i in range(100):
            n = self._createListClass(i)
            self.assertNotIn(n, class_list)
            class_list.append(n)

    def testEquality(self):
        class_list = []
        for i in range(100):
            n = self._createListClass(i)
            self.assertNotIn(n, class_list)
            class_list.append(n)

        for i in range(100):
            s = self._createListClass(i)
            self.assertEqual(s, class_list[i])
            self.assertIn(s, class_list)

        for i in range(100):
            self.assertIn(class_list[i], class_list)
