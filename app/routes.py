from constants import TAUNTS, SNAKE_NAME, PING, DIR_NAMES, DIR_VECTORS
from entities import Snake, Board
from strategy import general_direction, need_food
from utils import timing, get_direction, add, neighbours
from algorithms import bfs, find_safest_position, find_food, flood_fill
from threading import Thread

import random
import bottle
import json
import os

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.route('/')
@bottle.post('/start')
def start():
    # port = bottle.request.get_header('port')
    port = os.getenv('PORT', '8080')

    port_colors = {
        '8080': '#f00000',
        '8081': '#ff0000',
        '8082': '#fff000',
        '8083': '#ffff00',
        '8084': '#fffff0',
        '8085': '#ffffff',
        '8086': '#f0f0f0',
        '8087': '#0f0f0f'
    }

    try:
        color = port_colors[str(port)]
    except:
        color = "#123456"

    return {
        'color': '#ff0000',
        'taunt': random.choice(TAUNTS),
        'head_url': ('http://%s/static/uneil.gif' % bottle.request.get_header('host')),
        'name': 'BETTER THAN ALEKSIY\'S SNAKE',
        'head_type': 'safe',
        'tail_type': 'freckled'
    }


@bottle.post('/move')
def move():
    data = {}
    time_remaining = [150] # leave 50ms for network
    position = None
    path = None
    next_move = list()
    thread_pool = list()
    potential_snake_positions = list()
    direction = None

    with timing("bottle", time_remaining):
        data = bottle.request.json

    try:
        with timing("data parsing", time_remaining):
            board = Board(**data)
            snake = board.get_snake(data['you'])
            direction = general_direction(board, snake.head, snake.attributes['health_points'])
            move = direction # fallback

        for enemy_snake in board.snakes:
            if enemy_snake.attributes['id'] != snake.attributes['id']: # and enemy_snake.attributes['health_points'] >= snake.attributes['health_points']:
                potential_snake_positions.extend([position for position in enemy_snake.potential_positions() if board.inside(position)])

        number_of_squares = list()
        # find number of empty squares in every direction.
        for cell in neighbours(snake.head):
            if board.inside(cell):
                count = len(flood_fill(board, cell, False))
                number_of_squares.append((cell, count))
                if count <= 10: potential_snake_positions.append(cell)

        if number_of_squares[0][1] <= 10 and number_of_squares[1][1] <= 10 and number_of_squares[2][1] <= 10 and number_of_squares[3][1] <= 10:
            largest = reduce(lambda carry, direction: carry if carry[1] > direction[1] else direction, number_of_squares, number_of_squares[0])
            potential_snake_positions.remove(largest[0])

        print potential_snake_positions

        with timing("need_food", time_remaining):
            food = need_food(board, snake.head, snake.attributes['health_points'])

        if food:
            #if snake.attributes['health_points'] < 30:
                #potential_snake_positions = []

            with timing("find_food", time_remaining):
                food_positions = find_food(snake.head, snake.attributes['health_points'], board, food)
                positions = [ position[0] for position in food_positions ]
                # positions = list(set([ position[0] for position in food_positions ]) - set(potential_snake_positions))
                print positions
                print [ board.get_cell(position) for position in positions ]

                for position in positions:
                    t = Thread(target=bfs(snake.head, position, board, potential_snake_positions, next_move))
                    t = Thread(target=bfs(snake.head, position, board, [], next_move))

                    thread_pool.append(t)

                for thread in thread_pool:
                    thread.start()
                    thread.join()

                next_move = filter(lambda path: not len(path) == 0, next_move)

                path = min(next_move, key=len)
                move = get_direction(snake.head, path[0])
        else:
            #with timing("flood_fill", time_remaining):
                # flood_fill(board.vacant, snake.head, True)
            with timing("find_safest_position", time_remaining):
                positions = find_safest_position(snake.head, direction, board)
                positions = [ position[0] for position in positions ]
                # positions = list(set([position[0] for position in positions]) - set(potential_snake_positions))
                print positions
                print [ board.get_cell(position) for position in positions ]

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
        print "WTF", e.message

    print next_move
    print path
    print move

    if len(next_move) == 0:
        print "CHANGING MOVE"
        with timing("floodfill", time_remaining):
            floods = {
                "up": len(flood_fill(board, (snake.head[0],snake.head[1]-1))),
                "down": len(flood_fill(board, (snake.head[0],snake.head[1]+1))),
                "right": len(flood_fill(board, (snake.head[0]+1,snake.head[1]))),
                "left": len(flood_fill(board, (snake.head[0]-1,snake.head[1])))
            }

            move = max(floods.iterkeys(), key=(lambda key: floods[key]))

    # don't be stupid
    m_move = add(snake.head, DIR_VECTORS[DIR_NAMES.index(move)])
    if board.inside(m_move) and board.get_cell(m_move) == 1:
        print "CHANGING MOVE"
        for direction in DIR_NAMES:
            m_move = add(snake.head, DIR_VECTORS[DIR_NAMES.index(direction)])
            if board.inside(m_move) and board.get_cell(m_move) != 1:
                move = direction

    print "moving", move
    return {
        'move': move,
        'taunt': random.choice(TAUNTS)
    }
