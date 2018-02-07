# import unittest
# import requests

# from utils import TEST_INSTANCE, TestGameData


# class TestAvoidanceLogic(unittest.TestCase):
#     def test_corner(self):
#         """ turn at a corner """
#         data = TestGameData()
#         data.set_self([(0, 0), (0, 1), (0, 2)], health=10)

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'right')

#     def test_head_to_head_smaller(self):
#         """ don't suicide into snakes """
#         data = TestGameData()
#         data.set_self([(5, 5), (5, 6), (5, 7)])
#         data.add_enemy([(5, 4), (5, 3), (5, 2), (5, 1)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] in ['right', 'left'])

#     def test_head_to_tail_bigger(self):
#         """ don't attack tail if our snake is bigger """
#         data = TestGameData()
#         data.set_self([(5, 5), (5, 6), (5, 7)])
#         data.add_enemy([(5, 3), (5, 4)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'up')

#     def test_avoid_tunnel(self):
#         """ don't go down tunnels that have a dead end """
#         data = TestGameData()
#         data.set_self([(0, 4), (0, 5), (0, 6)])
#         data.add_enemy([(1, 0), (1, 1), (1, 2), (1, 3)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'right')

#     def test_avoid_tail_growth(self):
#         """ know that you needd to path around enemy tail growth """
#         data = TestGameData()
#         data.set_self([(5, 6), (5, 7), (5, 8)], health=10)
#         data.add_enemy([(7, 5), (6, 5), (5, 5)])
#         data.set_food([(5, 4), (8, 5)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertNotEqual(response.json()['move'], 'up')

#     def test_avoid_self(self):
#         """ avoid yourself when you are big and between yourself and the wall """
#         data = TestGameData()
#         data.set_self([(0, 5), (0, 6), (0, 7), (0, 8), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (1, 3)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'up')

#     def test_enemy_between_snake_wall_collision(self):
#         """ don't attack in this case if our snake is smaller """
#         data = TestGameData()
#         data.set_self([(1, 5), (1, 6)])
#         data.add_enemy([(0, 6), (0, 7), (0, 8)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'left')

#     def test_enemy_between_snake_snake_collision(self):
#         """ don't attack in this case if our snake is smaller """
#         data = TestGameData()
#         data.set_self([(3, 5), (3, 6)])
#         data.add_enemy([(2, 6), (2, 7), (2, 8)])
#         data.add_enemy([(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'left')
