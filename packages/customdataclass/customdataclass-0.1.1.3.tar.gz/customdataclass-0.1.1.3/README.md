# Customdataclass

<p align="center">
<img src=https://img.shields.io/github/issues-raw/lorossi/customdataclass></img>
<img src=https://img.shields.io/pypi/l/customdataclass></img>
<img src=https://img.shields.io/pypi/pyversions/customdataclass></img>
<img src=https://img.shields.io/pypi/v/customdataclass></img>
<img src=https://img.shields.io/pypi/format/customdataclass></img>
<img src=https://img.shields.io/badge/dynamic/json?color=informational&label=code%20coverage&query=totals.percent_covered_display&suffix=%25&url=https%3A%2F%2Fraw.githubusercontent.com%2Florossi%2Fcustomdataclass%2Fmain%2Fcoverage.json></img>
<img src=https://img.shields.io/github/languages/top/lorossi/customdataclass></img>
</p>

Custom implementation of the `dataclass` module from the standard Python library as a base class for other dataclasses.
The documentation is available [here](https://lorossi.github.io/customdataclass).

## Details

A while back I was working on a project *(now lost in a dusty corner of my GitHub profile)* that required me to create a lot of data structures *(variables used only to hold complex data)* and I quickly realised that using dictionaries *(or named dictionaries)* was slowly becoming messy because:

- dictionaries are mutable
- dictionary keys are strings and there's no easy way to set a default value for a key
- there's no way to ensure that a dictionary is well-formed
- complex attributes that are needed once or twice cannot be generated on the fly and must be stored in the dictionary

After a quick Google-fu session, I found out the existence of the `dataclass` decorator, swiftly provided by the `dataclasses`. This decorator allows you to create a class that is used only to hold data, and it provides a lot of useful features, such as:

- default values for attributes
- pre-determined methods *(such as `__init__`, `__repr__`, `__hash__`, etc.)*

However, it does not handle easily features like:

- complex attributes *(i.e. attributes that are dataclasses themselves)*
- nested dataclasses *(i.e. a dataclass that has another dataclass as an attribute)*
- serialization and deserialization
- hashing and equality
- type checking
- inheritance

All these were important for the project *(which once again will be finished, one day)* and so I decided to create a custom class that would handle all these features.

I chose to create a class *(and not a decorator)* because I wanted to be able to inherit from it and to be able to use it as a base class for other dataclasses, thus solving the aforementioned problems.

## Installing

The package is available on PyPI and can be installed using `pip`:

```bash
pip install -u customdataclass
```

## Examples

Examples can be found in the `examples` folder, both in a text file [Examples.md](examples/Examples.md) and in a set of Python scripts.

## Tests

Unit tests can be found in the `tests` folder.
Currently, the code coverage for unit tests is close to 100%.

### Running the tests

To run the tests, simply run the following command from the root folder of the project:

```bash
python3 -m unittest discover -v -s ./tests -p "test*.py
```

If you're using VScode, you can also use the `Run Tests` command from the `Python Test Explorer for Visual Studio Code` extension.

### Computing the coverage

To compute the coverage, simply run the following commands from the root folder of the project:

- `coverage run -m unittest discover -s ./tests -p "test*.py"`
- `coverage report -m` to see the report in the terminal
- `coverage html` to see format the report in HTML and see it in the browser

## Documentation

Documentation can be found in the `docs` folder of the repo and on this [page](https://lorossi.github.io/customdataclass).

### Building the documentation

To build the documentation, simply run the following command from the `src` folder of the project:

```bash
pdoc --html -o ../docs customdataclass.py --force
```

## Contributing

Pull requests, bug reports and feature requests are more than welcome!

Thank you for your interest in this silly little project of mine!

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
