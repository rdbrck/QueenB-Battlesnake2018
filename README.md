# Queen B

### Strategy

General Flow:
- gather data and setup board by freeing up spaces and finding 'bad_positions' we don't want to move in to (using floodfills and other logic)
- determine if we are boxed in
- determine if we have the opportunity to kill a snake (head to head and tunnel closing)
- determine which food (if any) we want to get
- do the following in order (skip a step if we have determined we don't want to do it or found a move in a previous step)
	- attacking logic (unless we really need to prioritize food)
	- boxed in logic (find exit then determine longest path)
	- food pathing logic (bfs to pre determined food)
	- find 'safe_spots' on the board by rating cells and path to the one that has the best rating/best path
- if for some reason we still don't have a move (caught an error or all moves are fairly bad) do a series of floodfills to determine our best option


This snake is a 'local search' snake that considers a large amount of situations (no predictions on what other snakes are going to do).
During development we opted to use a variety of configuration variables so that we could easily modify it to face different bountysnakes.
To help make sure this type of approach would work we created a set of static tests and dockerized several 'test' snakes.
These helped a lot to ensure that future changes did not break the existing code. Linting was also run periodically.

For the day of the competition this was deployed to a t2 instance in AWS.
Seeing as we don't do any look ahead we didn't need a large instance and we were responding within ~50ms on average.

[Strategy Brainstorming](docs/strategy-brainstorm.md) has some strategies that were discussed (most are not listed).

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

#### Dev Helpers

A Makefile is provided to ease tasks. Set up the virtualenv first.

```
# install dependencies
make bootstrap

# run static tests
make test-static

# clean, lint, test
make test
```

#### Local

A virtualenv is suggested when installing python requirements, although it's not required.
```
python3 -m venv .venv
. .venv/bin/activate
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
