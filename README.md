# battlesnake2018

### Strategy

tl;dr - pick a point, BFS, floodfill, catch errors, move

Our strategy was to use a local search algorithm with everything we could think added in.

It would start by choosing a general direction to move based on very simple information about the location of snakes and food (where they were, open space on board, distance to food compared to other snakes, our health, other snakes length, etc.) Once we picked a general direction we would look at all open spaces in that direction to evaluate how desirable they were (creating a list of rated spots). For each spot in this list we spawned a thread and ran a simple BFS to find the best path for each (pursuing the best). If nothing returned a path then we were trapped so we would floodfill in each direction and pick the longest path.

This was the basic concept, but there were a lot of overrides – We made some squares invalid to move into, such as the ones around enemy snakes heads when they were larger than us. However, we also ignored that override if we were very hungry. Quick floodfill checks were also run on surrounding areas to make sure that we weren’t moving into a dead end.

We were initially concerned about the 200ms response time limit. Following, we decided to avoid more complex algorithms such as Minimax or A*. However, the average response time for our snake on "production" hardware turned out to be ~30ms.

### Requirements

* docker and optionally docker-compose

- or -

* a working Python 3 development environment ([getting started guide](http://hackercodex.com/guide/python-development-environment-on-mac-osx/))
* [pip](https://pip.pypa.io/en/latest/installing.html) to install Python dependencies

### Running
You can run this with docker or locally on your computer.

#### Docker
```
docker-compose build
docker-compose up
```

#### Local

A virtualenv is suggested when installing python requirements, although it's not required.
```
python3 -m venv .venv
.venv/bin/activate

```

Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):
```
$ pip install -r requirements.txt
```

Then either run the app directly
```
$ python app.py # supply PORT to override default
```

Or using uwsgi
```
$ uwsgi --ini uwsgi/battlesnake-dev.ini # adjust uwsgi params accordingly
```

### Linting

From the top-level directory run the following
```
flake8 --config setup.cfg
```

### Static Tests

From the /tests/static directory run the following.
Currently tests a snake that is running at a specified url in utils.py's TEST_INSTANCE.
```
python test.py
```
