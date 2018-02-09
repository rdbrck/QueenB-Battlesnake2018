import time
import random
from functools import reduce
from math import floor
from copy import deepcopy
from collections import deque

from .utils import neighbours, surrounding, sub
from .constants import DIR_NAMES, DIR_VECTORS, SNAKE, EMPTY, FOOD, SPOILED
from .constants import FOOD_RATING, SPOILED_RATING, EMPTY_RATING, BODY_RATING, ENEMY_RATING, OUT_SIDE_BOARD_RATING


def _rate_cell(cell, board, bloom_level=10):
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


def find_safest_position(current_position, direction, board):
    """
    finds a position in a binary-search like fashion, this could probably just
    linearly scan the whole board, rating every position, and then returning the highest n
    positions
    """

    # the whole board
    m_bounds = [(0, 0), (board.width, board.height)]
    max_depth = 10

    def _find_safest(bounds=m_bounds, offset=(0, 0), depth=0, carry=[]):
        sector_width = (bounds[1][0] - bounds[0][0])
        sector_height = (bounds[1][1] - bounds[0][1])

        if depth == max_depth or (sector_height * sector_width <= 1):
            return sorted(carry, key=lambda x: x[1])[:3]

        center_point = (
            int(offset[0] + floor(sector_width / 2)),
            int(offset[1] + floor(sector_height / 2))
        )

        # filter cells that we've already rated
        carry_cells = [cell[0] for cell in carry]

        surrounding_ratings = []
        for cell in surrounding(center_point):
            if cell not in carry_cells and board.inside(cell) and board.get_cell(cell) != SNAKE:
                surrounding_ratings.append(
                    ((cell[0], cell[1]), _rate_cell((cell[0], cell[1]), board))
                )

        # randomize to remove bias towards last in surrounding list
        random.shuffle(surrounding_ratings)
        position, rating = reduce(lambda m_carry, cell: cell if cell[1] > m_carry[1] else m_carry, surrounding_ratings, (None, -100000000000))

        new_bounds = bounds
        if position is not None:
            carry = carry + [(position, rating)]
            direction_vector = sub(position, center_point)

            # diagonal
            if abs(direction_vector[0]) == abs(direction_vector[1]):
                direction_vector = list(direction_vector)  # tuples are immutable
                direction_vector[int(time.time()) % 2] = 0  # 300% faster than random.randint()
                direction_vector = tuple(direction_vector)  # back to tuple because DIR_VECTOR contains tuples

            direction = DIR_NAMES[DIR_VECTORS.index(direction_vector)]

            if direction == "up":
                new_bounds = [offset, (bounds[1][0], bounds[1][1])]
            elif direction == "down":
                offset = (offset[0], center_point[1])
                new_bounds = [offset, (bounds[1][0], bounds[1][1])]
            elif direction == "left":
                new_bounds = [offset, (center_point[0], bounds[1][1])]
            else:  # right
                offset = (center_point[0], offset[1])
                new_bounds = [offset, (bounds[0][0], bounds[1][1])]

        return _find_safest(new_bounds, offset, depth + 1, carry=carry)

    # set up initial bounds
    if direction == "up":
        bounds = [(0, 0), ((board.width-1), current_position[1])]
    elif direction == "down":
        bounds = [(0, current_position[1]), ((board.width-1), (board.height-1))]
    elif direction == "right":
        bounds = [(current_position[0], 0), ((board.width-1), (board.height-1))]
    else:  # left
        bounds = [(0, 0), (current_position[0], (board.height-1))]

    return _find_safest(bounds, bounds[0])


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
