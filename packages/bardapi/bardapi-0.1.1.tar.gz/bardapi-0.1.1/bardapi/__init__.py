import os
from bardapi.core import Bard

api_key = os.environ.get("_BARD_API_KEY")

__all__=['Bard', 'api_key']
__version__ = "0.1.1"
__author__ = "daniel park <parkminwoo1991@gmail.com>"