import heapq
import time
import random

from collections import deque
from entities import Board
from math import floor, ceil
from copy import copy, deepcopy

from utils import neighbours, surrounding, dist, mul, sub, timing
from constants import DIR_NAMES, DIR_VECTORS, FOOD, EMPTY, SNAKE


def _rate_cell(cell, board, recurse = False):
    """ rates a cell based on proximity to other snakes, food, the edge of the board, etc """
    cells = filter(lambda m_cell: board.inside(m_cell), surrounding(cell))
    cells = map(lambda m_cell: (m_cell, board.get_cell(m_cell)), cells)
    cell_value = reduce(lambda carry, m_cell: carry + [0.5, -5, 2, 0][m_cell[1]], cells, 0)

    if recurse or cell_value < 2: return cell_value
    else: return cell_value + sum([
        _rate_cell(m_cell, board) / 10
        for m_cell in surrounding(cell) if board.inside(m_cell)
    ])


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

    def _find_safest(bounds = m_bounds, offset = (0, 0), depth = 0, carry = []):
        sector_width = (bounds[1][0] - bounds[0][0])
        sector_height = (bounds[1][1] - bounds[0][1])

        center_point = (
            int(offset[0] + floor(sector_width / 2)),
            int(offset[1] + floor(sector_height / 2))
        )

        if depth == max_depth or (sector_height * sector_width <= 1):
            return sorted(carry, lambda cell_1, cell_2: cell_1[1] < cell_2[1])[:3]

        # filter cells that we've already rated
        carry_cells = [ cell[0] for cell in carry ]
        surrounding_ratings = [
            ((cell[0], cell[1]), _rate_cell((cell[0], cell[1]), board, True))
            for cell in surrounding(center_point)
            if cell not in carry_cells and board.inside(cell) and board.get_cell(cell) != SNAKE
        ]

        # randomize to remove bias towards last in surrounding list
        random.shuffle(surrounding_ratings)
        position, rating = reduce(lambda m_carry, cell: cell if cell[1] > m_carry[1] else m_carry, surrounding_ratings, (None, -100000000000))

        new_bounds = bounds
        if position is not None:
            carry = carry + [(position, rating)]
            direction_vector = sub(position, center_point)

            # diagnal
            if abs(direction_vector[0]) == abs(direction_vector[1]):
                direction_vector = list(direction_vector) # tuples are immutable
                direction_vector[int(time.time()) % 2] = 0 # 300% faster than random.randint()
                direction_vector = tuple(direction_vector) # back to tuple because DIR_VECTOR contains tuples

            direction = DIR_NAMES[DIR_VECTORS.index(direction_vector)]

            if direction == "up":
                new_bounds = [offset, (bounds[1][0], bounds[1][1])]
            elif direction == "down":
                offset = (offset[0], center_point[1])
                new_bounds = [offset, (bounds[1][0], bounds[1][1])]
            elif direction == "left":
                new_bounds = [offset, (center_point[0], bounds[1][1])]
            else: # right
                offset = (center_point[0], offset[1])
                new_bounds = [offset, (bounds[0][0], bounds[1][1])]

        return _find_safest(new_bounds, offset, depth + 1, carry = carry)

    # set up initial bounds
    if direction == "up":
        bounds = [(0, 0), (board.width, current_position[1])]
    elif direction == "down":
        bounds = [(0, current_position[1]), (board.width, board.height)]
    elif direction == "right":
        bounds = [(current_position[0], 0), (board.width, board.height)]
    else: # left
        bounds = [(0, 0), (current_position[0], board.height)]

    return _find_safest(bounds, bounds[0])


def find_food(current_position, health_remaining, board, board_food):
    """ finds and rates food positions """
    rated_food = map(lambda food: (food, _rate_cell(food, board, True)), board_food)
    return sorted(rated_food, lambda food_1, food_2: food_1[1] > food_2[1])


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
        while(node != None):
            path.insert(0, (node[0], node[1])) # Reverse
            node = node[2]
        return return_list.append(path[1:])

    x = starting_position[0]
    y = starting_position[1]
    board_copy = deepcopy(board)
    board_copy.set_cell((x, y), 0)

    for excluded_point in exclude:
        board_copy.set_cell(excluded_point, "B")

    queue = deque([(x, y, None)])

    while len(queue) > 0:
        node = queue.popleft()
        x = node[0]
        y = node[1]

        if board_copy.inside((x, y)) == True:
            if (x, y) == target_position: # If we reach target_position
                return _get_path_from_nodes(node) # Rebuild path

            if (board_copy.outside((x, y)) == True or board_copy.get_cell((x, y)) == "B" or board_copy.get_cell((x, y)) == 1) and not (x, y) == starting_position: # Snakes
                continue

            board_copy.set_cell((x, y), "B") # Mark as explored

            for i in neighbours(node):
                if board.inside((i[0], i[1])):
                    queue.append((i[0], i[1], node))

    return None # No path
