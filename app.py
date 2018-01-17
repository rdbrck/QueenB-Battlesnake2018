import os
import bottle

from app import application

if __name__ == "__main__":
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080')
    )
