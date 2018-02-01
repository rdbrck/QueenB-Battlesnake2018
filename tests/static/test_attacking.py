import unittest
import ujson


TEST_INSTANCE = 'http://0.0.0.0:8080/'


with open('./move.json') as move:
    MOVE_DEFAULT = ujson.load(move)


@unittest.skip("Skipping as snake currently doesn't attack.")
class TestAttackLogic(unittest.TestCase):
    def test_testing(self):
        pass
