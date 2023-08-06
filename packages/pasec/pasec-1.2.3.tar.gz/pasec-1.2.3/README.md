# Pasec

[![PyPI version](https://badge.fury.io/py/pasec.svg)](https://badge.fury.io/py/pasec)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your_username/pasec/blob/main/LICENSE)

Pasec is a Python module that generates secure passwords from a given passphrase. It ensures that the generated password is always the same for a given passphrase.It will generate the strong password from weak passphrase which is easy to remember.

## This is python adaptation of [pasec.ssuroj.com.np](https://pasec.ssuroj.com.np/)
## Installation

You can install pasec using pip:
```
pip install pasec
```

## Usage

Here's an example of how to use pasec in your Python code:

```python
from pasec import generate

# Set the passphrase and options
passphrase = "secret"

# Generate the password
password = generate.password(passphrase)
print(password)
```
Output will be:
```
F&huA8Owq-7!:6c_T3U3
```
note that it will give you 20 letter password and includes  Capital Letter, Small Letters, Number and Special Symbols to specify what we need we can use options shown below
## Options
We can also give the length of password it like this:
```python
generate.password(passphrase, 16) 
```
And also can spefity wether to include Capital Letters, Small Letters, Number and Special Symbols

To do so we need 4 digit number like this 1111 where first number is for Capital Letter Second for Small Letters Third for Number and foruth Special Symbols where 1 states include and 0  states don't include

lets see example:
```python
generate.password(passphrase, 16, '0010')
```
this will only generate number as we can see only third is 1 and third means number


Output will be :
```
8208036993008678
```

another example:
```python
generate.password(passphrase, 16, '0110')
```
this will only generate small letter and number as we can see only second and  third is 1 so Output will be :
```
ff4n243256a6gtud
```
Note that

- Frist = ` Capital letters`
- Second =  `Small Letters`
- Third =  `Number`
- Fourth = `Special Symbols`


## Liscense
PaSec is licensed under the [MIT liscense](https://mit-license.org/). Feel free to use, modify, and distribute our code for any purpose.
