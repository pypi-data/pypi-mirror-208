# checkify

checkify is a Python package that utilizes the GPT API to check for errors in code and explain the code.

## Installation

You can install checkify using pip:

pip install checkify


## Usage

To use checkify, import the `check_code` function from the `code_checker` module:

```python
from checkify.code_checker import check_code

code = """
def greet(name):
    print("Hello, " + name)

greet("John")
"""

explanation = check_code(code)
print(explanation)
