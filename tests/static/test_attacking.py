# import unittest
# import requests

# from utils import TEST_INSTANCE, TestGameData


# class TestAttackLogic(unittest.TestCase):
#     def test_head_to_head_bigger(self):
#         """ attack in a head to head fashion """
#         data = TestGameData()
#         data.set_self([(5, 5), (5, 6), (5, 7), (5, 8)])
#         data.add_enemy([(5, 3), (5, 2), (5, 1)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'up')

#         # follow up move if the dodged
#         data = TestGameData()
#         data.set_self([(5, 4), (5, 5), (5, 6), (5, 7)])
#         data.add_enemy([(4, 3), (5, 3), (5, 2)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'left')

#     def test_enemy_between_snake_wall(self):
#         """ attack an enemy snake when it is between you and the wall """
#         data = TestGameData()
#         data.set_self([(1, 5), (1, 6), (1, 7), (1, 8)])
#         data.add_enemy([(0, 7), (0, 8)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'left')

#     def test_enemy_between_snake_wall_collision(self):
#         """ attack an enemy with head collision when between you and the wall """
#         data = TestGameData()
#         data.set_self([(1, 5), (1, 6), (1, 7), (1, 8)])
#         data.add_enemy([(0, 6), (0, 7), (0, 8)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'left')

#     def test_enemy_between_snake_snake(self):
#         """ attack an enemy snake when it is between you and another snake"""
#         data = TestGameData()
#         data.set_self([(3, 5), (3, 6), (3, 7), (3, 8)])
#         data.add_enemy([(2, 7), (2, 8)])
#         data.add_enemy([(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'left')

#     def test_enemy_between_snake_snake_collision(self):
#         """ attack an enemy snake when it is between you and another snake but is level (head on collision) """
#         data = TestGameData()
#         data.set_self([(3, 5), (3, 6), (3, 7), (3, 8)])
#         data.add_enemy([(2, 6), (2, 7), (2, 8)])
#         data.add_enemy([(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (1, 3)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'left')

#     def test_enemy_between_snake_snake_other_attack_level(self):
#         """ don't attack in this case if our snake is smaller """
#         data = TestGameData()
#         data.set_self([(3, 5), (3, 6), (3, 7), (3, 8)])
#         data.add_enemy([(2, 6), (2, 7), (2, 8)])
#         data.add_enemy([(1, 5), (1, 6), (1, 7), (1, 8), (1, 9)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'left')

#         data = TestGameData()
#         data.set_self([(3, 5), (3, 6), (3, 7), (3, 8)])
#         data.add_enemy([(2, 6), (2, 7), (2, 8)])
#         data.add_enemy([(1, 5), (1, 6), (1, 7), (1, 8)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'left')

#     def test_enemy_between_snake_snake_same_length(self):
#         """ don't attack in this case if our snake is smaller """
#         data = TestGameData()
#         data.set_self([(3, 5), (3, 6), (3, 7)])
#         data.add_enemy([(2, 6), (2, 7), (2, 8)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'left')

#     def test_enemy_between_snake_wall_right(self):
#         """ should tunnel them into wall and not cut them off """
#         data = TestGameData()
#         data.set_self([(17, 18), (16, 18), (15, 18), (14, 18), (14, 17), (14, 16)])
#         data.add_enemy([(16, 19), (15, 19), (14, 19), (13, 19), (12, 19), (12, 18), (13, 18)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'right')

#     def test_enemy_between_snake_wall_up(self):
#         """ should tunnel them into wall and not cut them off """
#         data = TestGameData()
#         data.set_self([(1, 3), (1, 4), (1, 5), (1, 6), (1, 7)])
#         data.add_enemy([(0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)])

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertEqual(response.json()['move'], 'up')

#     def test_dont_attack_through_head(self):
#         """ this can be caused by removing a dead enemy snake that has no option sif it is our head blocking them (we might suicide into them) """
#         data = TestGameData()
#         data.set_self(
#             [
#                 (17, 8), (17, 7), (16, 7), (15, 7), (15, 6), (15, 5), (15, 4), (14, 4), (13, 4), (12, 4), (11, 4),
#                 (10, 4), (9, 4), (8, 4), (7, 4), (6, 4), (5, 4), (4, 4), (4, 5), (4, 6), (3, 6), (2, 6), (1, 6), (1, 7),
#                 (2, 7), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (4, 13), (4, 14), (4, 15), (5, 15),
#                 (5, 16), (6, 16), (7, 16), (8, 16), (9, 16), (10, 16), (10, 15), (11, 15), (11, 14), (12, 14), (12, 15),
#                 (12, 16), (12, 17), (13, 17), (14, 17), (14, 18), (15, 18), (16, 18), (17, 18), (17, 17), (17, 16),
#                 (17, 15), (17, 14), (16, 14)
#             ]
#         )
#         data.set_food([(8, 19), (7, 1), (17, 0)])
#         data.add_enemy(
#             [
#                 (16, 8), (15, 8), (14, 8), (13, 8), (12, 8), (11, 8), (11, 7), (11, 6), (10, 6), (10, 7), (9, 7), (8, 7),
#                 (7, 7), (6, 7), (6, 8), (5, 8), (4, 8), (4, 9), (4, 10), (4, 11), (4, 12), (5, 12), (6, 12), (7, 12),
#                 (8, 12), (9, 12), (9, 13), (10, 13), (11, 13), (11, 12), (11, 11), (12, 11), (12, 10), (11, 10), (10, 10),
#                 (9, 10), (9, 11), (8, 11), (7, 11), (6, 11), (5, 11), (5, 10), (6, 10), (6, 9), (7, 9), (8, 9), (9, 9),
#                 (10, 9), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 9), (17, 9)
#             ]
#         )

#         response = requests.post(TEST_INSTANCE,  json=data.data)
#         self.assertTrue(response.json()['move'] != 'left')