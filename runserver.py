"""
This script runs the hub application using a development server.
"""

from os import environ
from hub import create_app


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    PORT = 5050
        
    app = create_app()
    app.run(HOST, PORT)
