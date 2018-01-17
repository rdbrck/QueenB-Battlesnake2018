from utils import dist


def general_direction(board, head, health):
    """ Returns the most 'beneficial' direction to move in """

    # start with general area
    direction = {
        "up": 5000 / (dist(head, (head[0],0))+1),
        "down": 5000 / (dist(head, (head[0],board.height))+1),
        "right": 5000 / (dist((board.width,head[1]), head)+1),
        "left": 5000 / (dist((0,head[1]), head)+1)
    }

    # close to a border or snake?
    if not board.vacant((head[0]-1,head[1])):
        direction["left"] += 1000000

    if not board.vacant((head[0]+1,head[1])):
        direction["right"] += 1000000

    if not board.vacant((head[0],head[1]-1)):
        direction["up"] += 1000000

    if not board.vacant((head[0],head[1]+1)):
        direction["down"] += 1000000

    # snakes in area
    for snake in board.snakes:
        for pos in snake.coords:
            if pos == head: continue
            #right
            if pos[0] > head[0]:
                direction['right'] += 1000 / dist(pos, head)
            #left
            elif pos[0] < head[0]:
                direction['left'] += 1000 / dist(pos, head)
            #up
            if pos[1] < head[1]:
                direction['up'] += 1000 / dist(pos, head)
            #down
            elif pos[1] > head[1]:
                direction['down'] += 1000 / dist(pos, head)

    # food in area
    if health < 75:
        for pos in board.food:
            if board.get_cell(pos) == 3 and (health - dist(pos, head) > 20): continue
            #right
            if pos[0] > head[0]:
                direction['right'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)
            #left
            elif pos[0] < head[0]:
                direction['left'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)
            #up
            if pos[1] < head[1]:
                direction['up'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)
            #down
            elif pos[1] > head[1]:
                direction['down'] -= (10000 / ((health / 10) + 1)) / dist(pos, head)

    return min(direction.iterkeys(), key=(lambda key: direction[key]))


def need_food(board, head, health):
    food_to_get = []
    num_snakes = len(board.snakes)

    # if we really need food go for it even if it's not 'safe'
    if health < 50:
        for food in board.food:
            if (health + dist(head, food)) < 50:
                food_to_get.append(food)

    if len(food_to_get) > 0:
        return food_to_get

    # food that is considered 'safe'
    safe_food = [fud for fud in board.food if board.get_cell(fud) != 3]

    # always go for safe food even if we kind of need it
    for food in safe_food:
        # get food if it's close (more aggresive when more snakes on board)
        if dist(food, head) <= 2 and health < (((num_snakes + 1) * 7) + 15):
            food_to_get.append(food)
        # get food if we kind of need it
        elif health < 50:
            food_to_get.append(food)

    return (food_to_get if len(food_to_get) > 0 else None)
