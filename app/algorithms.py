from .utils import neighbours, surrounding, sub, dist, touching, next_to_wall, available_next_positions
from .entities import Board
from .constants import DIR_NAMES, DIR_VECTORS, SNAKE, EMPTY, FOOD, SPOILED, SAFE_SPACE_FACTOR,\
                       FOOD_RATING, SPOILED_RATING, EMPTY_RATING, BODY_RATING, ENEMY_RATING, OUT_SIDE_BOARD_RATING

import time
import random
from functools import reduce
from math import floor
from copy import deepcopy
from collections import deque


def rate_cell(cell, board, snake, bloom_level=4):
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
    cell_weightings = [EMPTY_RATING, ENEMY_RATING, FOOD_RATING, SPOILED_RATING, BODY_RATING, OUT_SIDE_BOARD_RATING]
    cell_values = []

    for m_cell in cells:
        weight_key = 5  # Outside the board
        if board.inside(m_cell[0]):
            weight_key = board.get_cell(m_cell[0])
            if m_cell[0] in snake.coords:
                weight_key = 4
        cell_values.append((weight_key, m_cell[1]))

    return reduce(lambda carry, m_cell: carry + cell_weightings[m_cell[0]]/m_cell[1], cell_values, 0)


def flood_fill(board, start_pos, allow_start_in_occupied_cell=False, max_size=None):
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
        if max_size and len(visited) > max_size:
            break

    return visited


def _touching_flood(flood, pos):
    for point in flood:
        if touching(pos, point):
            return True
    return False


def find_safest_positions(snake, board, bad_positions):
    # account for bad_positions
    temp_board = Board(clone=board)
    for pos in bad_positions:
        temp_board.set_cell(pos, SNAKE)

    # Create a checkerboard of positions to check
    potential_cells = []
    for x in range(0, board.width):
        for y in range(0, board.height):
            if temp_board.get_cell((x, y)) in [SNAKE, FOOD, SPOILED]:
                continue

            safe_area_size = snake.attributes['length'] * SAFE_SPACE_FACTOR
            flood = flood_fill(temp_board, (x, y), max_size=safe_area_size)
            if len(flood) <= safe_area_size and not _touching_flood(flood, snake.head):
                continue

            potential_cells.append(((x, y), rate_cell((x, y), temp_board, snake)))

    results = sorted(potential_cells, key=lambda x: x[1], reverse=True)
    return results[:5]


def rate_food(snake, board, board_food):
    """ finds and rates food positions """
    rated_food = [(food, rate_cell(food, board, snake)) for food in board_food]
    return sorted(rated_food, key=lambda x: x[1], reverse=True)


def bfs(starting_position, target_position, board, exclude, return_list, include_start=False, boxed=False):
    def _find_paths(starting_position, target_position, _fp_board):
        def _loop_through_queue(_ltq_queue):
            def _get_path_from_nodes(_gpfn_node):
                path = []
                while(_gpfn_node):
                    path.insert(0, (_gpfn_node[0], _gpfn_node[1]))
                    _gpfn_node = _gpfn_node[2]
                if not include_start:
                    path = path[1:]

                return_list.append(path)
                return True

            # ----- _loop_through_queue ----- #
            ltq_found_path = False
            while len(_ltq_queue) > 0:
                node = _ltq_queue.popleft()
                x = node[0]
                y = node[1]

                if (x, y) == target_position:  # If we reach target_position
                    ltq_found_path = True
                    _get_path_from_nodes(node)  # Rebuild path
                    continue

                if _fp_board.get_cell((x, y)) == SNAKE and not (x, y) == starting_position:
                    continue

                _fp_board.set_cell((x, y), SNAKE)  # Mark as explored

                for i in neighbours(node):
                    if _fp_board.inside((i[0], i[1])):
                        _ltq_queue.append((i[0], i[1], node))
            return ltq_found_path

        # ----- _find_paths ----- #
        fp_found_path = False
        # First try and find a path to the target that immidiatly leads us away from the wall
        if next_to_wall(starting_position, board):
            queue = deque([])
            for i in neighbours(starting_position):
                if board.inside(i) and not next_to_wall(i, board):
                    queue.append((i[0], i[1], (starting_position[0], starting_position[1], None)))
            fp_found_path = _loop_through_queue(queue)

        if not found_path:
            queue = deque([(starting_position[0], starting_position[1], None)])
            fp_found_path = _loop_through_queue(queue)

        return fp_found_path  # No path

    # ----- bfs ----- #
    found_path = False
    board_copy = Board(clone=board)

    if not next_to_wall(starting_position, board_copy) and not next_to_wall(target_position, board_copy) and not boxed:
        # We want to avoid going along the wall if possible. Make new board that excludes the outside
        small_board = Board(clone=board_copy)
        small_board.height = small_board.height - 1
        small_board.width = small_board.width - 1
        small_board.start_index = 1

        start_surround = surrounding(starting_position)

        # Try and allow going along small_board's wall if we can loop back around
        # due to having an escape route next to the normal board's wall
        for point in exclude:
            if small_board.outside(point):
                continue

            if not next_to_wall(point, small_board):
                small_board.set_cell(point, SNAKE)
                continue

            for surrounding_point in start_surround:
                # if point to exclude is one point away from our head then we may want to exclude it
                if point == surrounding_point:
                    # We have a one space gap between our head and the real game board wall. Only exclude this exclude point
                    # if the space between us and the real wall isn't empty. Otherwise we can still escape by looping back.
                    for neighbour_point in surrounding(point):
                        if next_to_wall(neighbour_point, board_copy) and (board_copy.get_cell(neighbour_point) == SNAKE or neighbour_point in exclude):
                            small_board.set_cell(point, SNAKE)
        found_path = _find_paths(starting_position, target_position, small_board)

    if not found_path:
        for point in exclude:
            board_copy.set_cell(point, SNAKE)
        _find_paths(starting_position, target_position, board_copy)
    return


def longest_path(starting_position, target_position, board, exclude):
    """ Gets the longest path between two points - can be very slow if given a large enough area (NP hard problem)"""
    def _create_path(start, end, board, path):
        if start == end:
            return (path[1:], len(path))

        highest = ([], 0)
        for point in neighbours(start):
            if point in path or board.outside(point) or board.get_cell(point) == SNAKE:
                continue

            path.append(point)
            value = _create_path(point, end, board, path)
            path.remove(point)

            if value and value[1] > highest[1]:
                highest = value

        return highest

    board_copy = Board(clone=board)
    board_copy.set_cell(starting_position, EMPTY)

    for excluded_point in exclude:
        board_copy.set_cell(excluded_point, SNAKE)

    return _create_path(starting_position, target_position, board_copy, [starting_position])[0]
