import time
import random
from functools import reduce
from math import floor
from copy import deepcopy
from collections import deque

from .utils import neighbours, surrounding, sub, dist, touching
from .entities import Board
from .constants import DIR_NAMES, DIR_VECTORS, SNAKE, EMPTY, FOOD, SPOILED, SAFE_SPACE_FACTOR, ENABLE_CHECKERBOARD_SIZE,\
                       FOOD_RATING, SPOILED_RATING, EMPTY_RATING, BODY_RATING, ENEMY_RATING, OUT_SIDE_BOARD_RATING


def _rate_cell(cell, board, bloom_level=4):
    """ rates a cell based on proximity to other snakes, food, the edge of the board, etc """

    cells = []
    # Get all the cells of "bloom_level" number of circles surrounding the given cell.
    for x in range(-bloom_level, bloom_level+1):
        for y in range(-bloom_level, bloom_level+1):
            division_factor = dist((cell[0]+x, cell[1]+y), cell)
            if division_factor == 0:
                division_factor = 1
            cells.append(((cell[0]+x, cell[1]+y), division_factor))

    # EMPTY = 0
    # SNAKE = 1
    # FOOD = 2
    # SPOILED = 3
    own_snake = board.get_snake(board.own_snake_id)
    cell_weightings = [EMPTY_RATING, ENEMY_RATING, FOOD_RATING, SPOILED_RATING, BODY_RATING, OUT_SIDE_BOARD_RATING]
    cell_values = []

    for m_cell in cells:
        weight_key = 5  # Outside the board
        if board.inside(m_cell[0]):
            weight_key = board.get_cell(m_cell[0])
            if m_cell[0] in own_snake.coords:
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


def _touching_flood(flood, pos):
    for point in flood:
        if touching(pos, point):
            return True
    return False


def find_safest_positions(snake, board, bad_positions):
    """
    finds a position in a binary-search like fashion, this could probably just
    linearly scan the whole board, rating every position, and then returning the highest n
    positions
    """
    # account for bad_positions
    temp_board = Board(clone=board)
    for pos in bad_positions:
        temp_board.set_cell(pos, SNAKE)

    # Setup bounds and modulous
    bounds = [(0, 0), (board.width-1, board.height-1)]
    skip_cell_modulous = 1 if (board.width*board.height) <= ENABLE_CHECKERBOARD_SIZE else 2
    checkerboard_count = 0

    # Create a checkerboard of positions to check
    potential_cells = []
    for x in range(bounds[0][0], bounds[1][0]+1):
        for y in range(bounds[0][1], bounds[1][1]+1):
            if board.get_cell((x, y)) in [SNAKE, FOOD, SPOILED]:
                continue
            if (x, y) in bad_positions:
                continue

            flood = flood_fill(temp_board, (x, y))
            if len(flood) <= snake.attributes['length'] * SAFE_SPACE_FACTOR and not _touching_flood(flood, snake.head):
                continue

            checkerboard_count += 1
            if (checkerboard_count % skip_cell_modulous) != 0:
                continue
            potential_cells.append(((x, y), _rate_cell((x, y), temp_board)))
        checkerboard_count += 1

    results = sorted(potential_cells, key=lambda x: x[1], reverse=True)
    return results[:5]


def rate_food(current_position, board, board_food):
    """ finds and rates food positions """
    rated_food = [(food, _rate_cell(food, board)) for food in board_food]
    return sorted(rated_food, key=lambda x: x[1], reverse=True)


def bfs(starting_position, target_position, board, exclude, return_list, include_start=False):
    """
    BFS implementation to search for path to food

    :param starting_position: starting position
    :param target_position: target position
    :param board: the board state

    example:

    bfs((0,0), (2,2), board) -> [(0,0), (0,1), (0,2), (1,2), (2,2)]
    """
    def _get_path_from_nodes(node, include_start):
        path = []
        while(node):
            path.insert(0, (node[0], node[1]))  # Reverse
            node = node[2]
        if include_start:
            return return_list.append(path)
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
            return _get_path_from_nodes(node, include_start)  # Rebuild path

        if (board_copy.get_cell((x, y)) == SPOILED or board_copy.get_cell((x, y)) == SNAKE) and not (x, y) == starting_position:
            continue

        board_copy.set_cell((x, y), SPOILED)  # Mark as explored

        for i in neighbours(node):
            if board_copy.inside((i[0], i[1])):
                queue.append((i[0], i[1], node))

    return None  # No path


def longest_path(starting_position, target_position, board, exclude):
    """ Gets the longest path between two points - can be very slow if given a large enough area """
    def _expand_rating(start, end, board_copy):
        if start == end:
            return board_copy

        not_needed = []
        for point in neighbours(start):
            if board_copy.outside(point) or board_copy.get_cell(point) == SNAKE or board_copy.get_cell_meta(point) is not None or point == end:
                not_needed.append(point)
                continue

            dist = board_copy.get_cell_meta(start) + 1
            board_copy.set_cell_meta(point, dist)

        for point in neighbours(start):
            if point in not_needed:
                continue

            board_copy = _expand_rating(point, end, board_copy)

        return board_copy

    def _create_path(start, end, board, path):
        if start == end:
            total = 0
            for point in path[1:]:
                total += board.get_cell_meta(point)
            return (path[1:], total)

        highest = None
        for point in neighbours(start):
            if point in path or board_copy.outside(point) or board_copy.get_cell(point) == SNAKE or board_copy.get_cell_meta(point) is None:
                continue

            path.append(point)
            value = _create_path(point, end, board, path)
            path.remove(point)

            if value and (not highest or value[1] > highest[1]):
                highest = value

        return highest

    board_copy = Board(clone=board)
    board_copy.set_cell(starting_position, EMPTY)

    for excluded_point in exclude:
        board_copy.set_cell(excluded_point, SNAKE)
    board_copy.set_cell_meta(target_position, 0)

    rated_board = _expand_rating(target_position, starting_position, board_copy)
    return _create_path(starting_position, target_position, rated_board, [starting_position])[0]
