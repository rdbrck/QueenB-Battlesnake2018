import bottle
import os
import random
import heapq


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']

    return {
        'color': '#002800',
        'taunt': 'I am Groot!',
        'head_url': 'https://www.popsci.com/sites/popsci.com/files/styles/1000_1x_/public/images/2015/03/snake.jpg?itok=oi82kZXn',
        'name': 'Groot',
        'head_type' : 'shades',
        'tail_type' : 'round-bum'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    move = get_move(data)

    #Emergency move if move is None
    if (move is None):
        map = make_map(data, True)
        groot = get_groot(data)
        head = groot["body"]["data"][0]

        x = head["x"]
        y = head["y"]

        #Try and find safe move
        if y != 0 and map[y-1][x] == 0:
            if y != 1 and map[y-2][x] == 0:
                move = 'up'

        if y != (data["height"]-1) and map[y+1][x] == 0:
            if y != (data["height"]-2) and map[y+2][x] == 0:
                move = 'down'

        if x != 0 and map[y][x-1] == 0:
            if x != 1 and map[y][x-2] == 0:
                move = 'left'

        if x != (data["width"]-1) and map[y][x+1] == 0:
            if x != (data["width"]-2) and map[y][x+2] == 0:
                move = 'right'


        #Just find a move
        if (move == None):
            if y != 0 and map[y-1][x] == 0:
                move = 'up'

            if y != (data["height"]-1) and map[y+1][x] == 0:
                move = 'down'

            if x != 0 and map[y][x-1] == 0:
                move = 'left'

            if x != (data["width"]-1) and map[y][x+1] == 0:
                move = 'right'

    taunt = 'I am Gro'
    for x in range(data['turn'] % 8):
        taunt += 'o'
    taunt += 'ot!'
    return {
        'move': move
    }


def get_move(data):
    groot = get_groot(data)
    if groot["health"] < 60:
        return hungry(data)
    else:
        return default(data)


def get_groot(data):
    return data["you"]


def default(data):
    map = make_map(data, False)

    groot = get_groot(data)
    head = groot["body"]["data"][0]

    x = head["x"]
    y = head["y"]
    
    dangersLeft = 0
    dangersRight = 0
    dangersUp = 0
    dangersDown = 0

    if (len(groot["body"]["data"]) > 1):
        firstBody = groot["body"]["data"][1]
        xfirstBody = firstBody["x"]
        yfirstBody = firstBody["y"]
        
        if y - 1 == yfirstBody:
            dangersUp = 100

        if y + 1 == yfirstBody:
            dangersDown = 100

        if x - 1 == xfirstBody:
            dangersLeft = 100

        if x + 1 == xfirstBody:
            dangersRight = 100

    xtemp = x
    ytemp = y


    for i in range(1, 4):
        for j in range(-1, 2):
            xtemp = x - i
            ytemp = y - j

            if xtemp < 0 or xtemp > data["width"]-1 or ytemp < 0 or ytemp > data["height"]-1:
                dangersLeft += 0.5
            else:
                if map[ytemp][xtemp] != 0:
                    dangersLeft += map[ytemp][xtemp]

    for i in range(1, 4):
        for j in range(-1, 2):
            xtemp = x + i
            ytemp = y - j

            if xtemp < 0 or xtemp > data["width"]-1 or ytemp < 0 or ytemp > data["height"]-1:
                dangersRight += 0.5
            else:
                if map[ytemp][xtemp] != 0:
                    dangersRight += map[ytemp][xtemp]

    for i in range(-1, 2):
        for j in range(1, 4):
            xtemp = x - i
            ytemp = y - j

            if xtemp < 0 or xtemp > data["width"]-1 or ytemp < 0 or ytemp > data["height"]-1:
                dangersUp += 0.5
            else:
                if map[ytemp][xtemp] != 0:
                    dangersUp += map[ytemp][xtemp]

    for i in range(-1, 2):
        for j in range(1, 4):
            xtemp = x - i
            ytemp = y + j

            if xtemp < 0 or xtemp > data["width"]-1 or ytemp < 0 or ytemp > data["height"]-1:
                dangersDown += 0.5
            else:
                if map[ytemp][xtemp] != 0:
                    dangersDown += map[ytemp][xtemp]


    move = None

    upTuple = (dangersUp, 'up')
    downTuple = (dangersDown, 'down')
    leftTuple = (dangersLeft, 'left')
    rightTuple = (dangersRight, 'right')

    values = [upTuple, downTuple, rightTuple, leftTuple]

    sorted_by_first = sorted(values, key=lambda tup: tup[0])

    for option in sorted_by_first:
        if option[1] == 'up':
            if y == 0:
                continue

            ytemp = y - 1
            if (map[ytemp][x] >= 2):
                continue
            return 'up'

        if option[1] == 'down':
            if y == data["height"] - 1:
                continue

            ytemp = y + 1
            if (map[ytemp][x] >= 2):
                continue
            return 'down'

        if option[1] == 'left':
            if x == 0:
                continue

            xtemp = x - 1
            if (map[y][xtemp] >= 2):
                continue
            return 'left'

        if option[1] == 'right':
            if x == data["width"] - 1:
                continue

            xtemp = x + 1
            if (map[y][xtemp] >= 2):
                continue
            return 'right'

    return None


def hungry(data):

    groot = get_groot(data)
    map = make_map(data, True)

    if not len(data["food"]["data"]):
        return default(data)

    food = food_eval(map, data["food"]["data"], groot["body"]["data"][0])

    if not len(food):
        return default(data)

    return get_astar_move(groot["body"]["data"][0], food, data)


def food_eval(map, data_food, our_head):
        food_distance = []
        for food in data_food:
            food_distance.append(get_distance(our_head, food))
        sorted(food_distance)
        for food in food_distance:
            if(is_food_safe(food[1], 1, map)):
                return food[1]
        for food in food_distance:
            if(is_food_safe(food[1], 2, map)):
                return food[1]
        for food in food_distance:
            if(is_food_safe(food[1], 3, map)):
                return food[1]
        return []


def get_distance(our_head, food_coords):
    x_distance = abs(our_head["x"] - food_coords["x"])
    y_distance = abs(our_head["y"] - food_coords["y"])
    return [ x_distance + y_distance , food_coords]


def is_food_safe(food_coords, threshold, map):
    return map[food_coords["x"]][food_coords["y"]] <= threshold


def make_map(data, excludeFood):
    wall_coords = []
    map = []

    for y in range(data["height"]):
        row = []
        for j in range(data["width"]):
            row.append(0)
        map.append(row)


    for snake in data["snakes"]["data"]:
        head_counter = 0
        if snake["id"] == data["you"]["id"]:
            for body in snake["body"]["data"][1:]:
                wall_coords.append(body)
        else:
            for body in snake["body"]["data"]:
                if (head_counter == 0):
                    wall_coords.append(body)
                    wall_coords.append(body)
                    wall_coords.append(body)
                wall_coords.append(body)


    for wall in wall_coords:
        x = wall["x"]
        y = wall["y"]

        map[y][x] = 1
    
    if (not excludeFood):
        for food in data["food"]["data"]:
            wall_coords.append(food)

    for wall in wall_coords:
        x = wall["x"]
        y = wall["y"]

        map[y][x] += 1

    # Make edge scary
    for y in range(data["height"]):
        for x in range(data["width"]):
            if x == 0 or x == (data["width"]-1):
                map[y][x] += 0.5
            if y == 0 or y == (data["height"]-1):
                map[y][x] += 0.5

    return map


def get_astar_move(start, goal, data):
    start = (start["x"], start["y"])
    goal = (goal["x"], goal["y"])
    wall_coords     = []
    start           = tuple(start)
    goal            = tuple(goal)

    for snake in data["snakes"]["data"]:
        if snake["id"] == data["you"]["id"]:
            for body in snake["body"]["data"][1:]:
                wall_coords.append((body["x"], body["y"]))
        else:
            for body in snake["body"]["data"]:
                wall_coords.append((body["x"], body["y"]))

    a = AStar()

    a.init_grid(data["height"],data["width"],wall_coords,start,goal)

    solution = a.solve()

    if solution:
        return convert_direction(start, solution[1])

    return None


def convert_direction(start, coord):

    if start[0] > coord[0]:
        return "left"
    elif start[0] < coord[0]:
        return "right"

    if start[1] > coord[1]:
        return "up"

    return "down"


'''
Thanks to Laurent Luce for supplying A*
https://github.com/laurentluce/python-algorithms/
'''
class Cell(object):
    def __init__(self, x, y, reachable):
        """Initialize new cell.
        @param reachable is cell reachable? not a wall?
        @param x cell x coordinate
        @param y cell y coordinate
        @param g cost to move from the starting cell to this cell.
        @param h estimation of the cost to move from this cell
                 to the ending cell.
        @param f f = g + h
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0



class AStar(object):
    def __init__(self):
        # open list
        self.opened = []
        heapq.heapify(self.opened)
        # visited cells list
        self.closed = set()
        # grid cells
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    def init_grid(self, width, height, walls, start, end):
        """Prepare grid cells, walls.
        @param width grid's width.
        @param height grid's height.
        @param walls list of wall x,y tuples.
        @param start grid starting point x,y tuple.
        @param end grid ending point x,y tuple.
        """
        self.grid_height = height
        self.grid_width = width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    def get_heuristic(self, cell):
        """Compute the heuristic value H for a cell.
        Distance between this cell and the ending cell multiply by 10.
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_cell(self, x, y):
        """Returns a cell from the cells list.
        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        return self.cells[x * self.grid_height + y]

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.grid_width-1:
            cells.append(self.get_cell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        if cell.y < self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def get_path(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """Update adjacent cell.
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def solve(self):
        """Solve maze, find path to ending cell.
        @returns path or None if not found.
        """
        # add starting cell to open heap queue
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list so we don't process it twice
            self.closed.add(cell)
            # if ending cell, return found path
            if cell is self.end:
                return self.get_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))

if __name__ == '__main__':
    bottle.run(bottle.default_app(), host='0.0.0.0', port='6000')
