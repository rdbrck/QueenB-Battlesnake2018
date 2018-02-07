import ujson
import random
import copy


TEST_INSTANCE = 'http://127.0.0.1:9000/move'
TEST_SNAKE_ID = '58a0142f-4cd7-4d35-9b17-815ec8ff8e70'


class TestGameData(object):
    def __init__(self, **kwargs):
        with open('./move.json') as move:
            self.data = ujson.load(move)

        with open('./snake.json') as snake:
            self.snake_default = ujson.load(snake)

        with open('./point.json') as point:
            self.point_default = ujson.load(point)

    def set_food(self, coords):
        foods = []
        for coord in coords:
            food = copy.deepcopy(self.point_default)
            food['x'] = coord[0]
            food['y'] = coord[1]
            foods.append(food)
        self.data['food']['data'] = foods

    def set_self(self, coords, health=None):
        snake = copy.deepcopy(self.snake_default)
        for coord in coords:
            point = copy.deepcopy(self.point_default)
            point['x'] = coord[0]
            point['y'] = coord[1]
            snake['body']['data'].append(point)
        snake['length'] = len(snake['body']['data'])

        if health is not None:
            snake['health'] = health

        potential_snakes = self.data['snakes']['data']
        for snek in self.data['snakes']['data']:
            if snek.id == TEST_SNAKE_ID:
                potential_snakes.remove(snek)
                break
        potential_snakes.append(snake)

        self.data['you'] = snake
        self.data['snakes']['data'] = potential_snakes

    def add_enemy(self, coords, health=None):
        snake = copy.deepcopy(self.snake_default)
        snake['id'] = ''.join(random.choice('0123456789') for x in range(5))
        for coord in coords:
            point = copy.deepcopy(self.point_default)
            point['x'] = coord[0]
            point['y'] = coord[1]
            snake['body']['data'].append(point)
        snake['length'] = len(snake['body']['data'])

        if health is not None:
            snake['health'] = health

        self.data['snakes']['data'].append(snake)
