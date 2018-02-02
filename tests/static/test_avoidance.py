import unittest
import requests

from utils import TEST_INSTANCE, TestGameData


class TestAvoidanceLogic(unittest.TestCase):
    def test_avoid_corner(self):
        data = TestGameData()
        data.set_self([(0, 0), (0, 1), (0, 2)], health=10)

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_head_to_head_smaller(self):
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)])
        data.add_enemy([(5, 4), (5, 3), (5, 2), (5, 1)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] in ['right', 'left'])

    def test_avoid_tunnel(self):
        data = TestGameData()
        data.set_self([(0, 4), (0, 5), (0, 6)])
        data.add_enemy([(1, 0), (1, 1), (1, 2), (1, 3)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_avoid_tail_growth(self):
        data = TestGameData()
        data.set_self([(5, 6), (5, 7), (5, 8)], health=10)
        data.add_enemy([(7, 5), (6, 5), (5, 5)])
        data.set_food([(5, 4), (8, 5)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertNotEqual(response.json()['move'], 'up')
