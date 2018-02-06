# flake8: noqa
from test_food import *
from test_avoidance import *
from test_attacking import *
from utils import TEST_INSTANCE

import unittest
import requests
import sys


url = TEST_INSTANCE.replace('move', 'start')

try:
    response = requests.post(url, {})
except:
    print("Instance not available at %s, closing tests." % url)
    sys.exit(0)

if response.status_code != 200:
    print("Instance not available at %s, closing tests." % url)
    sys.exit(0)

if __name__ == "__main__":
    unittest.main()
