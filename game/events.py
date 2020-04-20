from game.play import socketio
from flask_socketio import emit, join_room

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
