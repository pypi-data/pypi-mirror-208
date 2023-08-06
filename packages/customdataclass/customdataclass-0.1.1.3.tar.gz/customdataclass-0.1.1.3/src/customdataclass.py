"""This module contains a custom dataclass object.

It does work kinda good.
"""

from __future__ import annotations

from typing import Any

import json
import yaml
import toml


class Dataclass:
    """Custom dataclass.

    The real reason is that I didn't really like the way dataclasses work,
    and I wanted to have a better control over the attributes.

    Instead of using the decorator, the a Dataclass must be initialized
    by inheriting from it and specifying the attributes in the class definition.

    This simplifies the code, allowing a better control over the attributes
    and the methods.

    Check the examples folder for more information.

    Initialization parameters:
        enforce_types (bool, optional): If True, the types of the attributes \
            are enforced. Defaults to True.
        frozen (bool, optional): If True, attributes cannot be changed after \
            initialization. Defaults to True
        partial (bool, optional): If True, parameters can be missing in the \
            initialization. Defaults to False.
    """

    _frozen: bool = False
    _frozen_after_init: bool = True
    _enforce_types: bool = True
    _partial = False
    _deserialized: bool = False
    _serializer: __module__ = None

    def __init__(self, **kwargs) -> Dataclass:
        """Create a new Dataclass.

        Raises:
            AttributeError: an invalid attribute is passed
            AttributeError: an attribute is missing in kwargs.
            TypeError: a value is not of the correct type.
        """
        if not kwargs:
            return

        # unfreeze the class for the initialisation
        self._frozen = False

        # check if all the attributes are valid
        self._checkAttributesValid(kwargs)

        if not self._partial:
            # fix the default values
            self._fixDefaultValues(kwargs)
            # check if all the attributes are present
            self._checkAttributesPresent(kwargs)

        # fix the types
        self._fixMissingTypes()

        for k, v in self.__class_attributes__.items():
            # skip the loop if partial is True and the attribute is not present
            if self._enforce_types and not (self._partial and k not in kwargs):
                # serialized format don't support tuple and set (they convert \
                # both to list), so we need to convert them back IMPLICITLY
                if self._checkDeserializedIterator(kwargs[k], v):
                    if self._deserialized:
                        # convert to tuple or set
                        kwargs[k] = v(kwargs[k])

                # serialised format don't support classes (they convert them to \
                # dict), so we need to convert them back IMPLICITLY
                if self._checkDeserializedClass(kwargs[k], v):
                    # convert to class
                    if self._deserialized:
                        # convert to class
                        kwargs[k] = v.from_dict(kwargs[k])

                # check that the type is correct
                if not self._checkTypeCorrect(kwargs[k], v):
                    raise TypeError(f"{k} should be {v}, not {type(kwargs[k])}")

            setattr(self, k, kwargs.get(k, None))

        # freeze the class
        self._frozen = self._frozen_after_init
        # unset the deserialized flag
        self._deserialized = False

    def freeze(
        self,
    ) -> None:
        """Freeze the class.

        After this, attributes cannot be changed.
        The action cannot be undone.
        """
        self._frozen = True

    def _checkAttributesValid(self, kwargs: dict) -> bool:
        """Check if all the attributes are valid (as specified in the class \
            definition).

        Args:
            kwargs (dict): kwargs to check

        Returns:
            bool: True if all the attributes are valid, False otherwise.
        """
        for k in kwargs.keys():
            if k not in self.__class_attributes__.keys():
                raise AttributeError(f"{k} is not a valid attribute")

        return True

    def _fixDefaultValues(self, kwargs: dict) -> None:
        """Fix the default values.

        Args:
            kwargs (dict): kwargs to check
        """
        for k in self.__class_attributes__:
            if k not in kwargs:
                kwargs[k] = self.__getattribute__(k)

    def _checkAttributesPresent(self, kwargs: dict) -> bool:
        """Check if all the attributes are present (as specified in the class \
            definition).

        Args:
            kwargs (dict): kwargs to check

        Returns:
            bool: True if all the attributes are present, False otherwise.
        """
        for k in self.__class_attributes__.keys():
            if k not in kwargs:
                raise AttributeError(f"Missing {k} in kwargs")

        return True

    def _fixMissingTypes(self) -> None:
        """Fix the missing types."""
        for k, v in self.__class_attributes__.items():
            if v is None:
                # no type has been specified
                self.__class__.__annotations__[k] = Any

    def _checkTypeCorrect(self, value: Any, valid_type: type) -> bool:
        """Check if the type of the value is correct.

        Args:
            value (Any): value to check
            valid_type (type): type of the value

        Returns:
            bool: True if the type is correct, False otherwise.
        """
        if valid_type in (Any, None):
            return True

        try:
            valid = isinstance(value, valid_type)
        except TypeError:
            valid = all(issubclass(v.__class__, valid_type.__args__[0]) for v in value)
        except Exception:
            valid = False

        return valid

    def _checkDeserializedIterator(self, value: list[Any], valid_type: type) -> bool:
        """Check if the value is a valid iterator.

        Args:
            value (list[Any]): value to check
            valid_type (type): type of the value

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        if not isinstance(value, list):
            return False

        return valid_type in (set, tuple)

    def _checkDeserializedClass(self, value: dict, valid_type: type) -> bool:
        """Check if the value is a valid class.

        Args:
            value (dict): value to check
            valid_type (type): type of the value

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        if not isinstance(value, dict):
            return False

        return issubclass(valid_type, Dataclass)

    def __init_subclass__(
        cls,
        enforce_types: bool = True,
        frozen: bool = True,
        partial: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the subclass.

        Args:
            enforce_types (bool, optional): If True, the types of the attributes \
                are enforced.
            frozen (bool, optional): If True, attributes cannot be changed after \
                initialization. Defaults to True.
            partial (bool, optional): If True, the class can be initialized with \
                missing attributes. Defaults to False.
        """
        cls._enforce_types = enforce_types
        cls._frozen_after_init = frozen
        cls._partial = partial
        super().__init_subclass__(**kwargs)

    def __setattr__(self, key: str, value):
        """Set an attribute.

        Args:
            key (str): name of the attribute
            value (any): value of the attribute

        Raises:
            AttributeError: Attribute is not valid
        """
        if key.startswith("_"):
            super().__setattr__(key, value)
            return

        if self._frozen:
            raise AttributeError(
                f"Can't set {key}. {self.__class__.__name__} is immutable."
            )

        super().__setattr__(key, value)

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns:
            str
        """
        if not self.__clean_dict__:
            return f"{self.__class__.__name__}()"

        parentheses = {
            "tuple": ("(", ")"),
            "list": ("[", "]"),
            "set": ("{", "}"),
            "dict": ("{", "}"),
        }

        s = f"{self.__class__.__name__}("

        for k, v in self.__clean_dict__.items():
            if self._partial and v is None:
                continue
            s += f"{k}="
            if isinstance(v, str):
                s += f'"{v}"'
            elif isinstance(v, (list, tuple, set, dict)):
                s += parentheses[v.__class__.__name__][0]
                if isinstance(v, dict):
                    s += ", ".join(f'"{k}": {v}' for k, v in v.items())
                else:
                    s += f"{', '.join(str(i) for i in v)}"

                s += parentheses[v.__class__.__name__][1]
            else:
                s += str(v)

            s += ", "

        s = s[:-2] + ")"
        return s

    def __str__(self) -> str:
        """Return a string representation of the object.

        Returns:
            str
        """
        return self.__repr__()

    def __eq__(self, other) -> bool:
        """Compare two objects.

        Args:
            other (any): object to compare

        Returns:
            bool
        """
        if not isinstance(other, self.__class__):
            return False

        for k in self.__class_attributes__:
            if getattr(self, k) != getattr(other, k):
                return False

        return True

    def __hash__(self) -> int:
        """Return the hash of the object.

        Returns:
            int
        """
        ordered = sorted(self.__clean_dict__.items())
        return hash(tuple(ordered))

    def __contains__(self, item) -> bool:
        """Check if the object contains an item.

        This is used to check if an attribute exists via the \
        built-in `in` operator.

        Args:
            item (any): item to check

        Returns:
            bool
        """
        return item in self.__clean_dict__.keys()

    def __iter__(self):
        """Return an iterator for the object.

        Returns:
            iterator
        """
        return iter(self.__clean_dict__.items())

    @property
    def __class_attributes__(self) -> dict[str, type]:
        """Return all the attributes of the class and their type.

        Returns:
            dict
        """
        return {
            k: v if isinstance(v, type) else None
            for k, v in self.__class__.__annotations__.items()
            if not k.startswith("_")
        }

    @property
    def __clean_dict__(self) -> dict:
        """Return a dictionary with all the attributes of the object, \
            except for the ones starting with an underscore (private).

        Returns:
            dict
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def _importDecorator(f, *_, **__) -> None:
        """Import the correct serializer for the function.

        The serializer will be put in the `_serializer` attribute of the object.
        It's mandatory to have all the functions decorated with this decorator \
        to contain the name of the serializer in their name.

        Unittest will require all the serializers to be installed.

        Args:
            f (function): function to decorate

        Raises:
            ImportError: Could not import the correct serializer
        """
        libs = {
            "json": json,  # could be ujson but json is in the stdlib
            "yaml": yaml,  # not in the stdlib
            "toml": toml,  # not in the stdlib
        }
        serializer = None

        for k, v in libs.items():
            if k in f.__name__:
                serializer = v
                break

        if serializer is None:
            raise NotImplementedError(f"Serializer for {f.__name__} not implemented.")

        def wrapper(self: Dataclass, *args, **kwargs):
            self._serializer = serializer
            return f(self, *args, **kwargs)

        return wrapper

    @property
    def to_dict(self) -> dict:
        """Return a dictionary with all the attributes of the object.

        Returns:
            dict
        """

        def iterable_type(var: any) -> type:
            if isinstance(var, (list, tuple, set)):
                return var.__class__

            return None

        d = {}

        for k, v in self.__clean_dict__.items():
            if t := iterable_type(v):
                # handle recursive lists
                d[k] = t(i.to_dict if isinstance(i, Dataclass) else i for i in v)
            elif isinstance(v, Dataclass):
                # handle recursive dataclasses
                d[k] = v.to_dict
            else:
                # simple types
                d[k] = v

        return d

    @property
    def frozen(self) -> bool:
        """Return the frozen status of the object."""
        return self._frozen

    @property
    @_importDecorator
    def to_json(self) -> str:
        """
        Return a json representation of the object. \
        Attributes are recursively converted to json.

        Returns:
            str
        """
        dict_data = self.to_dict

        # all the sets and tuples are converted to lists
        # because json doesn't support them
        for k, v in dict_data.items():
            if isinstance(v, (set, tuple)):
                dict_data[k] = list(v)

        return self._serializer.dumps(dict_data)

    @property
    def to_json_pretty(self) -> str:
        """Return a pretty json representation of the object.

        Returns:
            str
        """
        return self._serializer.dumps(self._serializer.loads(self.to_json), indent=4)

    @property
    @_importDecorator
    def to_toml(self) -> str:
        """Return a toml representation of the object.

        Returns:
            str
        """
        return self._serializer.dumps(self.to_dict)

    @property
    @_importDecorator
    def to_yaml(self) -> str:
        """Return a yaml representation of the object.

        Returns:
            str
        """
        return self._serializer.dump(self.to_dict)

    @property
    def attributes(self) -> list:
        """Return a list of all the attributes of the class.

        Returns:
            list
        """
        return list(self.__class_attributes__.keys())

    @classmethod
    @_importDecorator
    def from_json(cls, json_string: str):
        """Create an object from a json string.

        Args:
            json_string (str): json string

        Returns:
            object
        """
        cls._deserialized = True
        return cls(**cls._serializer.loads(json_string))

    @classmethod
    @_importDecorator
    def from_toml(cls, toml_string: str):
        """Create an object from a toml string.

        Args:
            toml_string (str): toml string

        Returns:
            object
        """
        cls._deserialized = True
        return cls(**cls._serializer.loads(toml_string))

    @classmethod
    @_importDecorator
    def from_yaml(cls, yaml_string: str):
        """Create an object from a yaml string.

        Args:
            yaml_string (str): yaml string

        Returns:
            object
        """
        cls._deserialized = True
        return cls(
            **cls._serializer.load(yaml_string, Loader=cls._serializer.FullLoader)
        )

    @classmethod
    def from_dict(cls, d: dict):
        """Create an object from a dictionary.

        Args:
            d (dict): dictionary

        Returns:
            object
        """
        cls._deserialized = True
        return cls(**d)
