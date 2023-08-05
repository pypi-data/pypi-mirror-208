# Alphabetize

Alphabetize finds grouped lines of variables  within your files and orders them alphabetically. This is useful for cleaning up codebases.

The organisation priority is:

1. independent variables
2. dependent variables

The variable 'a' is ordered last as it depends on the other variables.

```
b = 10
c = 20
d = 40
a = b + c + d
```

UPPERCASE and lowercase variables are separated when ordered.

```
A = 10
B = 20
C = 30
a = 10
b = 20
c = 30
```

## Installation

    pip install alphabetize

## Usage

    alphabetize myfile.py
    alphabetize path/to/myfile.py

The provided argument can either be the relative path or absolute path to a Python file.

## Examples

### Example 1 - single use
Consider the following Python script (`unordered_code.py`)

```
import datetime
from time import time

# First Variable Block
c_variable = 60
A_variable = 10
a_variable = 40
B_variable = 20
b_variable = 50
C_variable = 30


class TestClass:
    def __init__(self):
        self.c_variable = 30
        self.a_variable = 10
        self.b_variable = 20


def test_function():
    c_variable = time()
    a_variable = 10
    b_variable = datetime
    a_list = [a_variable, b_variable, c_variable]
    bb_variable = 20
    aa_variable = 10
    cc_variable = aa_variable + bb_variable

    return a_list, cc_variable
    
```

Calling:

    alphabetize unordered_code.py

Results in the following output:

```
import datetime
from time import time

# First Variable Block
A_variable = 10
B_variable = 20
C_variable = 30
a_variable = 40
b_variable = 50
c_variable = 60


class TestClass:
    def __init__(self):
        self.a_variable = 10
        self.b_variable = 20
        self.c_variable = 30


def test_function():
    a_variable = 10
    b_variable = datetime
    c_variable = time()
    a_list = [a_variable, b_variable, c_variable]
    aa_variable = 10
    bb_variable = 20
    cc_variable = aa_variable + bb_variable

    return a_list, cc_variable
    
```

### Example 2 - multiple uses

Depending on the variable names found within grouped lines, `alphabetize` can be called multiple times to further reorder the grouped lines of variables.

This particularly comes into play when independent and dependent variables are mixed within the same grouped lines block.

Consider the following Python script (`unordered_code_multi.py`)

```
def test_function():
    c_variable = 30
    a_variable = 10
    b_variable = 20
    list = [a_variable, b_variable, c_variable]
    bb_variable = 20
    aa_variable = 10
    cc_variable = aa_variable + bb_variable

    return list, cc_variable
    
```

Calling `alphabetize unordered_code_multi.py` for the first time produces:

```
def test_function():
    a_variable = 10
    b_variable = 20
    c_variable = 30
    aa_variable = 10
    bb_variable = 20
    list = [a_variable, b_variable, c_variable]
    cc_variable = aa_variable + bb_variable

    return list, cc_variable

```

Then calling `alphabetize unordered_code_multi.py` a second time produces a further ordered file:

```
def test_function():
    a_variable = 10
    aa_variable = 10
    b_variable = 20
    bb_variable = 20
    c_variable = 30
    cc_variable = aa_variable + bb_variable
    list = [a_variable, b_variable, c_variable]

    return list, cc_variable

```

## Recommended Running

When using `alphabetize` it is recommended that you lint and format your files in the following order:

1. [flake8](https://pypi.org/project/flake8/) is a wrapper around the tools:
   1. Pyflakes 
   2. pycodestyle
   3. Ned Batchelder's McCabe script
2. [vulture](https://pypi.org/project/vulture/) finds unused code in Python programs.
3. [alphabetize](https://pypi.org/project/alphabetize/) finds and orders variables within files

It is recommended to run `alphabetize` a second time to catch any caught dependent variables. Then a further `flake8` to ensure your file is formatted and adheres to PEP8 correctly.