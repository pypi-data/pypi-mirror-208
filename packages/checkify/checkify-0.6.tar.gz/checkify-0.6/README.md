# Checkify

[![Downloads](https://pepy.tech/badge/checkify/month)](https://pepy.tech/project/checkify)

Checkify is a Python package that utilizes the power of the GPT API to provide comprehensive code analysis and assistance. It helps you identify errors in code, explains the code logic, and offers valuable suggestions for improvement.

## Installation

To get started with Checkify, make sure you have Python installed. Then, you can install Checkify using `pip`:

```shell
pip install checkify
```

## Usage

Before using Checkify, you need to obtain an API key from OpenAI. Follow the instructions on the OpenAI website to get your API key.

Once you have your API key, you can start using Checkify in your Python code. Import the `check_code` function from the `code_checker` module:

```python
from checkify.code_checker import check_code

# Prompt the user to enter their OpenAI API key
api_key = input("Please enter your OpenAI API key: ")

# Set the API key for Checkify
check_code.set_api_key(api_key)

# Write your code to be checked
code = """
def greet(name):
    print("Hello, " + name)

greet("John")
"""

# Call the check_code function to analyze and explain the code
explanation = check_code(code)
print(explanation)
```

Make sure to replace `YOUR_API_KEY` with your actual OpenAI API key.

By using Checkify, you can improve your code quality, catch potential errors, and gain a deeper understanding of your code logic.

---

Please note that Checkify is a powerful tool, and it relies on the OpenAI GPT API for code analysis. Ensure that you have an active OpenAI subscription and sufficient API credits to use Checkify effectively. For more details on OpenAI API pricing and usage, visit the OpenAI website.

We hope you find Checkify helpful in your coding journey! Happy coding and stay creative!