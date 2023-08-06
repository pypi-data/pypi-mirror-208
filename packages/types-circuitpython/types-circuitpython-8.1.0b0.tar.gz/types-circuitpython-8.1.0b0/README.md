# types-circuitpython

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-circuitpython?style=flat-square)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/types-circuitpython?style=flat-square)

Type Support (typings) for [CircuitPython](https://github.com/adafruit/circuitpython) built-in binding packages.

Coding with `adafruit-circuitpython-typing`:

![adafruit-circuitpython-typing](https://raw.githubusercontent.com/hardfury-labs/types-circuitpython/master/screen-records/adafruit-circuitpython-typing.gif)

Coding with `types-circuitpython`:

![types-circuitpython](https://raw.githubusercontent.com/hardfury-labs/types-circuitpython/master/screen-records/types-circuitpython.gif)

## Long term support versions

Following [CircuitPython release versions](https://github.com/adafruit/circuitpython/releases)

[Pypi versions](https://pypi.org/project/types-circuitpython/#history)

- 8.x
  - 8.1.x
    - 8.1.0b0 ()
    - 8.1.0a2 (Corresponds 8.1.0-alpha.2 of CircuitPython's version)
  - 8.0.x
    - 8.0.3
    - 8.0.2
    - 8.0.0
    - 8.0.0rc2 (Corresponds 8.0.0-rc.2 of CircuitPython's version)
    - 8.0.0rc1 (Corresponds 8.0.0-rc.1 of CircuitPython's version)
    - 8.0.0rc0 (Corresponds 8.0.0-rc.0 of CircuitPython's version)
    - 8.0.0b6 (Corresponds 8.0.0-beta.6 of CircuitPython's version)
    - 8.0.0b5 (Corresponds 8.0.0-beta.5 of CircuitPython's version)
    - 8.0.0b4 (Corresponds 8.0.0-beta.4 of CircuitPython's version)
    - 8.0.0b3 (Corresponds 8.0.0-beta.3 of CircuitPython's version)
    - 8.0.0b2 (Corresponds 8.0.0-beta.2 of CircuitPython's version)
    - 8.0.0b1 (Corresponds 8.0.0-beta.1 of CircuitPython's version)
    - 8.0.0b0 (Corresponds 8.0.0-beta.0 of CircuitPython's version)
    - 8.0.0a1 (Corresponds 8.0.0-alpha.1 of CircuitPython's version)
    - 8.0.0a0 (Corresponds 8.0.0-alpha.0 of CircuitPython's version)
- 7.x
  - 7.3.3
  - 7.3.2
  - 7.3.1
  - 7.3.0

## Usage

```bash
$ pip install types-circuitpython==7.3.3
# or
$ pip install types-circuitpython==8.0.0b0
```

## Development

## Initialization

```bash
$ virtualenv .venv
$ . ./.venv/bin/activate
$ pip install -r requirements.txt
$ python setup.py develop
# or
$ pip install -e .
```

## Generate bindings

```bash
$ make generate version=<CIRCUITPYTHON VERSION>
```

## Code styles

```bash
$ make format
$ make lint
```
