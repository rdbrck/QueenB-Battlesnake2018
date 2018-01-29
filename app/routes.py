from .entities import Board
from .strategy import general_direction, need_food
from .utils import timing, get_direction, add, neighbours
from .algorithms import bfs, find_safest_position, find_food, flood_fill
from .constants import SNAKE_TAUNT, SNAKE_NAME, SNAKE_COLOR, SNAKE_HEAD, SNAKE_TAIL, SNAKE_IMAGE, DIR_NAMES, DIR_VECTORS

from functools import reduce
from threading import Thread
import bottle
import logging


logging.basicConfig()
logger = logging.getLogger(__name__)


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.route('/')
@bottle.post('/start')
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
def move():
    data = {}
    time_remaining = [150]  # leave 50ms for network
    next_move = list()
    thread_pool = list()
    potential_snake_positions = list()
    direction = None

    with timing("bottle", time_remaining):
        data = bottle.request.json

    try:
        # Get general direction and fallback move
        with timing("data parsing", time_remaining):
            board = Board(**data)
            snake = board.get_snake(data['you']['id'])
            direction = general_direction(board, snake.head, snake.attributes['health'])
            move = direction  # fallback
    except Exception as e:
        logger.error("Failure handling request - %s" % e.message)
        return {'move': 'up'}  # In this case we don't know what the board looks like so guess

    try:
        # Get spots that an enemy snake could move into - adding comment below would make snake more aggressive (needs testing)
        with timing("enemy snake heads", time_remaining):
            for enemy_snake in board.snakes:
                if enemy_snake.attributes['id'] != snake.attributes['id']:  # and enemy_snake.attributes['health'] >= snake.attributes['health']:
                    potential_snake_positions.extend([position for position in enemy_snake.potential_positions() if board.inside(position)])

        # Flood fill in each direction to find bad directions - could be modified to correlate to length of our snake (see <= 10)
        with timing("intial flood fill", time_remaining):
            number_of_squares = list()
            for cell in neighbours(snake.head):
                if board.inside(cell):
                    count = len(flood_fill(board, cell, False))
                    number_of_squares.append((cell, count))
                    if count <= 10:
                        potential_snake_positions.append(cell)

            # If all are bad go with the largest
            if number_of_squares[0][1] <= 10 and number_of_squares[1][1] <= 10 and number_of_squares[2][1] <= 10 and number_of_squares[3][1] <= 10:
                largest = reduce(lambda carry, direction: carry if carry[1] > direction[1] else direction, number_of_squares, number_of_squares[0])
                potential_snake_positions.remove(largest[0])

        # Check if we need food (or if there is any that we can reach)
        with timing("need_food", time_remaining):
            food = need_food(board, snake.head, snake.attributes['health'])

        # If we need food find a good path to said food
        if food:
            with timing("find_food", time_remaining):
                food_positions = find_food(snake.head, snake.attributes['health'], board, food)
                positions = [position[0] for position in food_positions]

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, potential_snake_positions, next_move))
                    t = Thread(target=bfs(snake.head, position, board, [], next_move))

                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                next_move = [path for path in next_move if not len(path) == 0]

                path = min(next_move, key=len)
                move = get_direction(snake.head, path[0])

        # If we don't need food then find a good path to a "good" position on the board
        else:
            with timing("find_safest_position", time_remaining):
                positions = find_safest_position(snake.head, direction, board)
                positions = [position[0] for position in positions]

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, potential_snake_positions, next_move))
                    t = Thread(target=bfs(snake.head, position, board, [], next_move))

                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                path = max(next_move, key=len)
                move = get_direction(snake.head, path[0])

    except Exception as e:
        logger.error("Code failure - %s" % e.message)

    # If code above failed then fallback to a floodfill move
    if len(next_move) == 0:
        logger.info("CHANGED MOVE - floodfill fallback.")
        with timing("floodfill fallback", time_remaining):
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

    return {
        'move': move  # 'up' | 'down' | 'left' | 'right'
    }
