# flake8: noqa
import random
import logging

SNAKE_NAME = "Queen B"
SNAKE_COLOR = "#FFD700"
SNAKE_SECONDARY_COLOR = "#000000"
SNAKE_IMAGE = "yonce.png"
SNAKE_HEAD = "tongue"
SNAKE_TAIL = "freckled"

START_TAUNT = "All the single ladies!"
SNAKE_TAUNT = [
    "Nothin' else seems to hurt like the smile on your face when it's only in my memory",
    "What's worse, lookin' jealous or crazy?",
    "I am the dragon breathing fire. Beautiful mane I'm the lion",
    "I been sippin', that's the only thing that's keeping me on fire",
    "Out love was stronger than our pride",
    "I'm bigger tahn life. My name is the lights. I'm the number one chick, I don't need no hype",
    "Middle fingers up, put them hands high. Wave it in his face, tell him boy, bye",
    "I break chains all by myself, won't let my freedom rot in hell. Imma keep runnin' cus a winner don't quit on themselves",
    "You don't deserve my tears. I guess that's why they ain't here",
    "I don't know much about fighting, but I know I will fight for you",
    "I'll be there for you if somebody hurts you. Even if that somebody is me",
    "Don't bore me just show me. All menm talk but don't please",
    "Yep, I put on him, It ain't nothing that I can't do. Yup, I buy my own if he deserve it, but his shit too",
    "It's the way that you know what I thought I knew",
    "Diva' is a femal version of a hustler",
    "If you scared, call that reverend",
    "Some call it 'Arrogant', I call it 'Confident'",
    "I took some time to live my life. But don't think I'm just his little wife",
    "I'm a host of imperfection, and you see past all that",
    "Gotta check these chicks cause you they gon' block when I take these flicks",
    "I swore I'd never fall again, but this don't even feel like falling",
    "True love breathes salvation back into me",
    "If you thought I would wait for you, you though wrong",
    "The truth of the matter is replacing you is so easy",
    "Nine times out of ten, I'm in my feelings. Ten times out of nine I'm only human",
    "Freakum dress out my closet, Yonce filling out the skirt, I look damn good, I ain't lost it",
    "Got diamonds on my neck, got diamonds on my records",
    "From now on, I'm gonna be my onw best friend",
    "I love you even more than who I thought you were before",
    "Took 45 minutes to get all dressed up, and we ain't even gonna make it to this club",
    "Pretty hurts. we shine the light on whatever's worst; Perfection is a disease of a nation",
    "Tell me how should I feel when I know what I know and my female intuition tellin' me you a dog",
    "We're smart enough to make these millions, strong enough to bear the children, then get back to business",
    "Who needs a degree when you're schoolin' life?",
    "Don't be mad once you see that he want it",
    "Whatever I get you putting it on, now take it off while I watch you perform",
    "I'm known to walk alone but I'm alone for a reason. Sending me a drink ain't appeasin believe me",
    "Turn you into a star, I got it like that",
    "You givin' me a taste of your honey, I want the whole beehive",
    "I sneezed on that beat, and the beat got sicker"
]

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

FOOD_CLOSE_HEALTH = 80  # Between this and ignore health just go for close food
FOOD_CLOSE_DIST = 3  # The distance food is away to be considered close
FOOD_MEDIUM_HEALTH = 65  # Between this and close distance is medium distance
FOOD_MEDIUM_DIST = 6  # How many moves away is a medium distance food
FOOD_HUNGRY_HEALTH = 50  # When we should start going directly to safe food and contested food if there isn't safe food
FOOD_HUNGRY_WALL_HEALTH = 70  # When we should start going for food next to walls (put way lower if there is lots of food) 30 if playing against Scott
FOOD_DANGEROUS_HEALTH = 10  # If below value in health go for potentially dangerous food
FOOD_DANGEROUS_DIST = 6  # Go for potentially dangerous food if distance to food is greater than value
FOOD_STEAL_DIST = 3  # If we are within close/medium dist to a food and an enemy is within close/medium+value then steal it no matter our health
FOOD_BOXED_IN_HEALTH = 25  # if we are boxed in and below this value in health then prioritize food

DISABLE_ATTACKING = False  # Set to True to disable attack logic
DISABLE_STEALING = False  # Set to True to disable food stealing

SAFE_SPACE_FACTOR = 2
TAIL_PREFERENCE_FACTOR = 1.5

# Ratings for how important each thing is
FOOD_RATING = 6
SPOILED_RATING = 4
BODY_RATING = 0.25
EMPTY_RATING = 0.25
ENEMY_RATING = -2
OUT_SIDE_BOARD_RATING = -3

LOG_LEVEL = logging.DEBUG
