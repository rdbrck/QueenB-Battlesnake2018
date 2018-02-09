from .utils import dist, neighbours, sub
from .constants import FOOD_CLOSE_HEALTH, FOOD_CLOSE_DIST, FOOD_MEDIUM_HEALTH, FOOD_MEDIUM_DIST, FOOD_HUNGRY_HEALTH, FOOD_HEALTH_IGNORE, SPOILED, SNAKE,\
                       FOOD_RATING, ENEMY_RATING, BODY_RATING, EMPTY_RATING, SPOILED_RATING


def _add_count_directions(directions, index, pos, head):
    if pos[0] > head[0]:
        directions['right'][index] += 1
    elif pos[0] < head[0]:
        directions['left'][index] += 1
    if pos[1] < head[1]:
        directions['up'][index] += 1
    elif pos[1] > head[1]:
        directions['down'][index] += 1

    return directions


def general_direction(board, snake, bad_positions):
    """ Returns the most 'beneficial' general direction to move in terms of board position """
    directions = {
        "up": {
            'food': 0,
            'enemy': 0,
            'body': 0,
            'spoiled': 0,
            'area': board.width * (snake.head[1] - 1)
        },
        "down": {
            'food': 0,
            'enemy': 0,
            'body': 0,
            'spoiled': 0,
            'area': board.width * (board.height - (snake.head[1] + 1))
        },
        "left": {
            'food': 0,
            'enemy': 0,
            'body': 0,
            'spoiled': 0,
            'area': board.height * (snake.head[0] - 1)
        },
        "right": {
            'food': 0,
            'enemy': 0,
            'body': 0,
            'spoiled': 0,
            'area': board.height * (board.width - (snake.head[0] + 1))
        }     
    }

    # set bad positions as bad
    for pos in bad_positions:
        if pos in snake.body:
            continue

        directions = _add_count_directions(directions, 'enemy', pos, snake.head)

    # set snakes as bad and self as okay
    for enemy in board.snakes:
        index = 'body'
        if enemy.attributes['id'] != snake.attributes['id']:
            index = 'enemy'

        directions = _add_count_directions(directions, index, pos, snake.head)

    # set food as good
    for fud in board.food:
        index = 'food'
        if board.get_cell(pos) == SPOILED:
            index = 'spoiled'

        directions = _add_count_directions(directions, index, pos, snake.head)

    # find best general direction
    best_direction = None
    for direction, stats in directions.items():
        if stats['area'] < 1:
            continue

        empty_cells = stats['area'] - stats['food'] - stats['spoiled'] - stats['body'] - stats['enemy']
        average_cell_rating = (stats['food'] * FOOD_RATING + stats['spoiled'] * SPOILED_RATING + stats['body'] * BODY_RATING
                                + stats['enemy'] * ENEMY_RATING + empty_cells * EMPTY_RATING) / stats['area']

        if (best_direction and average_cell_rating > best_direction[1]) or not best_direction:
            best_direction = (direction, average_cell_rating)
        elif best_direction and average_cell_rating == best_direction[1] and directions[best_direction[0]]['area'] < stats['area']:
            best_direction = (direction, average_cell_rating)

    return best_direction[0]


def need_food(board, bad_positions, snake):
    """ Determines if we need food and returns potential food that we can get """
    food_to_get = []

    if snake.attributes['health'] >= FOOD_HEALTH_IGNORE:
        return None

    # food that is not contested (we are the closest)
    safe_food = [fud for fud in board.food if board.get_cell(fud) != SPOILED]

    # always go for safe food even if we kind of need it
    for food in safe_food:
        # prioritize safe food if it's close and we are a little hungry otherwise wait a little bit
        if dist(food, snake.head) <= FOOD_CLOSE_DIST and snake.attributes['health'] >= FOOD_CLOSE_HEALTH:
            food_to_get.append(food)
        elif dist(food, snake.head) <= FOOD_MEDIUM_DIST and snake.attributes['health'] >= FOOD_MEDIUM_HEALTH:
            food_to_get.append(food)
        elif dist(food, snake.head) <= snake.attributes['health'] and snake.attributes['health'] < FOOD_HUNGRY_HEALTH:
            food_to_get.append(food)

    # if there is no safe food and we are relatively hungry then move toward contested food
    if len(food_to_get) == 0 and snake.attributes['health'] < FOOD_HUNGRY_HEALTH:
        contested_food = [fud for fud in board.food if board.get_cell(fud) == SPOILED]

        # If it's contested but not going to get immediately taken and we are in possible distance of getting it then move one step closer
        for food in contested_food:
            if dist(food, snake.head) <= snake.attributes['health'] and food not in bad_positions:
                food_to_get.append(food)                

    return (food_to_get if len(food_to_get) > 0 else None)


def _touching_body(enemy, snake):
    """ tests if the enemy snake is touching our body """
    for pos in neighbours(enemy.head):
        if pos in snake.body:
            return True
    return False


def _same_direction(enemy, snake):
    """ returns true when a two snakes last move were the same (pointing in same direction) """
    return sub(enemy.coords[0], enemy.coords[1]) == sub(snake.coords[0], snake.coords[1])


def check_attack(board, potential_snake_positions, bad_positions, snake):
    """ Determines if we have the opportunity to attack - doesn't seek out attacking but will attack given the opportunity """
    possible_attacks = []
    enemy_snakes = [enemy for enemy in board.snakes if enemy.attributes['id'] != snake.attributes['id']]

    # add potential attack positions where a snake with less health might move into
    for pos in neighbours(snake.head):
        if pos in potential_snake_positions:
            possible_attacks.append(pos)

    # add potential attack positions where enemy snake is between us and a wall or another snake
    for enemy in enemy_snakes:
        # although generic, we can ignore snakes that don't pass these
        if not _touching_body(enemy, snake) or not _same_direction(enemy, snake):
            continue

        direction = sub(enemy.coords[0], enemy.coords[1])
        if direction[0] != 0 and enemy.head[1] in [snake.head[1] - 1, snake.head[1] + 1]:  # moving in the x plane and our head is one row off
            for x in range(1, abs(enemy.head[0] - snake.head[0])): # loop through whole body but not head
                position = (enemy.head[0] + direction[0] * x, enemy.head[1])  # find next path in tunnel

                # if enemy snake is not in a tunnel for the paths leading up to our head then ignore snake
                if board.vacant((position[0], position[1] + 1)) or board.vacant((position[0], position[1] - 1)):
                    break

                # if it's a tunnel the whole way it's possible that we can kill it if it's a safe move
                if x == abs(enemy.head[0] - snake.head[0]) - 1:
                    possible_attacks.append((snake.head[0], enemy.head[1]))

        elif enemy.head[0] in [snake.head[0] - 1, snake.head[0] + 1]:  # moving in the y plane and our head is one column off
            for x in range(1, abs(enemy.head[1] - snake.head[1])): # loop through whole body but not head
                position = (enemy.head[0], enemy.head[1] + direction[1] * x)  # find next path in tunnel

                # if enemy snake is not in a tunnel for the paths leading up to our head then ignore snake
                if board.vacant((position[0] + 1, position[1])) or board.vacant((position[0] - 1, position[1])):
                    break

                # if it's a tunnel the whole way it's possible that we can kill it if it's a safe move
                if x == abs(enemy.head[1] - snake.head[1]) - 1:
                    possible_attacks.append((enemy.head[0], snake.head[1]))

    # remove possible attack spots where the enemy snake is equal in size or bigger
    for enemy in enemy_snakes:
        for neighbour in neighbours(enemy.head):
            if neighbour in possible_attacks and enemy.attributes['length'] >= snake.attributes['length']:
                possible_attacks.remove(neighbour)

    # remove possible attack moves if they have been deamed 'bad' as aprt of previous logic
    for pos in bad_positions:
        if pos in possible_attacks:
            possible_attacks.remove(pos)

    return (possible_attacks[0] if len(possible_attacks) > 0 else None)
