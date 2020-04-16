#!/bin/env python
from game import create_app
from game.play import socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)
