from .entities import Board
from .strategy import need_food, check_attack, general_direction
from .utils import timing, get_direction, add, neighbours, dist
from .algorithms import bfs, find_safest_position, find_food, flood_fill
from .constants import SNAKE_TAUNT, SNAKE_NAME, SNAKE_COLOR, SNAKE_HEAD, SNAKE_TAIL, SNAKE_IMAGE, DIR_NAMES, DIR_VECTORS,\
                       SNAKE_SECONDARY_COLOR, DISABLE_ATTACKING, FOOD_HUNGRY_HEALTH, SAFE_SPACE_FACTOR, LOG_LEVEL

from functools import reduce
from threading import Thread
import bottle
import logging
import traceback


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.route('/')
@bottle.post('/start')
@bottle.post('/start/')
def start():
    logger.info("GAME START")
    return {
        'color': SNAKE_COLOR,
        'secondary_color': SNAKE_SECONDARY_COLOR,
        'taunt': SNAKE_TAUNT,
        'head_url': ('http://%s/static/%s' % (bottle.request.get_header('host'), SNAKE_IMAGE)),
        'name': SNAKE_NAME,
        'head_type': SNAKE_HEAD,
        'tail_type': SNAKE_TAIL
    }


@bottle.post('/move')
@bottle.post('/move/')
def move():
    data = {}
    move = None
    time_remaining = [150]  # leave 50ms for network
    next_move = []
    thread_pool = []
    potential_snake_positions = []
    bad_positions = []

    with timing("bottle", time_remaining):
        data = bottle.request.json

    try:
        # Get general direction and fallback move
        with timing("data parsing", time_remaining):
            board = Board(**data)
            snake = board.get_snake(data['you']['id'])
    except Exception as e:
        logger.error("Failure handling request - %s" % str(e))
        return {'move': 'up'}  # In this case we don't know what the board looks like so guess

    try:
        # Get spots that an enemy snake could move into
        with timing("enemy snake heads", time_remaining):
            for enemy_snake in board.snakes:
                if enemy_snake.attributes['id'] != snake.attributes['id']:
                    potential_snake_positions.extend([position for position in enemy_snake.potential_positions() if board.inside(position)])

        # Flood fill in each direction to find bad directions
        with timing("intial flood fill", time_remaining):
            number_of_squares = []

            # Get size of space we can safely move into (should be larger than body size)
            safe_space_size = snake.attributes.get('length', 10) * SAFE_SPACE_FACTOR
            for cell in neighbours(snake.head):
                if board.inside(cell):
                    count = len(flood_fill(board, cell, False))
                    number_of_squares.append((cell, count))
                    if count <= safe_space_size:
                        bad_positions.append(cell)

            # If all are bad don't set the largest as bad
            if set([cell[0] for cell in number_of_squares]).issubset(set(bad_positions)):
                largest = reduce(lambda carry, direction: carry if carry[1] > direction[1] else direction, number_of_squares, number_of_squares[0])
                bad_positions.remove(largest[0])

        # Check if we have the opportunity to attack
        with timing("check_attack", time_remaining):
            attack = check_attack(board, potential_snake_positions, bad_positions, snake)

        bad_positions.extend(potential_snake_positions)
        # Check if we need food (or if there is any that we can reach)
        with timing("need_food", time_remaining):
            food = need_food(board, bad_positions, snake)

        # If we have the opportunity to attack and are not starving then attack
        if attack and not DISABLE_ATTACKING and (snake.attributes['health'] > FOOD_HUNGRY_HEALTH or not food):
            move = get_direction(snake.head, attack)

        # If we need food find a good path to said food (prioritize over attacking when hungry)
        elif food:
            with timing("find_food", time_remaining):
                food_positions = find_food(snake.head, snake.attributes['health'], board, food)
                positions = [position[0] for position in food_positions]
                thread_pool = []

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, bad_positions, next_move))
                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                next_move = [path for path in next_move if not len(path) == 0]

                if len(next_move) > 0:  # No good path so we need to do a fallback move
                    path = min(next_move, key=len)
                    move = get_direction(snake.head, path[0])

        # If we don't need food and don't have the opportunity to attack then find a path to a "good" position on the board
        if not move:
            with timing("find_safest_position", time_remaining):
                positions = find_safest_position(snake.head, general_direction(board, snake, bad_positions), board)
                positions = [position[0] for position in positions]
                thread_pool = []

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, bad_positions, next_move))
                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                if len(next_move) > 0:  # No good path so we need to do a fallback move
                    path = max(next_move, key=len)
                    move = get_direction(snake.head, path[0])

    except Exception as e:
        logger.error("Code failure - %s \n %s" % (str(e), str(traceback.format_exc())))

    # setup the board for fallback and verification
    with timing("setup fallback and verification board", time_remaining):
        for enemy in board.snakes:
            if enemy.attributes['id'] != snake.attributes['id'] and (len(board.food) == 0 or snake.closest_food(board.food)[1] > dist(snake.head, enemy.tail)):
                board.set_cell(enemy.tail, 0)

    # If code above failed then fallback to a floodfill style move
    if not move:
        logger.info("CHANGED MOVE - floodfill fallback.")
        with timing("floodfill fallback", time_remaining):
            temp_board = Board(clone=board)
            for pos in potential_snake_positions:
                temp_board.set_cell(pos, 1)

            # try flood fill with bad positionns and no worry tails included
            floods = {
                "up": len(flood_fill(temp_board, (snake.head[0], snake.head[1]-1))),
                "down": len(flood_fill(temp_board, (snake.head[0], snake.head[1]+1))),
                "right": len(flood_fill(temp_board, (snake.head[0]+1, snake.head[1]))),
                "left": len(flood_fill(temp_board, (snake.head[0]-1, snake.head[1])))
            }

            # less restrictive as it doesn't look at the potential next move
            if all(direction < snake.attributes['length'] for direction in floods.values()):
                floods = {
                    "up": len(flood_fill(board, (snake.head[0], snake.head[1]-1))),
                    "down": len(flood_fill(board, (snake.head[0], snake.head[1]+1))),
                    "right": len(flood_fill(board, (snake.head[0]+1, snake.head[1]))),
                    "left": len(flood_fill(board, (snake.head[0]-1, snake.head[1])))
                }

            move = max(iter(floods.keys()), key=(lambda key: floods[key]))

    # Verify we didn't pick a bad move (wall or snake) - shouldn't happen but there if needed
    with timing("verify move", time_remaining):
        m_move = add(snake.head, DIR_VECTORS[DIR_NAMES.index(move)])
        if board.inside(m_move) and board.get_cell(m_move) == 1:
            logger.info("CHANGED MOVE - verify fallback.")
            for direction in DIR_NAMES:
                m_move = add(snake.head, DIR_VECTORS[DIR_NAMES.index(direction)])
                if board.inside(m_move) and board.get_cell(m_move) != 1:
                    move = direction
                    break

    return {
        'move': move  # 'up' | 'down' | 'left' | 'right'
    }
