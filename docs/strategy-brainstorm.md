# Brainstorming

The purpose of this document is to record ideas for strategies.
Even strategies we don't intend to use should be recorded.
These can 

## Paradigms

There are different paradigms for viewing the game.
These may lend themselves to different techniques and strategies.

### Board View

Traditional over-head view -- what you see viewing the game arena.

Lends itself to human-designed strategy.

Evaluate "strength" of positions on the board.
Find a route there.
Choose left, straight, or right based on that.

### Snake View

First "person" view -- what you would see if you were the snake.

Lends itself to neural networks.
At each step (except the very first),
there are three things to choose:
left, straight, or right.

The board can be viewed as a tree with each node having three children.
This view still requires board-view knowledge
to account for walls and other snakes.

## Attack Strategies

### Head-On

Attempt to cause a head-on with a shorter snake.

### Cut Off

This strategy can be used with a fairly short snake
and irrespective of the length of the target snake.

Cut off a snake between yourself
and a wall,
another snake,
or the snake being cutoff itself.

### Partitions

This strategy is likely effective only when
snake length significantly exceeds board dimensions.

Choose path to partition the board
into larger and smaller sections
with the goal of being alone
(or at least with fewer other snakes)
in the larger section.
If snakes are getting longer,
this may cause snakes to simply
exhaust the space available to them.
It also increases the chance of collisions
or attacks between other snakes.

# How to set constants

Constants that affect strategies are dependent on
- board size,
- number of food,
- number of alive snakes,
- the ratio of the sum of all snake body lengths to the size of the board,
- the ratio of our snakes length to free space on the board,
- the ratio of food to open coordinates,
- ...

Some metrics are related,
but one or another may have better correlation to the effectiveness of a strategy.

For example,
- board size
- ratio of wall/corner-adjacent squares to total number of squares
- ratio of wall/corner-adjacent squares to open-area squares

are all related,
but some will correlate
more strongly with the success of a strategy than the others.

Some of the measures that apply statically to walls
also apply to snakes, but are dynamic.

For example,
- a corner square has one possible egress direction
- a wall square has two possible egress directions
- an open square has three possible egress directions

(On the first turn, every square has one more egress direction
because there is no restricting ingress diretion.)

This relates to dynamic conditions caused by other snake bodies,
- a square next to a linearly moving snake has two possible egress directions
- a square next to the inside of a snake turn has one possible egress direction
- a square between two linearly moving snakes has one possible egress direction

