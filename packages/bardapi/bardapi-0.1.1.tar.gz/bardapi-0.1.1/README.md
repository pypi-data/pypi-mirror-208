# Google BARD API
> A package that returns Response of Google BARD through API

I referred to the [GitHub repository](https://github.com/acheong08/Bard) where inference process of BARD was reverse engineered. Using `__Secure-1PSID`, you can ask questions and get answers from Google BARD. This package is designed for application to the Python package [ExceptNotifier](https://github.com/dsdanielpark/ExceptNotifier).

<br>

## Install
The latest stable release (and required dependencies) can be installed from PyPI:
```
pip install bardapi
```
You may instead want to use the development version from Github:
```
pip install git+https://github.com/dsdanielpark/BARD_API.git
```

<br>

## Authentication
1. Visit https://bard.google.com/
2. F12 for console
3. Session: Application → Cookies → Copy the value of  __Secure-1PSID cookie.

<br>

## Usage
Simple Usage
```python
from bardapi import Bard

os.environ['_BARD_API_KEY']="xxxxxxxx."
Bard().get_answer("What is Google BARD????")['content']
```


Or you can use this
```python
import bardapi
import os

# set your __Secure-1PSID value to key
os.environ['_BARD_API_KEY']="xxxxxxxx."

# set your input text
input_text = "What is Google Bard???"

# Send an API request and get a response.
response = bardapi.core.Bard().get_answer(input_text)
```

## License
:star2: Just Give me and [them](https://github.com/acheong08/Bard) a star :stars:
