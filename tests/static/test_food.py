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
        data.set_self([(5, 5), (5, 6), (5, 7)], health=10)
        data.set_food([(0, 0)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)], health=10)
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

    @unittest.skip("Skipping as snake doesn't eat if it's not hungry. Could be implemented as an improvement.")
    def test_get_food_if_close_not_hungry(self):
        """ food is right beside us so might as well grab it """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)])
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

    @unittest.skip("Skipping as the logic here is debatable. Should we be aggressive or defensive?")
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

    @unittest.skip("This needs to be fixed. It should not commit suicide for food.")
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

    @unittest.skip("This needs to be fixed. It should go for the alternate food.")
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

    @unittest.skip("This needs to be fixed. We shouldn't commit suicide.")
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