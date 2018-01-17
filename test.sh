#!/bin/bash -e
curl -X POST -H "Content-Type: application/json" --data-binary @move_fixture.json http://0.0.0.0:8080/move
