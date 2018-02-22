# flake8: noqa
import random
import logging

SNAKE_NAME = "Rubber Ducky"
SNAKE_COLOR = "#ff0000"
SNAKE_SECONDARY_COLOR = "#ff0000"
SNAKE_IMAGE = "duck.jpg"
SNAKE_HEAD = "safe"
SNAKE_TAIL = "freckled"

SNAKE_TAUNT = random.choice([
    "I'm crazy, I'm nuts. Just the way my brain works. I'm not normal. I think differently.",
    "I know who I am and what I'm doing in my life and what I've accomplished and continue to accomplish as a performer, as a writer, as an artist, as a person, as a human being.",
    "I grew up below the poverty line; I didn't have as much as other people did. I think it made me stronger as a person, it built my character. Now I have a 4.0 grade point average and I want to go to college, and just become a better person.",
    "No one can stop me.",
    "I think older people can appreciate my music because I really show my heart when I sing, and it's not corny. I think I can grow as an artist, and my fans will grow with me.",
    "I want my world to be fun.",
    "My mind is always racing.",
    "Young people in the business have grown up and made the wrong decisions, or bad decisions, and haven't been good role models. To be someone that people look up to is important to me.",
    "When people see a negative thing about me on a magazine, they're gonna buy it. Every time some site writes something bad, all my followers go on there, and it brings them more traffic.",
    "I got a bright future ahead of me.",
    "Of course, I think that people are just waiting for that time when I make a mistake and they're gonna jump on it.... There's gonna be haters.",
    "Not trying to be arrogant, but if I walked down the street and a girl saw me, she might take a look back because maybe I'm good-looking, right?",
    "I started singing about three years ago, I entered a local singing competition called Stratford Idol. The other people in the competition had been taking singing lessons and had vocal coaches. I wasn't taking it too seriously at the time, I would just sing around the house. I was only 12 and I got second place.",
    "I'm looking forward to influencing others in a positive way. My message is you can do anything if you just put your mind to it.",
    "It's not me trying to act or pose in a certain way. It's a lifestyle - like a suaveness or a swag, per se.",
    "I want to be a young dad. By 25 or 26 I want to see myself, like, married or start looking for a family.",
    "I think I'm probably gonna quit music.",
    "The Beliebers have done some pretty crazy stuff. Last week, the night before I was due to do a show in Germany, four girls went into a dumpster so they could sneak into the building. They climbed in and hid. When the guys working on the truck started getting the garbage they found them straight away. It was crazy.",
    "I've had a few gigs where things have got out of hand and there has been a huge crush with my fans. They are important and I don't want them being hurt. They are a mad crowd.",
    "Sometimes it's overwhelming but I love my fans and it's always great to see them.",
    "I'm happy with the man I'm becoming.",
    "Cheryl Cole and Katy Perry are two of the hottest girls in the world - and so normal and funny with it. If I was a few years older they are the kind of girls I'd like to date. I want a younger version of Cheryl and Katy - a mixture of the two would be hot.",
    "Canada's the best country in the world."
])

DIR_NAMES = ['up', 'down', 'left', 'right']
DIR_VECTORS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

INVALID_MOVE = 0
HDEPTH = 10

EMPTY = 0
SNAKE = 1
FOOD = 2
SPOILED = 3

FOOD_CLOSE_HEALTH = 90  # Between this and ignore health just go for close food
FOOD_CLOSE_DIST = 3  # The distance food is away to be considered close
FOOD_MEDIUM_HEALTH = 60  # Between this and close distance is medium distance 
FOOD_MEDIUM_DIST = 6  # How many moves away is a medium distance food
FOOD_HUNGRY_HEALTH = 40  # When we should start going directly to safe food and contested food if there isn't safe food
FOOD_DANGEROUS = 10  # If below value in health go for potentially dangerous food or if distance to food is greater than value
FOOD_STEAL_DIST = FOOD_CLOSE_DIST + 2  # If we are within clost dist to a food and an enemy is within 5 then steal it no matter our health

DISABLE_ATTACKING = False  # Set to True to disable attack logic

SAFE_SPACE_FACTOR = 1.5
TAIL_PREFERENCE_FACTOR = 1.5

# Ratings for how important each thing is
FOOD_RATING = 6
SPOILED_RATING = 4
BODY_RATING = 0.5
EMPTY_RATING = 0.5
ENEMY_RATING = -2
OUT_SIDE_BOARD_RATING = -2

LOG_LEVEL = logging.DEBUG
