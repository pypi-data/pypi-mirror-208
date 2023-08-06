# myfuncs

This Python package, `myfuncs`, is a collection of personal utility functions created by myself. It is primarily intended for my personal use, providing easy access to frequently used functions across different projects and systems.

## Installation

You can install the package via pip:

```bash
pip install myfuncs
```


## Usage

Here's an example of how to use the functions provided by the `myfuncs` package:

```python
from myfuncs import valid_uuid, logf

# Example usage of valid_uuid
print(valid_uuid("550e8400-e29b-41d4-a716-446655440000"))  # True

# Example usage of logf
import logging

@logf(level=logging.DEBUG)
def example_function(x):
    return x * 2

print(example_function(4))  # 8
```

You can update your `README.md` file to include information about the tests as follows:

---

## Running Tests

To run the tests for the `myfuncs` package, follow these steps:

1\. Navigate to the root directory of the `myfuncs` package in your terminal.

2\. Make sure you have the necessary dependencies installed in your virtual environment.

3\. Run the tests by executing the following command:

```bash

python -m unittest tests.myfuncs_tests

```

If the tests run successfully, you should see output similar to the following:

```

..DEBUG:myfuncs.funcs:valid_uuid() | ('123e4567-e89b-12d3-a456-426614174000',) {}

DEBUG:myfuncs.funcs:valid_uuid() 0.00018s | True

DEBUG:myfuncs.funcs:valid_uuid() | ('123e4567-e89b-12d3-a456-42661417400',) {}

DEBUG:myfuncs.funcs:valid_uuid() 0.00002s | False

.

----------------------------------------------------------------------

Ran 3 tests in 0.001s

OK

```

This output indicates that all the tests have passed.

---