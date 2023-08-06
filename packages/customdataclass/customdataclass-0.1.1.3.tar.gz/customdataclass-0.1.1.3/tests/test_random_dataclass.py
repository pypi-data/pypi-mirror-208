import random
import unittest

from src.customdataclass import Dataclass


class RandomClass(Dataclass):
    """Test class."""

    int_var: int
    float_var: float
    str_var: str
    bool_var: bool


class TestRandomClass(unittest.TestCase):
    def _create_random_class(self, max_value=1000, seed=None):
        if seed is not None:
            random.seed(seed)

        return RandomClass(
            int_var=random.randint(0, max_value),
            float_var=random.random() * max_value,
            str_var=str(random.randint(0, max_value)),
            bool_var=bool(random.randint(0, 1)),
        )

    def testCreation(self):
        for _ in range(100):
            s = self._create_random_class()
            self.assertIsInstance(s.int_var, int)
            self.assertIsInstance(s.float_var, float)
            self.assertIsInstance(s.str_var, str)
            self.assertIsInstance(s.bool_var, bool)

    def testEquality(self):
        for x in range(100):
            s1 = self._create_random_class(seed=x * 1000)
            s2 = self._create_random_class(seed=x * 1000)
            self.assertEqual(s1, s2)
