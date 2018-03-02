import unittest
import requests

from utils import TEST_INSTANCE, TestGameData


class TestFoodLogic(unittest.TestCase):
    def test_food_close_hungry(self):
        """ get food if hungry """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=10)
        data.set_food([(5, 3)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

    def test_food_far_hungry(self):
        """ test that pathing kicks in to move towards far away food """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=12)
        data.set_food([(0, 0)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=12)
        data.set_food([(0, 10)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_get_closer_food(self):
        """ when not contested get closer food """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=10)
        data.set_food([(1, 5), (7, 5)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_get_food_if_close_not_hungry(self):
        """ food is right beside us so might as well grab it """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=80)
        data.set_food([(4, 5)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_contested_close_bigger(self):
        """ contested food - close - bigger - should go for it """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7), (5, 8)], health=10)
        data.set_food([(3, 5)])
        data.add_enemy([(3, 7), (3, 8), (3, 9)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_contested_close_bigger_alternate(self):
        """ contested food - close - bigger - other food available """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7), (5, 8)], health=10)
        data.set_food([(3, 5), (7, 5)])
        data.add_enemy([(3, 7), (3, 8), (3, 9)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_contested_close_equal(self):
        """ contested food - close - same size - move a spot closer maybe other snake isn't going for it """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=30)
        data.set_food([(3, 5)])
        data.add_enemy([(3, 7), (3, 8), (3, 9)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_contested_touching_equal(self):
        """ contested food - touching - same size - this would be suicide and we can't rely on other snakes accounting for that """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=30)
        data.set_food([(4, 5)])
        data.add_enemy([(4, 6), (4, 7), (4, 8)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] != 'left')

    def test_contested_close_equal_low(self):
        """ contested food - close - same size - low food """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=10)
        data.set_food([(3, 5)])
        data.add_enemy([(3, 7), (3, 8), (3, 9)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_contested_close_equal_low_alternate(self):
        """ contested food - close - same size - low food - other food available"""
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=10)
        data.set_food([(3, 5), (7, 5)])
        data.add_enemy([(3, 7), (3, 8), (3, 9)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_contested_close_smaller(self):
        """ contested food - close - smaller - move one closer to see what's up """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=30)
        data.set_food([(3, 5)])
        data.add_enemy([(3, 7), (3, 8), (3, 9), (3, 10)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_contested_touching_smaller(self):
        """ contested food - touching - smaller - getting food in this case is suicide """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=30)
        data.set_food([(4, 5)])
        data.add_enemy([(4, 6), (4, 7), (4, 8), (4, 9)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] != 'left')

    def test_contested_far(self):
        """ contested food - far - should go for alternate """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=30)
        data.set_food([(0, 5), (9, 5)])
        data.add_enemy([(0, 6), (0, 7), (0, 8)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] != 'left')

    def test_blocked_in_potential_big_snake(self):
        data = TestGameData()
        data.set_dimensions(15, 15)
        data.set_self(
            [
                (5, 8), (4, 8), (4, 7), (3, 7), (2, 7), (1, 7), (1, 8), (2, 8), (3, 8), (3, 9),
                (3, 10), (4, 10), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (10, 10),
                (9, 10), (8, 10), (7, 10), (6, 10), (6, 10)
            ]
        )
        data.set_food([(5, 7), (10, 2), (0, 12), (1, 5), (0, 8), (10, 14), (2, 12), (5, 0), (0, 5), (4, 13)])
        data.add_enemy(
            [
                (6, 7), (7, 7), (8, 7), (9, 7), (9, 6), (10, 6), (11, 6), (11, 5), (12, 5), (13, 5), (13, 4),
                (13, 3), (13, 2), (13, 1), (13, 0), (12, 0), (11, 0), (10, 0), (10, 1), (11, 1), (12, 1),
                (12, 2), (11, 2), (11, 3), (11, 4), (10, 4), (10, 3), (9, 3), (9, 2), (9, 1), (9, 0), (8, 0),
                (8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (0, 1), (0, 2), (1, 2), (1, 3),
                (2, 3), (3, 3), (4, 3), (4, 3)
            ]
        )

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')
