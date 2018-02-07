import unittest
import requests

from utils import TEST_INSTANCE, TestGameData


class TestAvoidanceLogic(unittest.TestCase):
    def test_corner(self):
        """ turn at a corner """
        data = TestGameData()
        data.set_self([(0, 0), (0, 1), (0, 2)], health=10)

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_head_to_head_smaller(self):
        """ don't suicide into snakes """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)])
        data.add_enemy([(5, 4), (5, 3), (5, 2), (5, 1)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] in ['right', 'left'])

    def test_head_to_tail_bigger(self):
        """ don't attack tail if our snake is bigger """
        data = TestGameData()
        data.set_self([(5, 5), (5, 6), (5, 7)])
        data.add_enemy([(5, 3), (5, 4)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] != 'up')

    def test_avoid_tunnel(self):
        """ don't go down tunnels that have a dead end """
        data = TestGameData()
        data.set_self([(0, 4), (0, 5), (0, 6)])
        data.add_enemy([(1, 0), (1, 1), (1, 2), (1, 3)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    def test_avoid_tail_growth(self):
        """ know that you needd to path around enemy tail growth """
        data = TestGameData()
        data.set_self([(5, 6), (5, 7), (5, 8)], health=10)
        data.add_enemy([(7, 5), (6, 5), (5, 5)])
        data.set_food([(5, 4), (8, 5)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertNotEqual(response.json()['move'], 'up')

    def test_avoid_self(self):
        """ avoid yourself when you are big and between yourself and the wall """
        data = TestGameData()
        data.set_self([(0, 5), (0, 6), (0, 7), (0, 8), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (1, 3)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

    def test_enemy_between_snake_wall_collision(self):
        """ don't attack in this case if our snake is smaller """
        data = TestGameData()
        data.set_self([(1, 5), (1, 6)])
        data.add_enemy([(0, 6), (0, 7), (0, 8)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] != 'left')

    def test_enemy_between_snake_snake_collision(self):
        """ don't attack in this case if our snake is smaller """
        data = TestGameData()
        data.set_self([(3, 5), (3, 6)])
        data.add_enemy([(2, 6), (2, 7), (2, 8)])
        data.add_enemy([(1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertTrue(response.json()['move'] != 'left')

    def test_stuck_between_corner_and_snake_last_chance(self):
        """ only chance for survival is to go where bigger snake's head might be """
        data = TestGameData()
        data.set_self([(0, 0), (0, 1), (0, 2)], health=10)
        data.add_enemy([(1, 1), (1, 2), (1, 3), (1, 4)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    # fails: due to crashing into larger snake rather than smaller
    def test_stuck_between_two_snakes_turn_into_shorter_one(self):
        """ stuck between two snakes collide head on with shorter one """
        data = TestGameData()
        data.set_self([(4, 0), (4, 1), (4, 2)], health=10)
        data.add_enemy([(5, 1), (5, 2), (5, 3), (5, 4)])
        data.add_enemy([(3, 1), (3, 2)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    # fails: chooses suicide rather than move into _potentially_ dangerous square
    def test_corner_must_turn_into_tail(self):
        """ only option is to turn where tail _could_ be if enemy grows """
        data = TestGameData()
        data.set_self([(0, 0), (0, 1), (0, 2)], health=10)
        data.add_enemy([(1, 1), (1, 0)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'right')

    # fails: if hungry
    def test_dont_trap_self(self):
        """ do not enter boxed off region that is smaller than body """
        data = TestGameData()
        data.set_self([(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (4, 2), (4, 1), (4, 0), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)], health=49)
        data.set_food([(0, 0)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'down')

    def test_if_trapped_choose_smaller_trap_small_body(self):
        """ if given two dead ends, choose the larger one """
        data = TestGameData()
        # size 5 body
        data.set_self([(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)], health=10)
        # size 3 region
        data.add_enemy([(0, 1), (1, 1), (2, 1)])
        # size 2 region
        data.add_enemy([(6, 0), (6, 1), (5, 1), (4, 1)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_if_trapped_choose_smaller_trap_large_body(self):
        """ if given two dead ends, choose the larger one """
        data = TestGameData()
        # size 24 body
        data.set_self([(5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
                       (5, 6), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6),
                       (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7),
                       (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7)],
                        health=10)
        # size 20 region
        data.add_enemy([(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)])
        # size 15 region
        data.add_enemy([(6, 5), (7, 5), (8, 5), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (9, 0)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'left')

    def test_trap_self_if_absolutely_necessary(self):
        """ enter boxed off region that is smaller than body if other paths kill us """
        data = TestGameData()
        data.set_self([(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (4, 2), (4, 1), (4, 0), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)], health=10)
        data.add_enemy([(0, 5), (0, 4), (1, 4)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

    def test_collide_head_on_with_smaller_rather_than_trap(self):
        """ choose head on collision with smaller snake rather than go into trap """
        data = TestGameData()
        data.set_self([(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (4, 2), (4, 1), (4, 0), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)], health=10)
        data.add_enemy([(1, 4), (2, 4)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'down')

    def test_avoid_moving_into_possible_cut_off_trap(self):
        """ do not move into a tunnel that could easily become a trap """
        data = TestGameData()
        data.set_self([(0, 3), (1, 3), (2, 3)], health=10)
        data.add_enemy([(1, 6), (1, 5), (1, 4), (2, 4), (3, 4)])

        response = requests.post(TEST_INSTANCE,  json=data.data)
        self.assertEqual(response.json()['move'], 'up')

