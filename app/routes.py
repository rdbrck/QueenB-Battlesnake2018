from .entities import Board
from .strategy import need_food, check_attack, detect_wall_tunnels
from .utils import timing, get_direction, add, neighbours, touching, food_in_box, available_next_positions
from .algorithms import bfs, find_safest_positions, rate_food, flood_fill, rate_cell, longest_path
from .constants import SNAKE_TAUNT, SNAKE_NAME, SNAKE_COLOR, SNAKE_HEAD, SNAKE_TAIL, SNAKE_IMAGE, DIR_NAMES, DIR_VECTORS, FOOD_BOXED_IN_HEALTH,\
                       SNAKE_SECONDARY_COLOR, DISABLE_ATTACKING, FOOD_HUNGRY_HEALTH, SAFE_SPACE_FACTOR, TAIL_PREFERENCE_FACTOR, LOG_LEVEL,\
                       SNAKE, FOOD, SPOILED, EMPTY

from threading import Thread
from copy import deepcopy
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
        # Get spots that an enemy snake could move into and also set snakes that are guaranteed to die as empty squares
        with timing("setup board and gather data", time_remaining):
            initial_floodfill_board = deepcopy(board)

            for enemy in board.enemies:
                enemy_options = available_next_positions(board, enemy)
                if (len(enemy_options) == 0 and snake.head not in neighbours(enemy.head)) or enemy.attributes['health'] == 0:
                    for pos in enemy.coords:
                        board.set_cell(pos, EMPTY)
                        initial_floodfill_board.set_cell(pos, EMPTY)
                    continue

                potential_snake_positions.extend(enemy_options)

                # floodfill in each direction with potential attack positions so we don't
                # do something dumb (predicts dead ends that can be seen next turn)
                for pos in enemy_options:
                    if pos not in neighbours(snake.head) or enemy.attributes['length'] >= snake.attributes['length']:
                        initial_floodfill_board.set_cell(pos, SNAKE)

        with timing("detect dangerous tunnels against walls (snake head at other end)", time_remaining):
            bad_positions.extend(detect_wall_tunnels(board))
            for pos in bad_positions:
                initial_floodfill_board.set_cell(pos, SNAKE)

        # Flood fill in each direction to find bad directions
        with timing("intial flood fill detection", time_remaining):
            number_of_squares = []
            boxed_in = False

            # Get size of space we can safely move into (should be larger than body size)
            safe_space_size = snake.attributes.get('length') * SAFE_SPACE_FACTOR
            for pos in available_next_positions(board, snake):
                if pos in bad_positions:
                    continue

                flooded_squares = flood_fill(initial_floodfill_board, pos, False)
                square_count = len(flooded_squares)
                number_of_squares.append([pos, square_count, any(x in neighbours(snake.head) for x in flooded_squares)])
                if square_count <= safe_space_size:
                    bad_positions.append(pos)

            # If all are bad don't set the largest as bad
            if all(pos[1] <= safe_space_size for pos in number_of_squares):
                boxed_in = True

                for square in number_of_squares:
                    # if tail present then scale region size by TAIL_PREFERENCE_FACTOR
                    if square[2]:
                        square[1] *= TAIL_PREFERENCE_FACTOR

                # go through each option and remove the largest from bad positions
                number_of_squares = sorted(number_of_squares, key=lambda x: x[1], reverse=True)
                for x in range(0, len(number_of_squares)):
                    # remove from bad_positions if it's the largest or has the same length as the largest
                    if number_of_squares[0][1] == number_of_squares[x][1]:
                        bad_positions.remove(number_of_squares[x][0])

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
            logger.info("ATTACKING")
            move = get_direction(snake.head, attack)

        # if we are boxed in, not attacking, and are in good health then we need to find an exit and max our movement
        if boxed_in and not move and (snake.attributes['health'] > FOOD_BOXED_IN_HEALTH or not food_in_box(flood_fill(board, snake.head, True), board)):
            logger.info("BOXED IN")
            with timing("boxed_in", time_remaining):
                # get the flooded squares of the inital floodfill board as that signifies boxed_in
                flooded_squares = flood_fill(initial_floodfill_board, snake.head, True)
                exit = None

                # loop through all snakes starting from tail and check if adjacent to flood choose closest that will be available by the time we get there
                for snek in board.snakes:
                    turns_until_space = 0
                    for piece in list(reversed(snek.body)):
                        turns_until_space += 1
                        for pos in flooded_squares:
                            if touching(pos, piece) and (exit is None or exit[1] > turns_until_space):
                                exit = (pos, turns_until_space)
                                break

                # if there isn't a good exit then we need to fallback
                if exit:
                    # if the area is more than a certain amount the longest path takes too long
                    if len(flooded_squares) > 20:
                        directions = []
                        thread_pool = []
                        next_move = []

                        for position in [v[0] for v in number_of_squares if v[1] > 0]:
                            if position in bad_positions:
                                continue

                            directions.append((position, get_direction(snake.head, position)))
                            t = Thread(target=bfs(position, exit[0], board, bad_positions, next_move, include_start=True, boxed=True))
                            thread_pool.append(t)

                        for thread in thread_pool:
                            thread.start()
                            thread.join()

                        next_move = [path for path in next_move if not len(path) == 0]

                        if len(next_move) > 0:
                            path = max([move for move in next_move], key=len)
                            move = get_direction(snake.head, path[0])
                    else:
                        path = longest_path(snake.head, exit[0], board, bad_positions)
                        if len(path) > 0:
                            move = get_direction(snake.head, path[0])

        # If we need food find a good path to said food (prioritized over attacking/boxed in when hungry)
        if food and not move:
            logger.info("FOOD")
            with timing("find_food", time_remaining):
                food_positions_ratings = rate_food(snake, board, food)
                thread_pool = []
                next_move = []

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
            logger.info("SAFEST")
            with timing("find_safest_positions", time_remaining):
                positions = find_safest_positions(snake, board, bad_positions)
                positions = [position[0] for position in positions]
                thread_pool = []
                next_move = []

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, bad_positions, next_move))
                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                if len(next_move) > 0:
                    # instead of max or min choose path with the best rated average
                    path = max([(path, sum(rate_cell(point, board, snake) for point in path)/len(path)) for path in next_move], key=lambda x: x[1])[0]
                    move = get_direction(snake.head, path[0])

    except Exception as e:
        logger.error("Code failure - %s \n %s" % (str(e), str(traceback.format_exc())))

    try:
        # If code above failed then fallback to a floodfill style move
        if not move:
            logger.info("FALLBACK")
            with timing("floodfill fallback", time_remaining):
                temp_board = deepcopy(board)
                for pos in potential_snake_positions:
                    temp_board.set_cell(pos, SNAKE)

                # try flood fill with bad positions and no worry tails included
                floods = {
                    "up": len(flood_fill(temp_board, (snake.head[0], snake.head[1]-1))),
                    "down": len(flood_fill(temp_board, (snake.head[0], snake.head[1]+1))),
                    "right": len(flood_fill(temp_board, (snake.head[0]+1, snake.head[1]))),
                    "left": len(flood_fill(temp_board, (snake.head[0]-1, snake.head[1])))
                }

                # less restrictive as it doesn't look at the potential next move off of food
                if all(direction == 0 for direction in floods.values()):
                    for pos in potential_snake_positions:
                        if board.get_cell(pos) == EMPTY:
                            temp_board.set_cell(pos, EMPTY)

                    floods = {
                        "up": len(flood_fill(temp_board, (snake.head[0], snake.head[1]-1))),
                        "down": len(flood_fill(temp_board, (snake.head[0], snake.head[1]+1))),
                        "right": len(flood_fill(temp_board, (snake.head[0]+1, snake.head[1]))),
                        "left": len(flood_fill(temp_board, (snake.head[0]-1, snake.head[1])))
                    }

                # less restrictive as it doesn't look at the potential next move on food
                if all(direction == 0 for direction in floods.values()):
                    for pos in potential_snake_positions:
                        if board.get_cell(pos) in [FOOD, SPOILED]:
                            temp_board.set_cell(pos, EMPTY)

                    floods = {
                        "up": len(flood_fill(temp_board, (snake.head[0], snake.head[1]-1))),
                        "down": len(flood_fill(temp_board, (snake.head[0], snake.head[1]+1))),
                        "right": len(flood_fill(temp_board, (snake.head[0]+1, snake.head[1]))),
                        "left": len(flood_fill(temp_board, (snake.head[0]-1, snake.head[1])))
                    }

                move = max(iter(floods.keys()), key=(lambda key: floods[key]))
    except Exception as e:
        logger.error("Fallback failure - %s \n %s" % (str(e), str(traceback.format_exc())))
        move = "up"  # Something is really messed up if this happens

    # Verify we didn't pick a bad move (wall or snake) - shouldn't happen but there if needed
    with timing("verify move", time_remaining):
        m_move = add(snake.head, DIR_VECTORS[DIR_NAMES.index(move)])
        if board.inside(m_move) and board.get_cell(m_move) == SNAKE:
            logger.info("CHANGED MOVE - verify fallback.")
            for direction in DIR_NAMES:
                m_move = add(snake.head, DIR_VECTORS[DIR_NAMES.index(direction)])
                if board.inside(m_move) and board.get_cell(m_move) != SNAKE:
                    move = direction
                    break

    return {
        'move': move,  # 'up' | 'down' | 'left' | 'right'
        'taunt': SNAKE_TAUNT
    }
