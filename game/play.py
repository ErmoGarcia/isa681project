####################
# PLAYING THE GAME #
####################


from datetime import datetime, timezone
from uuid import uuid4
import time

from flask import (
    Blueprint, session, request, redirect, render_template, url_for, flash
)

from game.models import db, User, Game, Move
from game.mus import Room, Card

from flask_login import current_user
from flask_socketio import (
    SocketIO, emit, send, join_room, leave_room, close_room
)

# Create the play blueprint
bp = Blueprint('play', __name__, url_prefix='/play')

# Extension: socketio
socketio = SocketIO()


# List of active rooms
rooms = {}


# New game function: creates a new game
@bp.route('/newgame')
def newgame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

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

    return render_template('play/available.html', rooms=available)


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
    if current_user.username not in room.getPlayers():
        # Unless the room is full
        if room.isFull():
            flash('The game is full. Try another one.')
            return redirect(url_for('play.joingame'))
        room.addPlayer(current_user.username)

    return render_template('play/gameroom.html')


# Socket connection event
@socketio.on('connect', namespace='/game')
def new_connection():
    if not current_user.is_authenticated:
        return False

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])

    # Gets the Player from the Room
    player = room.getByName(current_user.username)

    # Does nothing if the player has not already been added to the room
    # or if the player is already connected
    if player is None or player in room.connected:
        return False

    # Stores the connection SID for the player
    room.connect(player, request.sid)

    # Adds the player to the room channel (to receive events)
    join_room(room)
    print('{} has connected.'.format(player.name))

    # If player was just afk, do nothing else
    if room.isStarted():
        reconnect(room, player)
        return True

    # Sends event 'user has connected' to everyone in the room
    send("User {} has connected.".format(player.name),
         namespace='/game', room=room)

    # If the player that just connected was the 4th in the room the game starts
    if room.isFull():
        start(room)
    return


# Socket disconnection event
@socketio.on('disconnect', namespace='/game')
def new_disconnection():

    # Gets the room where the client was at form the session
    room = rooms.get(session['room'])
    if room is None:
        return

    # Because the player that just disconnected might have logged out,
    # we check his identity using th sid
    player = room.getBySid(request.sid)
    if player is None:
        return

    # The player is removed from the connected players list but
    # not from the actual players list yet, he might still come back
    room.disconnect(player)
    leave_room(room)
    print('{} has disconnected.'.format(player.name))

    # Unless the game has not started already
    if room.isStarted():
        # It waits 60 seconds
        time.sleep(60)

        # If after that time the player is not back in the connected list
        if player not in room.connected:
            send("User {} was afk for too long.".format(player.name),
                 namespace='/game', room=room)

            # The player's team loses
            if player.team == "blue":
                room.scoreRed = 100
            if player.team == "red":
                room.scoreBlue = 100

            # The game ends
            finish(room)
            return
        return

    # The player is now removed from the players list
    room.players.remove(player)
    send("User {} has disconnected.".format(player.name),
         namespace='/game', room=room)

    # If there are no players left, the room is destroyed
    # this happens only if the game has not started
    if len(room.players) == 0:
        rooms.pop(session['room'])
    return


# Socket event triggered by a player move during the mus phase
@socketio.on('client_mus_turn', namespace='/game')
def client_mus_turn(data):
    if not current_user.is_authenticated:
        return False

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])
    if room is None:
        return False

    # Checks that the sid of the socket conection from which the input comes
    # corresponds to the logged in player
    player = room.getBySid(request.sid)
    if player not in room.players or player.name != current_user.username:
        return False

    # Gets the round and the phase from the room object
    round = room.round
    if round is None:
        return False
    phase = round.getPhase()
    if phase is None:
        return False

    # If the phase is not mus, the move is not valid
    if not phase.isMus():
        return False

    # Input validation!
    if not mus_validate(data):
        return False

    # Chacks if the player wants to cut mus
    if bool(data['cutMus']):
        cut_mus(room, player)
        return True

    # Calls mus
    call_mus(room, player, data['discards'])
    return True


# Input validation during Mus phase
def mus_validate(data):
    # cutMus must be evaluatable as a boolean
    try:
        bool(data['cutMus'])
    except Exception:
        return False

    # discards must an iterable with 0 to 4 elements
    try:
        iter(data['discards'])
        if len(data['discards']) > 4 or len(data['discards']) < 0:
            return False

        # each element consists of an int between 0 and 10
        # and a string from the set of suits
        for d in data['discards']:
            try:
                if len(d) != 2:
                    return False
                if not int(d[0]) in range(1, 11):
                    return False
                suits = {
                    "oros",
                    "copas",
                    "espadas",
                    "bastos",
                    "o",
                    "c",
                    "b",
                    "e"
                }
                if not str(d[1]) in suits:
                    return False
            except Exception:
                return False
    except Exception:
        return False
    return True


# When a player calls cut mus
def cut_mus(room, player):
    msg = "{} cuts mus.".format(player.name)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)
    mus_turn(room, True)
    return


# When a player calls mus
def call_mus(room, player, discards):
    msg = "{} calls mus.".format(player.name)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)

    phase = room.round.getPhase()
    if not phase.isMus():
        return

    # The cards that the player selected are added to his discards list
    for discard in discards:
        rank = int(discard[0])
        suit = str(discard[1])
        card = Card(rank, suit)
        player.addDiscard(card)

    # If everyone has selected his discards, everyone is discarded
    if phase.allDiscarded():
        msg = "Everybody called mus."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        phase.discardAll()
        mus_turn(room, False)
    return


# Socket event triggered by a player move during a phase other than mus
@socketio.on('client_game_turn', namespace='/game')
def client_game_turn(data):
    if not current_user.is_authenticated:
        return False

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])
    if room is None:
        return False

    # Checks that the sid of the socket conection from which the input comes
    # corresponds to the logged in player
    player = room.getBySid(request.sid)
    if player not in room.players or player.name != current_user.username:
        return False

    # Gets the room and phase from the room object
    round = room.round
    if round is None:
        return False
    phase = round.getPhase()
    if phase is None:
        return False

    # In some phases not all players are allowed to participate
    if player not in phase.players:
        return False

    # A player can't make a move if its not his turn
    turn = phase.getTurn()
    if player != turn:
        return False

    # Input validation!
    if not validate_turn(data):
        return False

    # Get the last bid that have been made
    envite = phase.lastBid

    # When the player is introducing a new bid
    if int(data['bid']) is not None and int(data['bid']) > 0:
        new_envite(room, player, envite, int(data['bid']))
        return True

    # When the player sees the last bid
    if bool(data['see']):
        if envite is None:
            return False

        player_sees(room, player)
        return True

    # When the palyer passes
    player_passes(room, player)
    return True


# Input validation during a phase other than mus
def validate_turn(data):
    # bid can be None or an integer between 0 and 40
    try:
        if data['bid'] is not None:
            if int(data['bid']) < 0 or int(data['bid']) > 40:
                return False
    except Exception:
        return False

    # see must be evaluatable as a boolean
    try:
        bool(data['see'])
    except Exception:
        return False
    return True


# When the player is introducing a new bid
def new_envite(room, player, envite, bid):
    phase = room.round.getPhase()
    turn = phase.getTurn()

    # It there is a bet already, the new one increases it
    if envite is not None:
        bid = bid + envite.value

    msg = "{player} bets {value}.".format(player=player.name, value=bid)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)
    phase.envidar(player, bid)

    # The turns order is altered
    # only players of the opposite team can make a move now
    while (turn.team == phase.lastBid.color):
        turn = phase.nextTurn()
    game_turn(room)
    return


# When a player sees the last bid
def player_sees(room, player):
    msg = "{} sees the bet.".format(player.name)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)
    room.round.getPhase().see()
    new_phase(room)
    return


# When a player passes
def player_passes(room, player):
    phase = room.round.getPhase()
    turn = phase.getTurn()
    envite = phase.lastBid

    # If there is a bet on the table
    if envite is not None:
        msg = "{} doesn't see the bet.".format(player.name)
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        turn = phase.nextTurn()

        # The turns order is altered
        # only players of the opposite team can make a move now
        while (turn.team == envite.color):
            if turn == envite.player:
                phase.fold()
                new_phase(room)
                if room.round.getPhase().isMus():
                    return True
            turn = phase.nextTurn()
        game_turn(room)
        return True

    msg = "{} passes.".format(player.name)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)
    turn = phase.nextTurn()

    # When everyone passed
    if phase.allPassed():
        new_phase(room)

    if room.round.getPhase().isMus():
        return True

    game_turn(room)
    return True


# When the game starts
def start(room):
    # The time is set and the teams are made
    # the 1st and the 3rd player entering the room are the blue team
    # the 2nd and 4th player are the red team
    room.started = datetime.now(timezone.utc)
    room.makeTeams()

    start_db(room)

    # Every player receives the names of other players
    # and his team (based on his possition entering the room)
    for p in room.players:
        data = {
            "scoreBlue": room.scoreBlue,
            "scoreRed": room.scoreRed,
            "players": room.getPlayers(),
            "player_number": room.players.index(p)
        }
        emit('start_game', data, namespace='/game', room=p.sid)
    new_round(room)
    return


# When a new round starts
def new_round(room):
    room.newRound()
    mano = room.getMano().name
    msg = "{} is mano this round.".format(mano)
    move_db(room, msg)

    # The players receive the updated scores
    data = {
        "scoreBlue": room.scoreBlue,
        "scoreRed": room.scoreRed,
    }
    emit('start_round', data, namespace='/game', room=room)
    send(msg, namespace='/game', room=room)

    mus_turn(room, False)
    return


# When a new phase starts
def new_phase(room):
    round = room.round
    phase = round.nextPhase()

    # When there are no phases left for this round
    if phase is None:
        show_down(room)
        time.sleep(60)

        # Checks if the game ended after the points update
        finished = score_update(room)
        if finished:
            return

        new_round(room)
        return

    msg = "New phase {}.".format(phase.getName())
    move_db(room, msg)
    send(msg, namespace='/game', room=room)

    # When the new phase is pares it has to check who has pares
    # those who don't won't participate
    if phase.isPares():
        for p in phase.players:
            if p.hasPares() is not None:
                msg = "{0} has pares.".format(p.name)
                move_db(room, msg)
                send(msg, namespace='/game', room=room)
            else:
                msg = "{0} doesn't have pares.".format(p.name)
                move_db(room, msg)
                send(msg, namespace='/game', room=room)
        if not thereIsPares(room):
            new_phase(room)
            return

    # When the new phase is juego it has to check who has juego
    # those who don't won't participate
    if phase.isJuego():
        for p in phase.players:
            if p.hasJuego():
                msg = "{0} has juego.".format(p.name)
                move_db(room, msg)
                send(msg, namespace='/game', room=room)
            else:
                msg = "{0} doesn't have juego.".format(p.name)
                move_db(room, msg)
                send(msg, namespace='/game', room=room)
        if not thereIsJuego(room):
            new_phase(room)
            return

    game_turn(room)
    return


# Updates the scores
def score_update(room):
    # Gets the winners for each round and the points earned
    winners = room.round.winners
    points = room.round.points

    # Assigns the points to the corresponding team
    for i in range(0, 4):
        winner = winners[i]
        amount = points[i]
        if winner is None:
            pass
        elif winner.team == "blue":
            room.scoreBlue = room.scoreBlue + amount
        elif winner.team == "red":
            room.scoreRed = room.scoreRed + amount

        # When a team score is more than 40, that team has won
        if room.scoreRed >= 40 or room.scoreBlue >= 40:
            finish(room)
            return True
    return False


# When a mus phase starts
def mus_turn(room, cutMus=False):

    # When someone has cut
    if cutMus:
        new_phase(room)
        game_turn(room)
        return

    # Informs the players of the cards they have gotten
    for p in room.players:
        cards = []
        for c in p.cards:
            cards.append([c.rank, c.suit])

        data_mus = {
            "cutMus": False,
            "cards": cards
        }
        emit('mus_turn', data_mus, namespace='/game', room=p.sid)

    return


# When a phase other than mus starts
def game_turn(room):
    phase = room.round.getPhase()
    turn = phase.getTurn()

    blueBid, redBid = phase.getLastBids()
    phase_name = phase.getName()

    # Informs the players of the bids on the table, the phase and the turn
    data = {
        "phase": phase_name,
        "blueBid": blueBid,
        "redBid": redBid,
        "turn": turn.name
    }

    msg = "{} speaks.".format(turn.name)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)
    emit('game_turn', data, namespace='/game', room=room)

    # It waits 40 seconds for the player to make a move
    # if not, it is considered that he passed
    time.sleep(40)
    if phase == room.round.getPhase() and turn == phase.getTurn():
        msg = "{} was too slow.".format(turn.name)
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        player_passes(room, turn)
    return


# The showdown of the current round
def show_down(room):
    # Informs everyone of the cards of all players
    playerCards = {}
    for p in room.players:
        cards = []
        for c in p.cards:
            cards.append((c.rank, c.suit))
        playerCards[p.name] = cards

    # Gets the winners and corresponding points
    winners = room.round.winners
    points = room.round.points

    grande = ("Nobody", 0)
    chica = ("Nobody", 0)
    pares = ("Nobody", 0)
    juego = ("Nobody", 0)

    # Informs the players of the winner and points for each phase
    if winners[0] is not None:
        grande = (winners[0].name, points[0])
        msg = "{0} ({1} team) wins {2} points for grande.".format(
            winners[0].name, winners[0].team, points[0]
        )
        move_db(room, msg)
    if winners[1] is not None:
        chica = (winners[1].name, points[1])
        msg = "{0} ({1} team) wins {2} points for chica.".format(
            winners[1].name, winners[1].team, points[1]
        )
        move_db(room, msg)
    if winners[2] is not None:
        msg = "{0} ({1} team) wins {2} points for pares.".format(
            winners[2].name, winners[2].team, points[2]
        )
        move_db(room, msg)
        pares = (winners[2].name, points[2])
    if winners[3] is not None:
        msg = "{0} ({1} team) wins {2} points for grande.".format(
            winners[3].name, winners[3].team, points[3]
        )
        move_db(room, msg)
        juego = (winners[3].name, points[3])
    # if len(winners) > 4:
    #     punto = (winners[4].name, points[1])
    # else:
    #     punto = None

    # Sends everything out
    data = {
        "playerCards": playerCards,
        "grande": grande,
        "chica": chica,
        "pares": pares,
        "juego": juego,
        # "punto": punto
    }
    emit('show_down', data, namespace='/game', room=room)
    return


# When the game finishes
def finish(room):
    # Checks the score to decide who won
    if room.scoreBlue > room.scoreRed:
        msg = "Game ended: blue team won."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)

        # Updates the wins and losses for each player in the DB
        for p in room.players:
            user = User.query.filter_by(username=p.name).first()
            if p.team == "blue":
                emit('finish', {"message": "You won!"},
                     namespace='/game', room=p.sid)
                user.wins = user.wins + 1
            elif p.team == "red":
                emit('finish', {"message": "You lost :("},
                     namespace='/game', room=p.sid)
                user.losses = user.losses + 1

    # Checks the score to decide who won
    if room.scoreRed > room.scoreBlue:
        msg = "Game ended: red team won."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)

        # Updates the wins and losses for each player in the DB
        for p in room.players:
            user = User.query.filter_by(username=p.name).first()
            if p.team == "red":
                emit('finish', {"message": "You won!"}, room=p.sid)
                user.wins = user.wins + 1
            elif p.team == "blue":
                emit('finish', {"message": "You lost :("}, namespace='/game',
                     room=p.sid)
                user.losses = user.losses + 1

    # Sets the time
    room.finished = datetime.now(timezone.utc)
    game = Game.query.filter_by(room_id=room.id).first()
    game.finished = room.finished
    db.session.commit()

    # Destroys the room
    rooms.pop(session['room'])
    close_room(room)
    return


# Check if the pares phase will be played
def thereIsPares(room):
    phase = room.round.getPhase()

    # Gets the teams of the players who have pares
    teams = phase.noPares()

    # When nobody has pares
    if len(teams) == 0:
        msg = "Nobody has pares."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    # When only one team has pares
    if "blue" not in teams:
        msg = "Only red team has pares."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    # When only one team has pares
    if "red" not in teams:
        msg = "Only blue team has pares."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    return True


# Check if the juego phase will be played
def thereIsJuego(room):
    phase = room.round.getPhase()

    # Gets the teams of the players who have juego
    teams = phase.noJuego()

    # When nobody has juego
    if len(teams) == 0:
        msg = "Nobody has juego."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    # When only one team has juego
    if "blue" not in teams:
        msg = "Only red team has juego."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    # When only one team has juego
    if "red" not in teams:
        msg = "Only blue team has juego."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    return True


# When a player is connecting back
# (he was already in the room when the game started)
def reconnect(room, player):
    # He is informed of the scores, the player names and his team
    data = {
        "scoreBlue": room.scoreBlue,
        "scoreRed": room.scoreRed,
        "players": room.getPlayers(),
        "player_number": room.players.index(player)
    }
    emit('start_game', data, namespace='/game', room=player.sid)

    data = {
        "scoreBlue": room.scoreBlue,
        "scoreRed": room.scoreRed,
    }
    emit('start_round', data, namespace='/game', room=player.sid)

    # He is informed of his current cards
    cards = []
    for c in player.cards:
        cards.append([c.rank, c.suit])

    data_mus = {
        "cutMus": False,
        "cards": cards
    }
    emit('mus_turn', data_mus, namespace='/game', room=player.sid)

    # He is informed of the current bids, phase and turn
    phase = room.round.getPhase()
    if not phase.isMus():
        turn = phase.getTurn()

        blueBid, redBid = phase.getLastBids()

        phase_name = phase.getName()

        data = {
            "phase": phase_name,
            "blueBid": blueBid,
            "redBid": redBid,
            "turn": turn.name
        }
        emit('game_turn', data, namespace='/game', room=player.sid)
    return


# Creates the DB entry for the game
def start_db(room):
    game = Game(room_id=room.id, started=room.started)
    for p in room.players:
        user = User.query.filter_by(username=p.name).first()
        game.players.append(user)
    db.session.add(game)
    db.session.commit()
    return


# Creates the DB entry for a move
def move_db(room, msg):
    game = Game.query.filter_by(room_id=room.id).first()
    timestamp = datetime.now(timezone.utc)
    phase = room.round.getPhase().getName()
    message = msg

    # Saves every player's cards
    cards = []
    for p in room.players:
        for c in p.cards:
            cards.append('{0:0>2}{1}.jpg'.format(c.rank, c.suit[0]))

    for i in range(len(cards), 16):
        cards.append('Reverse.jpg')

    move = Move(timestamp=timestamp, phase=phase, message=message,
                scoreBlue=room.scoreBlue, scoreRed=room.scoreRed,
                card11=cards[0], card12=cards[1], card13=cards[2],
                card14=cards[3], card21=cards[4], card22=cards[5],
                card23=cards[6], card24=cards[7], card31=cards[8],
                card32=cards[9], card33=cards[10], card34=cards[11],
                card41=cards[12], card42=cards[13], card43=cards[14],
                card44=cards[15])

    game.moves.append(move)
    db.session.add(move)
    db.session.commit()
    return
