import unittest
import requests

from utils import TEST_INSTANCE, TestGameData


@unittest.skip("Skipping as snake currently doesn't purposefully attack.")
class TestAttackLogic(unittest.TestCase):
    def test_head_to_head_bigger(self):
        data = TestGameData()
        data.set_self([(5,5),(5,6),(5,7)])
        data.add_enemy([(5,4),(5,3)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')
