import unittest

from src.customdataclass import Dataclass


class ComplexDataclass(Dataclass):
    """Test class."""

    list_var: list
    tuple_var: tuple
    set_var: set
    dict_var: dict


class TestComplexDataclass(unittest.TestCase):
    def _createComplexDataclass(self):
        return ComplexDataclass(
            list_var=[1, 2, 3],
            tuple_var=(1, 2, 3),
            set_var={1, 2, 3},
            dict_var={"a": 1, "b": 2, "c": 3},
        )

    def _reprComplexDataclass(self):
        return (
            "ComplexDataclass(list_var=[1, 2, 3], tuple_var=(1, 2, 3), "
            'set_var={1, 2, 3}, dict_var={"a": 1, "b": 2, "c": 3})'
        )

    def testComplexDataclass(self):
        c = self._createComplexDataclass()
        self.assertEqual(c.list_var, [1, 2, 3])
        self.assertEqual(c.tuple_var, (1, 2, 3))
        self.assertEqual(c.set_var, {1, 2, 3})
        self.assertEqual(c.dict_var, {"a": 1, "b": 2, "c": 3})

        self.assertIsInstance(c.list_var, list)
        self.assertIsInstance(c.tuple_var, tuple)
        self.assertIsInstance(c.set_var, set)
        self.assertIsInstance(c.dict_var, dict)

    def testComplexDataclassEquality(self):
        c1 = self._createComplexDataclass()
        c2 = self._createComplexDataclass()
        self.assertEqual(c1, c2)

    def testRepr(self):
        c = self._createComplexDataclass()
        self.assertEqual(repr(c), self._reprComplexDataclass())
        self.assertEqual(str(c), self._reprComplexDataclass())

    def testSerializeDeserialize(self):
        c1 = self._createComplexDataclass()
        c2 = ComplexDataclass.from_dict(c1.to_dict)
        self.assertEqual(c1, c2)

        c3 = ComplexDataclass.from_json(c1.to_json)
        self.assertEqual(c1, c3)

        c4 = ComplexDataclass.from_toml(c1.to_toml)
        self.assertEqual(c1, c4)

        c5 = ComplexDataclass.from_yaml(c1.to_yaml)
        self.assertEqual(c1, c5)

    def testIterableType(self):
        with self.assertRaises(TypeError):
            ComplexDataclass(
                list_var=[1, 2, 3],
                tuple_var=[1, 2, 3],
                set_var=[1, 2, 3],
                dict_var={"a": 1, "b": 2, "c": 3},
            )
