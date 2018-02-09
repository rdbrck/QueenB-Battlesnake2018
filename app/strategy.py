from .utils import dist, neighbours, sub
from .constants import FOOD_CLOSE_HEALTH, FOOD_CLOSE_DIST, FOOD_MEDIUM_HEALTH, FOOD_MEDIUM_DIST, FOOD_HUNGRY_HEALTH, FOOD_HEALTH_IGNORE, SPOILED


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
            for x in range(1, abs(enemy.head[0] - snake.head[0])):  # loop through whole body but not head
                position = (enemy.head[0] + direction[0] * x, enemy.head[1])  # find next path in tunnel

                # if enemy snake is not in a tunnel for the paths leading up to our head then ignore snake
                if board.vacant((position[0], position[1] + 1)) or board.vacant((position[0], position[1] - 1)):
                    break

                # if it's a tunnel the whole way it's possible that we can kill it if it's a safe move
                if x == abs(enemy.head[0] - snake.head[0]) - 1:
                    possible_attacks.append((snake.head[0], enemy.head[1]))

        elif enemy.head[0] in [snake.head[0] - 1, snake.head[0] + 1]:  # moving in the y plane and our head is one column off
            for x in range(1, abs(enemy.head[1] - snake.head[1])):  # loop through whole body but not head
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
