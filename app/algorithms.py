import time
import random
from functools import reduce
from math import floor
from copy import deepcopy
from collections import deque

from .utils import neighbours, surrounding, sub
from .constants import DIR_NAMES, DIR_VECTORS, SNAKE, EMPTY, FOOD, SPOILED
from .constants import FOOD_RATING, SPOILED_RATING, EMPTY_RATING, BODY_RATING, ENEMY_RATING, OUT_SIDE_BOARD_RATING


def _rate_cell(cell, board, bloom_level=4):
    """ rates a cell based on proximity to other snakes, food, the edge of the board, etc """

    cells = []
    # Get all the cells of "bloom_level" number of circles surrounding the given cell.
    for x in range(-bloom_level, bloom_level+1):
        for y in range(-bloom_level, bloom_level+1):
            division_factor = max(abs(x), abs(y))
            if division_factor == 0:
                division_factor = 1
            cells.append(((cell[0]+x, cell[1]+y), division_factor))

    # EMPTY = 0
    # SNAKE = 1
    # FOOD = 2
    # SPOILED = 3
    cell_weightings = [EMPTY_RATING, ENEMY_RATING, FOOD_RATING, SPOILED_RATING, BODY_RATING, OUT_SIDE_BOARD_RATING]
    cell_values = []
    own_snake = board.get_snake(board.own_snake_id)

    for m_cell in cells:
        weight_key = 5  # Outside the board
        if board.inside(m_cell[0]):
            weight_key = board.get_cell(m_cell[0])
            if m_cell[0] in own_snake.body:
                weight_key = 4
        cell_values.append((weight_key, m_cell[1]))

    return reduce(lambda carry, m_cell: carry + cell_weightings[m_cell[0]]/m_cell[1], cell_values, 0)


def flood_fill(board, start_pos, allow_start_in_occupied_cell=False):
    """
    Flood fill is an algorithm that expands from a starting position into adjacent
    vacant cells. Returns the set of all vacant cells found.

    If allow_start_in_occupied_cell is True, the flood fill start position may be occupied
    and the start position will be included in the resulting set.
    """
    visited = set()

    if not allow_start_in_occupied_cell and not board.vacant(start_pos):
        return visited

    visited.add(start_pos)
    todo = deque([start_pos])

    while todo:
        current = todo.popleft()
        for p in neighbours(current):
            if p not in visited and board.vacant(p):
                visited.add(p)
                todo.append(p)

    return visited


def find_safest_positions(current_position, direction, board):
    """
    finds a position in a binary-search like fashion, this could probably just
    linearly scan the whole board, rating every position, and then returning the highest n
    positions
    """

    # set up initial bounds
    bound_x = current_position[0]+1 if current_position[0] != (board.width-1) else current_position[0]
    bound_y = current_position[1]+1 if current_position[1] != (board.height-1) else current_position[1]
    if direction == "up":
        bounds = [(0, 0), ((board.width-1), bound_y)]
    elif direction == "down":
        bounds = [(0, bound_y), ((board.width-1), (board.height-1))]
    elif direction == "right":
        bounds = [(bound_x, 0), ((board.width-1), (board.height-1))]
    else:  # left
        bounds = [(0, 0), (bound_x, (board.height-1))]

    # Create a checkerboard of positions to check
    skip_cell_modulous = 2
    potential_cells = []
    checkerboard_count = 0
    for x in range(bounds[0][0], bounds[1][0]+1):
        if checkerboard_count != 0:
            checkerboard_count += 1
        for y in range(bounds[0][1], bounds[1][1]+1):
            checkerboard_count += 1
            if (checkerboard_count % skip_cell_modulous) == 0:
                continue
            potential_cells.append(((x, y), _rate_cell((x, y), board)))
    results = sorted(potential_cells, key=lambda x: x[1], reverse=True)
    return results[:5]


def find_food(current_position, health_remaining, board, board_food):
    """ finds and rates food positions """
    rated_food = [(food, _rate_cell(food, board)) for food in board_food]
    return sorted(rated_food, key=lambda x: x[1], reverse=True)


def bfs(starting_position, target_position, board, exclude, return_list):
    """
    BFS implementation to search for path to food

    :param starting_position: starting position
    :param target_position: target position
    :param board: the board state

    example:

    bfs((0,0), (2,2), board) -> [(0,0), (0,1), (0,2), (1,2), (2,2)]
    """
    def _get_path_from_nodes(node):
        path = []
        while(node):
            path.insert(0, (node[0], node[1]))  # Reverse
            node = node[2]
        return return_list.append(path[1:])

    x = starting_position[0]
    y = starting_position[1]
    board_copy = deepcopy(board)
    board_copy.set_cell((x, y), EMPTY)

    for excluded_point in exclude:
        board_copy.set_cell(excluded_point, SPOILED)

    queue = deque([(x, y, None)])

    while len(queue) > 0:
        node = queue.popleft()
        x = node[0]
        y = node[1]

        if (x, y) == target_position:  # If we reach target_position
            return _get_path_from_nodes(node)  # Rebuild path

        if (board_copy.get_cell((x, y)) == SPOILED or board_copy.get_cell((x, y)) == SNAKE) and not (x, y) == starting_position:
            continue

        board_copy.set_cell((x, y), SPOILED)  # Mark as explored

        for i in neighbours(node):
            if board_copy.inside((i[0], i[1])):
                queue.append((i[0], i[1], node))

    return None  # No path
