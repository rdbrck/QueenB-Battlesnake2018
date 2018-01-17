# battlesnake2018

#### who wrote me

* [Mark Roller](https://github.com/rollerbrick)

#### what's our strat?

tl;dr - pick a point, BFS, floodfill, catch errors, move

Our strategy was to use a local search algorithm with everything we could think added in.

It would start by choosing a general direction to move based on very simple information about the location of snakes and food (where they were, open space on board, distance to food compared to other snakes, our health, other snakes length, etc.) Once we picked a general direction we would look at all open spaces in that direction to evaluate how desirable they were (creating a list of rated spots). For each spot in this list we spawned a thread and ran a simple BFS to find the best path for each (pursuing the best). If nothing returned a path then we were trapped so we would floodfill in each direction and pick the longest path.

This was the basic concept, but there were a lot of overrides – We made some squares invalid to move into, such as the ones around enemy snakes heads when they were larger than us. However, we also ignored that override if we were very hungry. Quick floodfill checks were also run on surrounding areas to make sure that we weren’t moving into a dead end.

We were initially concerned about the 200ms response time limit. Following, we decided to avoid more complex algorithms such as Minimax or A*. However, the average response time for our snake on "production" hardware turned out to be ~30ms.

#### hardware and environment

BtAS was deployed to an m3.medium EC2 instance in the us-east AZ to minimize latency to the Battlesnake gameboard. The app itself was managed by uwsgi, running as a service behind nginx. Although, in hindsight, this is way more complicated than it needed to be.

We decided against Heroku due to the tendency for heroku deployments to go into sleepmode after a period of inactivity.

### you will need...

* a working Python 2.7 development environment ([getting started guide](http://hackercodex.com/guide/python-development-environment-on-mac-osx/))
* [pip](https://pip.pypa.io/en/latest/installing.html) to install Python dependencies

### running BtAS

A virtualenv is suggested when installing python requirements, although it's not required.

Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):
```
$ pip install -r requirements.txt
```

then either run the app directly

```
$ python app.py # supply PORT to override default
```

or run it using uwsgi

```
$ uwsgi --ini uwsgi/battlesnake-dev.ini # adjust uwsgi params accordingly
```
