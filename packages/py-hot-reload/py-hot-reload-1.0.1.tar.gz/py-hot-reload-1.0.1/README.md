# Python Hot Reload
Python Hot Reload starts the given program and reloads it whenever any file changes in the current directory or imported modules.

## Installation

You can install the Python Hot Reload from [PyPI](https://pypi.org/project/py-hot-reload/):

    python -m pip install py-hot-reload

Python Hot Reload is supported on Python 3.6 and above.

## How to use

Python Hot Reload has a command line implementation called `py-hot-reload`. To see help message, call the program with `-h, --help`:

    $ py-hot-reload -h
    Usage: python -m hot_reload [OPTIONS] PYTHON_FILE

    Options:
    -V, --version                   Show the version and exit.
    -C, --copyright                 Show the copyright and exit.
    -v, --verbose                   Verbose.
    -ep, --extra-patterns TEXT      Extra patterns
    -ip, --ignore-patterns TEXT     Ignore patterns
    -i, --interval INTEGER          Interval
    --add-current-folder-to-patterns
                                    Add current folder to patterns.
    --ignore-venv-and-python-lib    Ignore venv and python lib.
    -h, --help                      Show this message and exit.

To run ignoring certain patterns, run using `-ip, --ignore-patterns`:

    $ py-hot-reload -ip="*.txt;*/dir/*" <python-file>

To run with extra patterns, run using `-ep, --extra-patterns`:

    $ py-hot-reload -ep="*.txt;*/dir/*" <python-file>


You can also call the Python Hot Reload in your own Python code, by importing from the `py_hot_reload` package:
```Python
import py_hot_reload

def main():
    print(1)

py_hot_reload.run_with_reloader(main)
```