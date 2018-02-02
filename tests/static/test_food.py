import unittest
import requests

from utils import TEST_INSTANCE, TestGameData


class TestFoodLogic(unittest.TestCase):
    def test_food_close_hungry(self):
        data = TestGameData()
        data.set_self([(5,5),(5,6),(5,7)], health=10)
        data.set_food([(5,3)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

    def test_food_far_hungry(self):
        data = TestGameData()
        data.set_self([(5,5),(5,6),(5,7)], health=10)
        data.set_food([(0,0)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

        data = TestGameData()
        data.set_self([(5,5),(5,6),(5,7)], health=10)
        data.set_food([(0,10)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')
