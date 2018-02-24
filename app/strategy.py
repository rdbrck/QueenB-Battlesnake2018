from .utils import dist, neighbours, sub, get_directions, get_next_from_direction
from .constants import FOOD_CLOSE_HEALTH, FOOD_CLOSE_DIST, FOOD_MEDIUM_HEALTH, FOOD_MEDIUM_DIST, FOOD_HUNGRY_HEALTH, SPOILED, SNAKE,\
                       FOOD_RATING, ENEMY_RATING, BODY_RATING, EMPTY_RATING, SPOILED_RATING, FOOD_DANGEROUS_HEALTH, FOOD_DANGEROUS_DIST, FOOD_STEAL_DIST

import random


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


def need_food(board, bad_positions, snake):
    """ Determines if we need food and returns potential food that we can get """
    potential_food = []

    # food that is not contested (we are the closest)
    safe_food = [fud for fud in board.food if board.get_cell(fud) != SPOILED]

    # always go for safe food even if we kind of need it
    for food in safe_food:
        if dist(food, snake.head) >= snake.attributes['health']:
            continue

        # check if enemy is approaching food we are close to
        steal = False
        for enemy in board.snakes:
            if enemy.attributes['id'] != snake.attributes['id'] and dist(enemy.head, food) <= FOOD_STEAL_DIST:
                steal = True
                break

        # prioritize safe food if it's close and we are a little hungry otherwise wait a little bit
        if dist(food, snake.head) <= FOOD_CLOSE_DIST and (snake.attributes['health'] <= FOOD_CLOSE_HEALTH or steal):
            potential_food.append(food)
        elif dist(food, snake.head) <= FOOD_MEDIUM_DIST and snake.attributes['health'] <= FOOD_MEDIUM_HEALTH:
            potential_food.append(food)
        elif snake.attributes['health'] < FOOD_HUNGRY_HEALTH:
            potential_food.append(food)

    # if there is no safe food and we are relatively hungry then go for contested food
    if len(potential_food) < 1 and snake.attributes['health'] < FOOD_HUNGRY_HEALTH:
        contested_food = [fud for fud in board.food if board.get_cell(fud) == SPOILED]

        # if we are in possible distance of getting it then add it
        for food in contested_food:
            if dist(food, snake.head) <= snake.attributes['health']:
                potential_food.append(food)

    # remove food that puts us in a bad_position
    food_to_get = []
    for fud in potential_food:
        # if we are really low on health or the food is not super close then add it
        if snake.attributes['health'] < FOOD_DANGEROUS_HEALTH or dist(snake.head, fud) > FOOD_DANGEROUS_DIST:
            food_to_get.append(fud)
            continue

        # for each direction that would make sense for the shortest path verify the next move doesn't put us in a bad position
        for direction in get_directions(snake.head, fud):
            next_pos = get_next_from_direction(snake.head, direction)
            if next_pos not in bad_positions and board.inside(next_pos) and board.get_cell(next_pos) != SNAKE:
                food_to_get.append(fud)
                break

    return (food_to_get if len(food_to_get) > 0 else None)


def _touching_body(snake_a, snake_b):
    """ tests if snake_a is touching body of snake_b """
    for pos in neighbours(snake_a.head):
        if pos in snake_b.body:
            return True
    return False


def _same_direction(snake_a, snake_b):
    """ returns true when two snakes last move were the same (pointing in same direction) """
    return sub(snake_a.coords[0], snake_a.coords[1]) == sub(snake_b.coords[0], snake_b.coords[1])


def check_attack(board, bad_positions, snake):
    """ Determines if we have the opportunity to attack - doesn't seek out attacking but will attack given the opportunity """
    possible_attacks = []
    enemy_snakes = [enemy for enemy in board.snakes if enemy.attributes['id'] != snake.attributes['id']]

    # attack potential position that enemy would move into unless we are tailing their head
    for enemy in enemy_snakes:
        possible_attacks.extend([
            position for position in enemy.potential_positions() if board.inside(position)
            and not (_touching_body(snake, enemy) and _same_direction(snake, enemy)) and position in neighbours(snake.head)
        ])

    # remove dups from extending logic
    possible_attacks = list(set(possible_attacks))

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

    # remove possible attack moves if they have been deamed 'bad' as part of previous logic
    for pos in bad_positions:
        if pos in possible_attacks:
            possible_attacks.remove(pos)

    return (possible_attacks[0] if len(possible_attacks) > 0 else None)
