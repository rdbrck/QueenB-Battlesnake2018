import time
import logging
from contextlib import contextmanager

from .constants import DIR_NAMES, DIR_VECTORS


logging.basicConfig()
logger = logging.getLogger(__name__)


@contextmanager
def timing(label="previous action", time_remaining=[200]):
    start_time = time.time()
    yield
    time_elapsed = time.time() - start_time
    time_remaining[0] = time_remaining[0] - (time_elapsed * 1000)
    logger.info('{} took {}ms'.format(label, time_elapsed * 1000))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, b):
    return (a[0] * b[0], a[1] * b[1])


def dist(a, b):
    """ Returns the 'manhattan distance' between a and b """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def surrounding(pos):
    return [
        (pos[0], pos[1] + 1),
        (pos[0] + 1, pos[1]),
        (pos[0] + 1, pos[1] + 1),
        (pos[0] + 1, pos[1] - 1),
        (pos[0], pos[1] - 1),
        (pos[0] - 1, pos[1]),
        (pos[0] - 1, pos[1] - 1),
        (pos[0] - 1, pos[1] + 1)
    ]


def neighbours(pos):
    """ Gets coordinates of neighbour coordinates to a coordinate. """
    return [
        (pos[0], pos[1] + 1),
        (pos[0] + 1, pos[1]),
        (pos[0], pos[1] - 1),
        (pos[0] + -1, pos[1])
    ]


def touching(pos1, pos2):
    """ tells you if two positions are touching """
    if pos1[0] == pos2[0] and abs(pos1[1] - pos2[1]) == 1:
        return True
    if pos1[1] == pos2[1] and abs(pos1[0] - pos2[0]) == 1:
        return True
    return False


def translate_to_direction(new_pos, old_pos):
    """ Translates the change between two positions into a direction name. """
    return DIR_NAMES[DIR_VECTORS.index(sub(new_pos, old_pos))]


def get_direction(cur_pos, next_pos):
    if cur_pos[0] == next_pos[0]:
        if next_pos[1] < cur_pos[1]:
            return 'up'
        return 'down'
    elif cur_pos[1] == next_pos[1]:
        if next_pos[0] < cur_pos[0]:
            return 'left'
        return 'right'


def get_directions(cur_pos, next_pos):
    if cur_pos[0] > next_pos[0]:
        if cur_pos[1] > next_pos[1]:
            return ['left', 'up']
        elif cur_pos[1] < next_pos[1]:
            return ['left', 'down']
        return ['left']
    elif cur_pos[0] < next_pos[0]:
        if cur_pos[1] > next_pos[1]:
            return ['right', 'up']
        elif cur_pos[1] < next_pos[1]:
            return ['right', 'down']
        return ['right']
    elif cur_pos[1] > next_pos[1]:
        return ['up']
    return ['down']


def get_next_from_direction(position, direction):
    if direction == 'right':
        return (position[0]+1, position[1])
    elif direction == 'left':
        return (position[0]-1, position[1])
    elif direction == 'up':
        return (position[0], position[1]-1)
    return (position[0], position[1]+1)


def food_in_box(flood_squares, board):
    for fud in board.food:
        if fud in flood_squares:
            return True
    return False


def next_to_wall(pos, board):
    if pos[0] == (board.width - 1) or pos[0] == 0:
        return True
    if pos[1] == (board.height - 1) or pos[1] == 0:
        return True
    return False
