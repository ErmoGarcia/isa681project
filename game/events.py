from time import sleep
from datetime import datetime

from flask import session, request

from game.play import socketio, rooms

from flask_socketio import emit, join_room, leave_room, close_room
from flask_login import current_user

def start(room):
    room.started = datetime.utcnow()
    room.deck.shuffle()
    print(room.deck)
    return


def finish(room):
    room.finished = datetime.utcnow()
    rooms.pop(room.id)
    socketio.close_room(room)
    return

# Socket connection event
@socketio.on('connect')
def new_connection():
    if not current_user.is_authenticated:
        return False

    print('on connection: '+str(request.sid))

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])

    print(rooms)

    # Gets the Player from the Room
    player = room.getByName(current_user.username)

    # Does nothing if the player has not already been added to the room
    if player is None:
        return False

    # Stores the connection SID for the player
    player.connected(request.sid)

    # If player was just afk, do nothing else
    if player.afk:
        player.afk = False
        return True

    # Adds the player to the room channel (to receive events)
    join_room(room)

    # Sends event 'user has connected' to everyone in the room
    emit("new_connection", {"connection" :
            'User {} has connected.'.format(player.name)},
            room = room)

    if room.isFull():
        start_game(room)


@socketio.on('disconnect')
def new_disconnection():

    # Gets the room where the client was at form the session
    room = rooms.get(session['room'])
    if room is None:
        raise Exception('No room available to connect.')

    player = room.getBySid(request.sid)

    if player is None:
        raise Exception('Players should be in the game before they disconnect.')

    #room.players.remove(player)

    player.disconnected()
    leave_room(room)

    emit("new_disconnection", {"disconnection" :
            'User {} has disconnected.'.format(player.name)},
            room=room)

    print('removed: '+player.name)

    sleep(60)

    if player.afk:
        #finish(room)
        emit("game_over", {"game_over" :
                'User {} was afk for too long.'.format(player.name)},
                room=room)
