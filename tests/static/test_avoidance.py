import unittest
import requests
from datetime import datetime, timedelta

from utils import TEST_INSTANCE, TestGameData


class TestAvoidanceLogic(unittest.TestCase):
    # def test_corner(self):
    #     """ turn at a corner """
    #     data = TestGameData()
    #     data.set_self([(0, 0), (0, 1), (0, 2)], health=10)

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_head_to_head_smaller(self):
    #     """ don't suicide into snakes """
    #     data = TestGameData()
    #     data.set_self([(5, 5), (5, 6), (5, 7)])
    #     data.add_enemy([(5, 4), (5, 3), (5, 2), (5, 1)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertTrue(response.json()['move'] in ['right', 'left'])

    # def test_head_to_tail_bigger(self):
    #     """ don't attack tail if our snake is bigger """
    #     data = TestGameData()
    #     data.set_self([(5, 5), (5, 6), (5, 7)])
    #     data.add_enemy([(5, 3), (5, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertTrue(response.json()['move'] != 'up')

    # def test_avoid_tunnel(self):
    #     """ don't go down tunnels that have a dead end """
    #     data = TestGameData()
    #     data.set_self([(0, 4), (0, 5), (0, 6)])
    #     data.add_enemy([(1, 0), (1, 1), (1, 2), (1, 3)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_avoid_tail_growth(self):
    #     """ know that you need to path around enemy tail growth """
    #     data = TestGameData()
    #     data.set_self([(5, 6), (5, 7), (5, 8)], health=10)
    #     data.add_enemy([(7, 5), (6, 5), (5, 5), (5, 5)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertNotEqual(response.json()['move'], 'up')

    # def test_avoid_self(self):
    #     """ avoid yourself when you are big and between yourself and the wall """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (0, 5), (0, 6), (0, 7), (0, 8), (1, 8),
    #             (1, 7), (1, 6), (1, 5), (1, 4), (1, 3)
    #         ]
    #     )

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'up')

    # def test_enemy_between_snake_wall_collision(self):
    #     """ don't attack in this case if our snake is smaller """
    #     data = TestGameData()
    #     data.set_self([(1, 5), (1, 6)])
    #     data.add_enemy([(0, 6), (0, 7), (0, 8)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertTrue(response.json()['move'] != 'left')

    # def test_enemy_between_snake_snake_collision(self):
    #     """ don't attack in this case if our snake is smaller """
    #     data = TestGameData()
    #     data.set_self([(3, 5), (3, 6)])
    #     data.add_enemy([(2, 6), (2, 7), (2, 8)])
    #     data.add_enemy([(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertTrue(response.json()['move'] != 'left')

    # def test_stuck_between_two_snakes_turn_into_shorter_one(self):
    #     """ stuck between two snakes collide head on with shorter one """
    #     data = TestGameData()
    #     data.set_self([(4, 0), (4, 1), (4, 2)], health=10)
    #     data.add_enemy([(5, 1), (5, 2), (5, 3), (5, 4)])
    #     data.add_enemy([(3, 1), (3, 2)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'left')

    # def test_move_into_potential_position_small(self):
    #     """ only option is to turn where tail _could_ be if enemy grows """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
    #             (4, 2), (4, 1), (4, 0), (5, 0), (5, 1),
    #             (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
    #             (5, 7)
    #         ],
    #         health=10
    #     )
    #     data.add_enemy([(1, 4), (2, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_avoid_moving_into_possible_cut_off_trap(self):
    #     """ do not move into a tunnel that could easily become a trap """
    #     data = TestGameData()   
    #     data.set_self([(0, 3), (1, 3), (2, 3)], health=10)
    #     data.add_enemy([(1, 6), (1, 5), (1, 4), (2, 4), (3, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'up')

    # def test_dont_trap_self(self):
    #     """ do not enter boxed off region that is smaller than body """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
    #             (4, 2), (4, 1), (4, 0), (5, 0), (5, 1),
    #             (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
    #             (5, 7)
    #         ],
    #         health=49
    #     )
    #     data.set_food([(0, 0)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_stuck_between_corner_and_snake_last_chance(self):
    #     """ only chance for survival is to go where bigger snake's head might be """
    #     data = TestGameData()
    #     data.set_self([(0, 0), (0, 1), (0, 2)], health=10)
    #     data.add_enemy([(1, 1), (1, 2), (1, 3), (1, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_corner_must_turn_into_tail(self):
    #     """ only option is to turn where tail _could_ be if enemy grows """
    #     data = TestGameData()
    #     data.set_self([(0, 0), (0, 1), (0, 2)], health=10)
    #     data.add_enemy([(2, 1), (1, 1), (1, 0)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_tunnel_self_max_health(self):
    #     """ only option is to turn where tail _could_ be if enemy grows """
    #     data = TestGameData()
    #     data.set_self([
    #         (18, 0), (18, 1), (18, 2), (18, 3), (18, 4), (18, 5),
    #         (18, 6), (18, 7), (18, 8), (18, 9), (18, 10), (18, 11),
    #         (18, 12), (18, 13), (18, 14), (18, 15), (18, 16), (18, 17),
    #         (18, 18), (18, 19), (17, 19), (16, 19), (15, 19), (14, 19)])
    #     data.add_enemy([(1, 1), (1, 0)])
    #     data.set_food([(19, 0)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'left')

    # def test_if_trapped_choose_smaller_trap_small_body_tail(self):
    #     """ if given two dead ends, choose one the snake can escape - tail regarding food """
    #     data = TestGameData()
    #     # size 3 body
    #     data.set_self([(3, 0), (3, 1), (3, 2)], health=10)
    #     # size 3 region
    #     data.add_enemy([(0, 1), (1, 1), (2, 1)])
    #     # size 2 region
    #     data.add_enemy([(6, 0), (6, 1), (5, 1), (4, 1), (4, 2)])
    #     data.set_food([(7, 0)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'left')

    # def test_if_trapped_choose_smaller_trap_large_body_food(self):
    #     """ if given two dead ends, choose the one that will open up according to the distance of our snake to the tail """
    #     data = TestGameData()
    #     # size 24 body
    #     data.set_self(
    #         [
    #             (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
    #             (5, 5), (5, 6), (4, 6), (3, 6), (2, 6),
    #             (1, 6), (0, 6), (0, 7), (1, 7), (2, 7),
    #             (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
    #             (8, 7), (9, 7), (10, 7), (11, 7)
    #         ],
    #         health=10
    #     )
    #     # size 20 region
    #     data.add_enemy([(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)])
    #     # size 15 region
    #     data.add_enemy(
    #         [
    #             (6, 5), (7, 5), (8, 5), (9, 5), (9, 4),
    #             (9, 3), (9, 2), (9, 1), (9, 0)
    #         ]
    #     )
    #     data.set_food([(6, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_trap_self_if_absolutely_necessary(self):
    #     """ enter boxed off region that is smaller than body if other paths kill us """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
    #             (4, 2), (4, 1), (4, 0), (5, 0), (5, 1),
    #             (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
    #             (5, 7)
    #         ],
    #         health=10
    #     )
    #     data.add_enemy([(0, 5), (0, 4), (1, 4)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'up')

    # def test_better_to_not_move_down(self):
    #     """ found through testing, not sure why it wouldn't go up """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (11, 6), (10, 6), (9, 6), (8, 6), (7, 6),
    #             (6, 6), (5, 6), (4, 6), (4, 7), (4, 8),
    #             (3, 8), (3, 9), (3, 10), (2, 10), (2, 11),
    #             (2, 12), (2, 13), (1, 13), (0, 13), (0, 14),
    #             (0, 15), (0, 16), (1, 16), (2, 16), (3, 16),
    #             (4, 16), (5, 16), (5, 17), (6, 17), (7, 17),
    #             (8, 17), (9, 17), (10, 17), (11, 17), (12, 17),
    #             (13, 17), (13, 18), (12, 18), (11, 18), (10, 18),
    #             (9, 18), (8, 18), (7, 18), (6, 18), (5, 18),
    #             (4, 18), (3, 18), (2, 18), (1, 18), (0, 18),
    #             (0, 19), (1, 19), (2, 19)
    #         ]
    #     )
    #     data.set_food([(14, 9), (1, 2), (8, 10), (0, 4)])
    #     data.add_enemy(
    #         [
    #             (16, 15), (15, 15), (14, 15), (13, 15), (12, 15),
    #             (11, 15), (10, 15), (9, 15), (9, 14), (10, 14), (11, 14),
    #             (12, 14), (13, 14), (14, 14), (15, 14), (16, 14), (17, 14),
    #             (18, 14), (18, 13), (17, 13), (16, 13), (16, 12), (16, 11),
    #             (16, 10), (16, 9), (15, 9), (15, 8), (14, 8), (13, 8),
    #             (13, 9), (13, 10), (13, 11), (13, 12), (13, 13), (12, 13),
    #             (11, 13), (10, 13), (9, 13), (8, 13), (8, 14), (7, 14),
    #             (6, 14), (5, 14), (4, 14), (4, 15), (3, 15), (2, 15),
    #             (2, 14), (3, 14), (3, 13), (3, 12), (4, 12), (5, 12), (6, 12),
    #             (7, 12), (8, 12), (9, 12), (9, 11), (9, 10), (9, 9), (9, 8)
    #         ]
    #     )

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertTrue(response.json()['move'] in ['right', 'up'])

    # def test_if_two_dead_ends_choose_one_with_tail_no_food(self):
    #     """ only options are dead ends, don't go for bait, choose one with tail """
    #     data = TestGameData()
    #     data.set_self([(4, 4), (4, 3), (4, 2), (4, 1), (4, 0), 
    #                    (3, 0), (2, 0), (1, 0), (0, 0), 
    #                    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), 
    #                    (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), 
    #                    (6, 5), (7, 5), (8, 5), (8, 4), (8, 3), 
    #                    (8, 2), (8, 1), (8, 0), (7, 0), (6, 0)
    #                    ], health=20)

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_if_two_dead_ends_choose_one_with_tail_food(self):
    #     """ only options are dead ends, don't go for bait, choose one with tail """
    #     data = TestGameData()
    #     data.set_self([(4, 4), (4, 3), (4, 2), (4, 1), (4, 0), 
    #                    (3, 0), (2, 0), (1, 0), (0, 0), 
    #                    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), 
    #                    (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), 
    #                    (6, 5), (7, 5), (8, 5), (8, 4), (8, 3), 
    #                    (8, 2), (8, 1), (8, 0), (7, 0), (6, 0)
    #                    ], health=20)
    #     data.set_food([(1, 1)])

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # def test_long_good_distribution_avoid_hole(self):
    #     """ tests escape logic when expecting a snakes tail to move """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (12, 6), (11, 6), (10, 6), (9, 6), (8, 6), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5),
    #             (13, 5), (14, 5), (15, 5), (16, 5), (17, 5), (18, 5), (19, 5), (19, 4), (18, 4), (17, 4),
    #             (16, 4), (15, 4), (13, 4), (12, 4), (11, 4), (10, 4), (9, 4), (8, 4), (8, 5), (8, 6), (8, 7),
    #             (8, 8)
    #         ], health=90
    #     )
    #     data.set_food([(5, 7), (16, 2), (19, 0), (0, 19)])
    #     data.add_enemy(
    #         [
    #             (11, 10), (12, 10), (13, 10), (13, 9), (13, 8), (13, 7), (14, 7), (14, 8), (14, 9), (14, 10),
    #             (15, 10), (16, 10), (17, 10), (18, 10), (19, 10), (19, 11), (18, 11), (17, 11), (16, 11), (15, 11),
    #             (14, 11), (13, 11), (12, 11), (11, 11), (10, 11), (9, 11), (8, 11), (8, 10), (8, 9)
    #         ]
    #     )

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_survival_bad_times_roundup_two(self):
    #     """ Although not intuitive we could survive if we go right """
    #     data = TestGameData()
    #     data.set_self(
    #         [
    #             (10, 0), (9, 0), (9, 1), (8, 1), (8, 0), (7, 0), (6, 0), (5, 0), (4, 0), (4, 1), (3, 1), (3, 0),
    #             (2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (1, 3), (1, 2), (1, 1), (2, 1),
    #             (2, 2), (3, 2), (4, 2), (4, 3), (5, 3), (5, 4), (6, 4), (6, 3), (6, 2), (7, 2), (7, 3), (8, 3),
    #             (9, 3), (10, 3), (10, 4), (11, 4), (11, 3), (11, 2), (11, 1), (12, 1), (12, 2), (12, 3), (12, 4),
    #             (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (11, 11), (10, 11), (9, 11), (8, 11),
    #             (7, 11), (7, 12), (6, 12), (5, 12), (5, 11), (5, 10), (4, 10), (3, 10), (3, 11), (4, 11), (4, 12),
    #             (4, 13), (3, 13), (3, 12), (2, 12)
    #         ]
    #     )
    #     data.set_food([(17, 18), (11, 10), (8, 4), (2, 3)])
    #     data.add_enemy(
    #         [
    #             (16, 17), (16, 16), (15, 16), (15, 15), (15, 14), (15, 13), (15, 12), (14, 12), (14, 13), (14, 14),
    #             (14, 15), (14, 16), (14, 17), (13, 17), (12, 17), (12, 16), (13, 16), (13, 15), (12, 15), (12, 14),
    #             (11, 14), (11, 13), (12, 13), (13, 13), (13, 12), (12, 12), (11, 12), (10, 12), (9, 12), (8, 12), (8, 13),
    #             (8, 14), (8, 15), (7, 15), (7, 14), (6, 14), (5, 14), (4, 14), (3, 14), (2, 14), (1, 14), (1, 15), (2, 15),
    #             (3, 15), (3, 16), (4, 16), (5, 16), (5, 17), (6, 17), (6, 18), (6, 19), (7, 19), (8, 19), (9, 19), (10, 19),
    #             (11, 19), (11, 18), (12, 18), (13, 18), (14, 18)
    #         ]
    #     )

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'right')

    # #The four boxed in tests demonstrate our max area when executing the longest_path method for boxed_in (NPHard)
    # def test_boxed_in_10(self):
    #     """ If we only use the NP Hard boxed in then this will pass as it is below the execution time barrier """
    #     data = TestGameData()   
    #     data.set_dimensions(2, 7)
    #     data.set_self([(0, 2), (0, 1), (1, 1), (1, 0), (0, 0), (0, 0)])

    #     time1 = datetime.now()
    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     time2 = datetime.now()

    #     self.assertTrue(time2 < time1 + timedelta(milliseconds=150))
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_boxed_in_20(self):
    #     """ If we only use the NP Hard boxed in then this will pass as it is below the execution time barrier """
    #     data = TestGameData()   
    #     data.set_dimensions(4, 7)
    #     data.set_self([(0, 2), (0, 1), (1, 1), (2, 1), (3, 1), (3, 0), (2, 0), (1, 0), (0, 0), (0, 0)])

    #     time1 = datetime.now()
    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     time2 = datetime.now()

    #     self.assertTrue(time2 < time1 + timedelta(milliseconds=150))
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_boxed_in_25(self):
    #     """ If we only use the NP Hard boxed in then this will fail as it exceeds the execution time """
    #     data = TestGameData()   
    #     data.set_dimensions(5, 7)
    #     data.set_self(
    #         [
    #             (0, 2), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
    #             (4, 0), (3, 0), (2, 0), (1, 0), (0, 0), (0, 0)
    #         ]
    #     )

    #     time1 = datetime.now()
    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     time2 = datetime.now()

    #     self.assertTrue(time2 < time1 + timedelta(milliseconds=150))
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_boxed_in_30(self):
    #     """ If we only use the NP Hard boxed in then this will fail as it exceeds the execution time """
    #     data = TestGameData()   
    #     data.set_dimensions(6, 8)
    #     data.set_self(
    #         [
    #             (0, 3), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (5, 1), (4, 1),
    #             (3, 1), (2, 1), (1, 1), (0, 1), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)
    #         ]
    #     )

    #     time1 = datetime.now()
    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     time2 = datetime.now()

    #     self.assertTrue(time2 < time1 + timedelta(milliseconds=150))
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_boxed_in_none(self):
    #     data = TestGameData()   
    #     data.set_dimensions(15, 15)
    #     data.set_self(
    #         [
    #             (5, 7), (6, 7), (6, 8), (6, 9), (6, 10), (5, 10), (5, 11), (4, 11), (3, 11), (2, 11), (1, 11),
    #             (0, 11), (0, 12), (1, 12), (2, 12), (3, 12), (4, 12), (5, 12), (5, 13), (4, 13), (3, 13), (2, 13),
    #             (1, 13), (0, 13), (0, 14), (1, 14), (2, 14), (3, 14), (4, 14), (5, 14), (6, 14), (6, 13), (6, 12),
    #             (6, 11), (7, 11), (7, 12), (7, 13), (7, 14), (8, 14), (8, 13), (8, 12), (8, 11), (8, 10), (7, 10),
    #             (7, 9), (7, 8), (8, 8), (8, 9), (9, 9), (10, 9), (10, 10), (9, 10), (9, 11), (9, 12), (9, 13),
    #             (9, 14), (10, 14), (11, 14), (11, 13), (10, 13), (10, 13)
    #         ]
    #     )
    #     data.set_food([(14, 8), (12, 12), (5, 4), (13, 8), (6, 4), (3, 0), (0, 1), (4, 1), (3, 2), (4, 0)])
    #     data.add_enemy(
    #         [
    #             (1, 8), (2, 8), (2, 7), (3, 7), (3, 6), (4, 6), (5, 6), (6, 6), (6, 5), (7, 5), (7, 4), (7, 3),
    #             (8, 3), (9, 3), (9, 4), (8, 4), (8, 5), (8, 6), (8, 7), (9, 7), (9, 6), (9, 5), (10, 5), (10, 4),
    #             (10, 3), (10, 2), (10, 1), (9, 1), (9, 2), (8, 2), (8, 1), (7, 1), (7, 0), (6, 0), (5, 0), (5, 1),
    #             (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (0, 3), (0, 4), (0, 5), (0, 6), (1, 6), (1, 6)
    #         ]
    #     )

    #     response = requests.post(TEST_INSTANCE,  json=data.data)
    #     self.assertEqual(response.json()['move'], 'down')

    # def test_2nd_snake_death_escape(self):
    #     """Test dead-end escape via 2nd snake death.

    #     AaBb.X..cC
    #     .aabbxccc.
    #     ..a.b.c...
    #     ....b.c...

    #     Snake B and Snake C create dead-ends for us (Snake X).
    #     The right dead-end caused by C is longer than the left dead-end caused
    #     by B, but we know that Snake B is about to die and so an escape route
    #     is about to appear on the left dead-end before it kills us, whereas 
    #     unless Snake C does something stupid, death is inevitable on the right
    #     dead-end. (The naive choice is the right dead-end because it's longer.)
    #     """
    #     data = TestGameData()
    #     data.set_dimensions(10, 4)
    #     data.set_self([(5, 0), (5, 1)])
    #     data.add_enemy([(2, 0), (3, 0), (3, 1), (4, 1), (4, 2), (4, 3)])
    #     data.add_enemy([(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)])
    #     data.add_enemy([(9, 0), (8, 0), (8, 1), (7, 1), (6, 1), (6, 2), (6, 3)])

    #     response = requests.post(TEST_INSTANCE, json=data.data)
    #     self.assertEqual(response.json()['move'], 'left')

    # def test_2nd_snake_death_escape_starved(self):
    #     """
    #     Test dead-end escape via 2nd snake death due to starving.

    #     ..Bb.X..cC
    #     ...bbxccc.
    #     ....b.c...
    #     ....b.c...
    #     """
    #     data = TestGameData()
    #     data.set_dimensions(10, 4)
    #     data.set_self([(5, 0), (5, 1)])
    #     data.add_enemy([(2, 0), (3, 0), (3, 1), (4, 1), (4, 2), (4, 3)], health=0)
    #     data.add_enemy([(9, 0), (8, 0), (8, 1), (7, 1), (6, 1), (6, 2), (6, 3)])

    #     response = requests.post(TEST_INSTANCE, json=data.data)
    #     self.assertEqual(response.json()['move'], 'left')

    def test_avoid_wall_when_snake_next_to_ourself(self):
        """
        If we are two away from the wall but next to a snake, chose to go up
        against the snake rather than the wall to maintain an exit route
        """
        data = TestGameData()
        data.set_dimensions(17, 17)
        data.set_food([(6, 0), (11, 0), (1, 1), (0, 13), (5, 16), (5, 15), (6, 15), (15, 13), (16, 11), (12, 10)])
        data.set_self([
            (15, 12), (14, 12), (13, 12), (12, 12), (11, 12), (10, 12), (9, 12), (8, 12), (7, 12),
            (6, 12), (5, 12), (4, 12), (3, 12), (2, 12), (1, 12), (0, 12), (0, 11), (0, 10), (0, 9)
        ])
        data.add_enemy([(14, 10), (14, 11), (13, 11), (12, 11), (11, 11), (10, 11), (9, 11), (8, 11), (7, 11), (6, 11)])

        response = requests.post(TEST_INSTANCE, json=data.data)
        self.assertEqual(response.json()['move'], 'up')

    # def test_broken_excludes_small_board_bfs(self):
    #     data = TestGameData()
    #     data.set_dimensions(20, 11)
    #     data.set_self([(18, 10), (17, 10), (16, 10), (15, 10), (14, 10)])
    #     data.add_enemy([(18, 8), (17, 8), (16, 8), (15, 8), (14, 8), (13, 8)])

    #     response = requests.post(TEST_INSTANCE, json=data.data)
    #     self.assertTrue(response.json()['move'] != 'up')