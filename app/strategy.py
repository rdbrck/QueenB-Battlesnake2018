from .utils import dist, neighbours, sub, add, get_directions, get_next_from_direction, next_to_wall, available_next_positions, touching
from .constants import FOOD_CLOSE_HEALTH, FOOD_CLOSE_DIST, FOOD_MEDIUM_HEALTH, FOOD_MEDIUM_DIST, FOOD_HUNGRY_HEALTH, SPOILED, SNAKE, DISABLE_STEALING,\
                       FOOD_DANGEROUS_HEALTH, FOOD_DANGEROUS_DIST, FOOD_STEAL_DIST, \
                       FOOD_HUNGRY_WALL_HEALTH


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
        for enemy in board.enemies:
            if dist(enemy.head, food) <= FOOD_MEDIUM_DIST + FOOD_STEAL_DIST:
                steal = True and not DISABLE_STEALING
                break

        # prioritize safe food if it's close and we are a little hungry otherwise wait a little bit
        if dist(food, snake.head) <= FOOD_CLOSE_DIST and (snake.attributes['health'] <= FOOD_CLOSE_HEALTH or steal):
            potential_food.append(food)
        elif dist(food, snake.head) <= FOOD_MEDIUM_DIST and (snake.attributes['health'] <= FOOD_MEDIUM_HEALTH or steal):
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

    if not potential_food:
        return None

    # get food that is not next to wall so we can potentially ignore food that is next to wall
    no_wall_food = []
    for fud in potential_food:
        if not next_to_wall(fud, board) or snake.attributes['health'] < FOOD_HUNGRY_WALL_HEALTH:
            no_wall_food.append(fud)

    if len(no_wall_food) == 0 and snake.attributes['health'] > FOOD_HUNGRY_WALL_HEALTH:
        return None

    # remove food that puts us in a bad_position
    food_to_get = []
    for fud in (potential_food if len(no_wall_food) == 0 else no_wall_food):
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
    available_moves = available_next_positions(board, snake)

    # attack potential position that enemy would move into unless we are tailing their head
    for enemy in board.enemies:
        possible_attacks.extend([
            pos for pos in available_next_positions(board, enemy) if pos in available_moves
            and not (_touching_body(snake, enemy) and _same_direction(snake, enemy))
        ])

    # remove dups from extending logic
    possible_attacks = list(set(possible_attacks))

    # add potential attack positions where enemy snake is between us and a wall or another snake
    for enemy in board.enemies:
        # although generic, we can ignore snakes that don't pass these
        if not _touching_body(enemy, snake) or not _same_direction(enemy, snake):
            continue

        direction = sub(enemy.coords[0], enemy.coords[1])
        if direction[0] != 0 and enemy.head[1] in [snake.head[1] - 1, snake.head[1] + 1]:  # moving in the x plane and our head is one row off
            head_distance = abs(enemy.head[0] - snake.head[0])
            for x in range(1, head_distance + 1):  # loop through whole body but not head
                position = (enemy.head[0] + direction[0] * x, enemy.head[1])  # find next path in tunnel

                # if enemy snake is not in a tunnel for the paths leading up to our head then ignore snake
                if board.vacant((position[0], position[1] + 1)) or board.vacant((position[0], position[1] - 1)):
                    break

                # if it's a tunnel the whole way it's possible that we can kill it if it's a safe move
                if x == head_distance - 1:
                    possible_attacks.append((snake.head[0], enemy.head[1]))
                elif x == head_distance and snake.attributes['health'] <= enemy.attributes['health']:
                    possible_attacks.append((snake.head[0] + direction[0], snake.head[1]))

        elif direction[1] != 0 and enemy.head[0] in [snake.head[0] - 1, snake.head[0] + 1]:  # moving in the y plane and our head is one column off
            head_distance = abs(enemy.head[1] - snake.head[1])
            for x in range(1, head_distance + 1):  # loop through whole body but not head
                position = (enemy.head[0], enemy.head[1] + direction[1] * x)  # find next path in tunnel

                # if enemy snake is not in a tunnel for the paths leading up to our head then ignore snake
                if board.vacant((position[0] + 1, position[1])) or board.vacant((position[0] - 1, position[1])):
                    break

                # if it's a tunnel the whole way it's possible that we can kill it if it's a safe move
                if x == head_distance - 1:
                    possible_attacks.append((enemy.head[0], snake.head[1]))
                elif x == head_distance and snake.attributes['health'] <= enemy.attributes['health']:
                    possible_attacks.append((snake.head[0], snake.head[1] + direction[1]))

    # remove possible attack spots where the enemy snake is equal in size or bigger
    for enemy in board.enemies:
        if enemy.attributes['length'] < snake.attributes['length']:
            continue

        for neighbour in neighbours(enemy.head):
            if neighbour in possible_attacks:
                possible_attacks.remove(neighbour)

    # remove possible attack moves if they have been deamed 'bad' as part of previous logic
    for pos in bad_positions:
        if pos in possible_attacks:
            possible_attacks.remove(pos)

    # I don't know why this would happen but we will add it anyways
    possible_attacks = [pos for pos in possible_attacks if board.inside(pos)]
    return (possible_attacks[0] if len(possible_attacks) > 0 else None)


def detect_wall_tunnels(board):
    tunnel_ends = []

    for enemy in board.enemies:
        # if the head of the enemy is not near a wall skip it
        if enemy.head[0] not in [1, board.width-2] and enemy.head[1] not in [1, board.height-2]:
            continue

        # if the enemy snake is not moving perpendicular to the wall skip it
        if abs(enemy.coords[1][0] - enemy.head[0]) != 1 and abs(enemy.coords[1][1] - enemy.head[1]) != 1:
            continue

        # get opposite of enemies last move (1, 0) (-1, 0) (0, 1) (0, -1)
        direction = sub(enemy.coords[1], enemy.coords[0])

        # get end of tunnel (by enemy head)
        if direction[0] == 0:
            end = (0 if enemy.head[0] == 1 else board.width-1, enemy.head[1])
        else:
            end = (enemy.head[0], 0 if enemy.head[1] == 1 else board.height-1)
 
        # starting from end apply opposite direction until not touching snake
        previous = None
        while any(touching(end, pos) for pos in enemy.coords) and board.inside(end) and board.get_cell(end) != SNAKE:
            previous = end
            end = add(end, direction)

        # if edge of board was reached ebfore finding end of tunnel then skip snake
        if board.outside(end) or board.get_cell(end) == SNAKE or not previous:
            continue

        tunnel_ends.append(previous)

    return tunnel_ends
