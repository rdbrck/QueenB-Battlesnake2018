from .utils import dist, neighbours, translate_to_direction
from .constants import FOOD_CLOSE_HEALTH, FOOD_HUNGRY_HEALTH


def general_direction(board, head, health):
    """ Returns the most 'beneficial' direction to move in terms of board position """
    # start with general area
    direction = {
        "up": 5000 / (dist(head, (head[0], 0))+1),
        "down": 5000 / (dist(head, (head[0], board.height))+1),
        "right": 5000 / (dist((board.width, head[1]), head)+1),
        "left": 5000 / (dist((0, head[1]), head)+1)
    }

    # close to a border or snake?
    if not board.vacant((head[0]-1, head[1])):
        direction["left"] += 1000000

    if not board.vacant((head[0]+1, head[1])):
        direction["right"] += 1000000

    if not board.vacant((head[0], head[1]-1)):
        direction["up"] += 1000000

    if not board.vacant((head[0], head[1]+1)):
        direction["down"] += 1000000

    # snakes in area
    for snake in board.snakes:
        for pos in snake.coords:
            if pos == head:
                continue
            # right
            if pos[0] > head[0]:
                direction['right'] += 1000 / dist(pos, head)
            # left
            elif pos[0] < head[0]:
                direction['left'] += 1000 / dist(pos, head)
            # up
            if pos[1] < head[1]:
                direction['up'] += 1000 / dist(pos, head)
            # down
            elif pos[1] > head[1]:
                direction['down'] += 1000 / dist(pos, head)

    # food in area
    if health < 75:
        for pos in board.food:
            if board.get_cell(pos) == 3 and (health - dist(pos, head) > 20):
                continue
            # right
            if pos[0] > head[0]:
                direction['right'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)
            # left
            elif pos[0] < head[0]:
                direction['left'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)
            # up
            if pos[1] < head[1]:
                direction['up'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)
            # down
            elif pos[1] > head[1]:
                direction['down'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)

    return min(iter(direction.keys()), key=(lambda key: direction[key]))


def need_food(board, bad_positions, snake):
    """ Determines if we need food and returns potential food that we can get """
    food_to_get = []

    # food that is not contested (we are the closest)
    safe_food = [fud for fud in board.food if board.get_cell(fud) != 3]

    # always go for safe food even if we kind of need it
    for food in safe_food:
        # prioritize safe food if it's close and we are a little hungry otherwise wait a little bit
        if dist(food, snake.head) <= 2 and snake.attributes['health'] < FOOD_CLOSE_HEALTH:
            food_to_get.append(food)
        elif dist(food, snake.head) <= snake.attributes['health'] and snake.attributes['health'] < FOOD_HUNGRY_HEALTH:
            food_to_get.append(food)

    # if there is no safe food and we are relatively hungry then move toward contested food
    if len(food_to_get) == 0 and snake.attributes['health'] < FOOD_HUNGRY_HEALTH:
        contested_food = [fud for fud in board.food if board.get_cell(fud) == 3]

        # If it's contested but not going to get immediately taken and we are in possible distance of getting it then move one step closer
        for food in contested_food:
            if dist(food, snake.head) <= snake.attributes['health'] and food not in bad_positions:
                food_to_get.append(food)                

    return (food_to_get if len(food_to_get) > 0 else None)


def _touching_snake(enemy, snake):
    """ tests if the enemy snake is touching our tail """
    for pos in neighbours(enemy.head):
        if pos in snake.tail:
            return True
    return False


def _same_direction(enemy, snake):
    """ returns true when a two snakes last move were the same (pointing in same direction) """
    return translate_to_direction(enemy.coords[0], enemy.coords[1]) == translate_to_direction(snake.coords[0], snake.coords[1])


def _sandwiched(board, enemy):
    """ return true if snake is sandwiched in either x or y plane """
    sandwiched_column = (not board.vacant(enemy.head[0]-1, enemy.head[1]) and not board.vacant(enemy.head[0]+1, enemy.head[1]))
    sandwiched_row = (not board.vacant(enemy.head[0], enemy.head[1]-1) and not board.vacant(enemy.head[0], enemy.head[1]+1))

    return sandwiched_row != sandwiched_column:


def check_attack(board, potential_snake_positions, bad_positions, snake):
    """ Determines if we have the opportunity to attack - doesn't seek out attacking but will attack given the opportunity """
    possible_attacks = []
    enemy_snakes = [enemy for enemy in board.snakes if enemy.attributes['id'] != snake.attributes['id']]

    # add potential attack positions where a snake with less health might move into
    for pos in neighbours(snake.head):
        if pos in potential_snake_positions and pos not in bad_positions:
            possible_attacks.append(pos)

    # add potential attack positions where enemy snake is between us and a wall or another snake
    for enemy in enemy_snakes:
        # filters that must pass for us to perform this attack
        if not _touching_snake(enemy, snake) or not _sandwiched(board, enemy) or not _same_direction(enemy, snake):
            continue




    # remove possible attack spots where the enemy snake is equal in size or bigger
    for enemy in enemy_snakes:
        enemy_neighbours = neighbours(enemy.head)
        for neighbour in enemy_neighbours:
            if neighbour in possible_attacks and enemy.attributes['length'] >= snake.attributes['length']:
                possible_attacks.remove(neighbour)

    return (possible_attacks[0] if len(possible_attacks) > 0 else None)
