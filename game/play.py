####################
# PLAYING THE GAME #
####################

from datetime import datetime

from flask import (
        Blueprint, session, redirect, render_template, url_for, flash
)

from game.models import Game, db
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room

# Create the play blueprint
bp = Blueprint('play', __name__, url_prefix='/play')

# Extension: socketio
socketio = SocketIO()

# List of active rooms
rooms = {}

# Room class: its id is the username of its creator
class Room:

    def __init__(self, id):
        self.id = id;
        self.created = datetime.utcnow()
        self.started = None
        self.finished = None

    # List of players in the room
    players = []

    # The room is full if it has 4 players
    def is_full(self):
        if len(self.players) == 4:
            return True
        return False

    # The room is available if it has less than 4 players and has not started
    def is_available(self):
        if len(self.players) < 4 and self.started is None:
            return True
        return False


# New game function: creates a new game
@bp.route('/newgame')
def newgame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Creates a room with the username that created it as id
    creator = current_user.username
    if creator not in rooms:
        rooms[creator] = Room(creator)

    # Unless there is an active room from the same creator
    else:
        flash('The game you created is not finished.')

    # Sends the user to the new game room
    return redirect(url_for('play.gameroom', id=creator))


# Join game function:
@bp.route('/joingame')
def joingame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # List of available rooms to join
    available = []

    # Searches for available rooms
    for room in rooms.values():
        if room.is_available():
            available.append(room)

    return render_template('play/available.html', rooms = available)


# Game room function: where the game occurs
@bp.route('/gameroom/<id>')
def gameroom(id):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the room object from the active rooms dictionary
    room = rooms[id]
    # Saves the room in the session
    session['room'] = id

    # Redirect if there is no such room
    if room is None:
        flash('Game not found.')
        return redirect(url_for('info.home'))

    # Add the new player to the room
    if current_user.username not in room.players:
        # Unless the room is full
        if room.is_full():
            flash('The game is full. Try another one.')
            return redirect(url_for('play.joingame'))
        room.players.append(current_user.username)

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


# Socket connection event
@socketio.on('connect')
def new_connection():
    if not current_user.is_authenticated:
        return False
    
    # Gets the room where the client is at form the session
    room = rooms[session['room']]

    # Does nothing if the player has not already been added to the room
    if current_user.username not in room.players:
        return False

    # Adds the player to the room channel (to receive events)
    join_room(room)
    
    # Sends event 'user has connected' to everyone in the room
    emit("new_connection", 
            {"connection" : 'User {} has connected.'.format(current_user.username)},
            room = room)



#@socketio.on('disconnect')
#def new_disconnection():
#    if not current_user.is_authenticated:
#        flash('You need to login first.')
#        return False
#    print('New desconnection')
#    msg = 'User {} has disconnected.'.format(current_user.username)
#    emit("new_disconnection", {"msg" : msg}, broadcast=True)

#@socketio.on('new game')
#def new_game():
#    if not current_user.is_authenticated:
#        return False
#    waitroom[request.sid] = current_user.username
#    print(waitroom)
