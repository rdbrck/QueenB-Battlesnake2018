# flake8: noqa
from test_food import *
from test_avoidance import *
from test_attacking import *

import unittest
import requests
import sys


try:
    response = requests.post("http://0.0.0.0:8080/start", {})
except:
    print("Instance not available at http://0.0.0.0:8080/start, closing tests.")
    sys.exit(0)

if response.status_code != 200:
    print("Instance not available at http://0.0.0.0:8080/start, closing tests.")
    sys.exit(0)

if __name__ == "__main__":
    unittest.main()
