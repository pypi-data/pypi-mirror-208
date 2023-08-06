# ADD TWO NUMBERS

This is an example project demonstrating how to publish a python module to PyPI.

## Installation

Run the following to install:
''' 
python3
pip install add_15_05_23
'''

##Usage
'''
python3
from add import add_numbers

# Generate "25"
add_numbers(15,10)
'''

# Developing add_numbers
To install add_numbers, along with tools you need to develop and run tests, run the following in your virtualenv:
'''
bash
$pip install -e .[dev]
'''