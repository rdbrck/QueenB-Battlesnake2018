from .entities import Board
from .strategy import need_food, check_attack
from .utils import timing, get_direction, add, neighbours, dist, touching
from .algorithms import bfs, find_safest_positions, rate_food, flood_fill
from .constants import SNAKE_TAUNT, SNAKE_NAME, SNAKE_COLOR, SNAKE_HEAD, SNAKE_TAIL, SNAKE_IMAGE, DIR_NAMES, DIR_VECTORS, FOOD_BOXED_IN_HEALTH,\
                       SNAKE_SECONDARY_COLOR, DISABLE_ATTACKING, FOOD_HUNGRY_HEALTH, SAFE_SPACE_FACTOR, TAIL_PREFERENCE_FACTOR, LOG_LEVEL

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
        with timing("intial flood fill detection", time_remaining):
            number_of_squares = []
            boxed_in = False

            # Get size of space we can safely move into (should be larger than body size)
            safe_space_size = snake.attributes.get('length') * SAFE_SPACE_FACTOR
            for cell in neighbours(snake.head):
                if board.inside(cell):
                    flooded_squares = flood_fill(board, cell, False)
                    tail_present = bool(set(neighbours(snake.tail)) & set(flooded_squares))
                    square_count = len(flooded_squares)
                    number_of_squares.append([cell, square_count, tail_present])
                    if square_count <= safe_space_size:
                        bad_positions.append(cell)

            # If all are bad don't set the largest as bad
            if set([cell[0] for cell in number_of_squares]).issubset(set(bad_positions)):
                for square in number_of_squares:
                    # if tail present then scale region size by TAIL_PREFERENCE_FACTOR
                    if square[2]:
                        square[1] *= TAIL_PREFERENCE_FACTOR

                number_of_squares = sorted(number_of_squares, key=lambda x: x[1], reverse=True)

                # go through each option and remove the largest from bad positions
                for x in range(0, len(number_of_squares)):
                    # remove from bad_positions if it's the largest or has the same length as the largest
                    if number_of_squares[0][1] == number_of_squares[x][1] and number_of_squares[x][0] not in snake.body:
                        bad_positions.remove(number_of_squares[x][0])

                # if there is atleast two none zero floodfills then check for box in
                if len([v for v in number_of_squares if v[1] > 0]) > 1:
                    boxed_in = True
                    # if all of the non zeros are the same and the rest are zero then we are boxed in
                    for value in [pos[1] for pos in number_of_squares]:
                        if value not in [number_of_squares[0][1], 0]:
                            boxed_in = False

        # Check if we have the opportunity to attack
        with timing("check_attack", time_remaining):
            attack = check_attack(board, bad_positions, snake)

        # combine and get rid of duplicates
        bad_positions = list(set(potential_snake_positions + bad_positions))

        # Check if we need food (or if there is any that we can reach)
        with timing("need_food", time_remaining):
            food = need_food(board, bad_positions, snake)

        # If we have the opportunity to attack and are not starving then attack
        if attack and not DISABLE_ATTACKING and (snake.attributes['health'] > FOOD_HUNGRY_HEALTH or not food):
            move = get_direction(snake.head, attack)

        # if we are boxed in, not attacking, and are in good health then we need to find an exit and max our movement
        if boxed_in and not move and (snake.attributes['health'] > FOOD_BOXED_IN_HEALTH or not food_in_box(flood_fill(board, snake.head, True), board)):
            with timing("boxed_in", time_remaining):
                # get the flooded squares
                flooded_squares = flood_fill(board, snake.head, True)
                exit = snake.tail

                # loop through snake starting from tail and check if adjacent to flood
                for piece in list(reversed(snake.body)):
                    for pos in flooded_squares:
                        if touching(pos, piece):
                            exit = pos
                            break
                    if exit != snake.tail:
                        break
                
                directions = []
                for position in [v[0] for v in number_of_squares if v[1] > 0]:
                    directions.append((position, get_direction(snake.head, position)))
                    t = Thread(target=bfs(position, exit, board, bad_positions, next_move, include_start=True))
                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                next_move = [path for path in next_move if not len(path) == 0]

                if len(next_move) > 0:
                    path = max([move for move in next_move], key=len)
                    move = get_direction(snake.head, path[0])

        # If we need food find a good path to said food (prioritized over attacking/boxed in when hungry)
        if food and not move:
            with timing("find_food", time_remaining):
                food_positions_ratings = rate_food(snake.head, board, food)
                thread_pool = []

                for position in [position[0] for position in food_positions_ratings]:
                    t = Thread(target=bfs(snake.head, position, board, bad_positions, next_move))
                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                next_move = [path for path in next_move if not len(path) == 0]

                if len(next_move) > 0:
                    food_moves = []

                    # verify if atleast one path returned had a positive rating
                    for move in next_move:
                        for pos in food_positions_ratings:
                            if pos[0] == move[-1]:
                                food_moves.append((move, pos[1]))

                    # if we have more than one option then figure out if we want to get rid of any poor ratings
                    if len(food_moves) > 1:
                        pos_moves = [move for move in food_moves if move[1] > 0]
                        food_moves = pos_moves if pos_moves else food_moves

                    path = min([move[0] for move in food_moves], key=len)
                    move = get_direction(snake.head, path[0])

        # If we don't need food, don't have the opportunity to attack, and are not boxed in then find a path to a "good" position on the board
        if not move:
            with timing("find_safest_positions", time_remaining):
                positions = find_safest_positions(snake, board, bad_positions)
                positions = [position[0] for position in positions]
                thread_pool = []

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, bad_positions, next_move))
                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                if len(next_move) > 0:  # if not then no good path so we need to do a fallback move
                    path = min(next_move, key=len)
                    move = get_direction(snake.head, path[0])

    except Exception as e:
        logger.error("Code failure - %s \n %s" % (str(e), str(traceback.format_exc())))

    try:
        # If code above failed then fallback to a floodfill style move
        if not move:
            logger.info("CHANGED MOVE - floodfill fallback.")
            # setup the board for fallback and verification
            with timing("setup fallback and verification board", time_remaining):
                for enemy in board.snakes:
                    if enemy.attributes['id'] != snake.attributes['id'] and (len(board.food) == 0 or enemy.closest_food(board.food)[1] != dist(enemy.tail, snake.head)):
                            board.set_cell(enemy.tail, 0)

            with timing("floodfill fallback", time_remaining):
                temp_board = Board(clone=board)
                for pos in potential_snake_positions:
                    temp_board.set_cell(pos, 1)

                # try flood fill with bad positions and no worry tails included
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
    except Exception as e:
        logger.error("Fallback failure - %s \n %s" % (str(e), str(traceback.format_exc())))
        move = "up"  # Something is really messed up if this happens

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
        'move': move,  # 'up' | 'down' | 'left' | 'right'
        'taunt': SNAKE_TAUNT
    }
