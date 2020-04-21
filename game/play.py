####################
# PLAYING THE GAME #
####################

from datetime import datetime
from uuid import uuid4

from flask import (
        Blueprint, session, redirect, render_template, url_for, flash
)

from game.models import Game, db
from game.mus import Room

from flask_login import current_user
from flask_socketio import SocketIO

# Create the play blueprint
bp = Blueprint('play', __name__, url_prefix='/play')

# Extension: socketio
socketio = SocketIO()

# List of active rooms
rooms = {}

from game.events import *

# New game function: creates a new game
@bp.route('/newgame')
def newgame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Creates a room with the username that created it as id
    #creator = current_user.username
    #if creator not in rooms:
    #    rooms[creator] = Room(creator)

    # Creates a random id
    id = str(uuid4().int)

    # Checks that the id is unique
    if id in rooms:
        raise Exception('Every room needs to have a different id.')

    # Creates the room with the random unique id
    rooms[id] = Room(id)

    # Sends the user to the new game room
    return redirect(url_for('play.gameroom', id=id))


# Join game function:
@bp.route('/joingame')
def joingame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # List of available rooms to join and time they were created
    available = []

    # Searches for available rooms
    for room in rooms.values():
        if room.isAvailable():
            # Saves creation time and player names for each available room
            available.append((room.id, room.created, room.getPlayers()))

    return render_template('play/available.html', rooms = available)


# Game room function: where the game occurs
@bp.route('/gameroom/<id>')
def gameroom(id):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the room object from the active rooms dictionary
    room = rooms.get(id)

    # Redirect if there is no such room
    if room is None:
        flash('Game not found.')
        return redirect(url_for('info.home'))

    # Saves the room in the session
    session['room'] = id

    # Add the new player to the room
    if current_user.username not in room.players:
        # Unless the room is full
        if room.isFull():
            flash('The game is full. Try another one.')
            return redirect(url_for('play.joingame'))
        room.addPlayer(current_user.username)

    return render_template('play/gameroom.html')


# MOVE TO INFO???
# History function
@bp.route('/history')
def history():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # INCOMPLETE
    # Searches for games in the database
    games = Game.query.order_by(Game.started).all()
    return render_template('play/history.html', games = games)
