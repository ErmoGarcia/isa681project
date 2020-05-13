####################
# PLAYING THE GAME #
####################


from datetime import datetime
from uuid import uuid4
import time

from flask import (
    Blueprint, session, request, redirect, render_template, url_for, flash
)

from game.models import db, User, Game, Move
from game.mus import Room, Card

from flask_login import current_user
from flask_socketio import SocketIO, emit, send, join_room, leave_room, close_room

# Create the play blueprint
bp = Blueprint('play', __name__, url_prefix='/play')

# Extension: socketio
socketio = SocketIO(cors_allowed_origins='http://localhost:8000')


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

    if room.isFull():
        start(room)


@socketio.on('disconnect', namespace='/game')
def new_disconnection():

    # Gets the room where the client was at form the session
    room = rooms.get(session['room'])
    if room is None:
        return

    player = room.getBySid(request.sid)
    if player is None:
        print('Players should be in the game before they disconnect.')
        return

    room.disconnect(player)
    leave_room(room)
    print('{} has disconnected.'.format(player.name))

    if room.isStarted():
        time.sleep(60)

        if player not in room.connected:
            print('game over')
            send("User {} was afk for too long.".format(player.name),
                 namespace='/game', room=room)
            if player.team == "blue":
                room.scoreRed = 100
            if player.team == "red":
                room.scoreBlue = 100
            finish(room)
            return

    room.players.remove(player)
    send("User {} has disconnected.".format(player.name),
         namespace='/game', room=room)
    if len(room.players) == 0:
        rooms.pop(session['room'])
    return


@socketio.on('client_mus_turn', namespace='/game')
def client_mus_turn(data):
    if not current_user.is_authenticated:
        return False

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])
    if room is None:
        return False

    player = room.getBySid(request.sid)
    if player not in room.players or player.name != current_user.username:
        return False

    round = room.round
    if round is None:
        return False

    phase = round.getPhase()
    if phase is None:
        return False

    if not phase.isMus():
        return False

    # input validation!!!!
    # data

    if bool(data['cutMus']):
        msg = "{} cuts mus.".format(player.name)
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        mus_turn(room, True)
        return True
    msg = "{} calls mus.".format(player.name)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)

    if data['discards'] is not None:
        for discard in data['discards']:
            rank = int(discard[0])
            suit = discard[1]
            card = Card(rank, suit)
            player.addDiscard(card)
        if phase.allDiscarded():
            msg = "Everybody called mus."
            move_db(room, msg)
            send(msg, namespace='/game', room=room)
            phase.discardAll()
            mus_turn(room, False)

    return True


@socketio.on('client_game_turn', namespace='/game')
def client_game_turn(data):
    if not current_user.is_authenticated:
        return False

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])
    if room is None:
        return False

    player = room.getBySid(request.sid)
    if player not in room.players or player.name != current_user.username:
        return False

    round = room.round
    if round is None:
        return False

    phase = round.getPhase()
    if phase is None:
        return False

    if player not in phase.players:
        return False

    # A player can't bet if its not his turn
    turn = phase.getTurn()
    if player != turn:
        return False

    # input validation!!!!!
    # data

    envite = phase.lastBid

    if int(data['bid']) is not None and int(data['bid']) > 0:
        print('New envite: '+str(data['bid']))
        new_envite(room, player, envite, int(data['bid']))
        return True

    if bool(data['see']):
        if envite is None:
            return False
        print(player.name+' ve el envite.')

        msg = "{} sees the bet.".format(player.name)
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        phase.see()
        new_phase(room)
        if room.round.getPhase().isMus():
            return True
        return True

    if envite is not None:
        print('Last envite: '+str(envite.value)+', '+envite.color)
        msg = "{} doesn't see the bet.".format(player.name)
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        turn = phase.nextTurn()

        while(turn.team == envite.color):
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
    if phase.allPassed():
        new_phase(room)
        if room.round.getPhase().isMus():
            return True

    game_turn(room)
    return True


def start(room):
    room.started = datetime.utcnow()
    room.makeTeams()

    start_db(room)

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


def new_round(room):
    room.newRound()
    mano = room.getMano().name
    msg = "{} is mano this round.".format(mano)
    # move_db(room, msg)

    data = {
        "scoreBlue": room.scoreBlue,
        "scoreRed": room.scoreRed,
    }
    emit('start_round', data, namespace='/game', room=room)
    send(msg, namespace='/game', room=room)

    mus_turn(room, False)
    return


def new_phase(room):
    round = room.round
    phase = round.nextPhase()

    if phase is None:
        show_down(room)
        time.sleep(60)

        winners = round.winners
        points = round.points
        for i in range(0, 4):
            winner = winners[i]
            amount = points[i]
            if winner is None:
                pass
            elif winner.team == "blue":
                room.scoreBlue = room.scoreBlue + amount
            elif winner.team == "red":
                room.scoreRed = room.scoreRed + amount
            if room.scoreRed >= 40 or room.scoreBlue >= 40:
                finish(room)

        new_round(room)
        return

    msg = "New phase {}.".format(phase.getName())
    move_db(room, msg)
    send(msg, namespace='/game', room=room)

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


def mus_turn(room, cutMus=False):
    if cutMus:
        # phase = room.round.nextPhase()
        # if phase is None:
        #     return False
        # if not phase.isGrande():
        #     return False

        # emit('mus_turn', {"cutMus": True, "cards": None},
        #      room=room)

        new_phase(room)
        game_turn(room)
        return

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


def game_turn(room):
    phase = room.round.getPhase()
    # print('Turn: '+str(phase.turn))
    # print('Number of players: '+str(len(phase.players)))
    turn = phase.getTurn()

    blueBid, redBid = phase.getLastBids()
    phase_name = phase.getName()

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
    return


def new_envite(room, player, envite, bid):
    phase = room.round.getPhase()
    turn = phase.getTurn()

    if envite is not None:
        bid = bid + envite.value

    msg = "{player} bets {value}.".format(player=player.name, value=bid)
    move_db(room, msg)
    send(msg, namespace='/game', room=room)
    phase.envidar(player, bid)

    while(turn.team == phase.lastBid.color):
        turn = phase.nextTurn()
    game_turn(room)
    return


def show_down(room):
    playerCards = {}
    for p in room.players:
        cards = []
        for c in p.cards:
            cards.append((c.rank, c.suit))
        playerCards[p.name] = cards

    winners = room.round.winners
    points = room.round.points

    grande = ("Nobody", 0)
    chica = ("Nobody", 0)
    pares = ("Nobody", 0)
    juego = ("Nobody", 0)

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


def finish(room):
    if room.scoreBlue > room.scoreRed:
        msg = "Game ended: blue team won."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)

        for p in room.players:
            user = User.query.filter_by(username=p.name).first()
            if p.team == "blue":
                emit('finish', {"message": "You won!"}, namespace='/game', room=p.sid)
                user.wins = user.wins + 1
            elif p.team == "red":
                emit('finish', {"message": "You lost :("}, namespace='/game', room=p.sid)
                user.losses = user.losses + 1

    if room.scoreRed > room.scoreBlue:
        msg = "Game ended: red team won."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)

        for p in room.players:
            user = User.query.filter_by(username=p.name).first()
            if p.team == "red":
                emit('finish', {"message": "You won!"}, room=p.sid)
                user.wins = user.wins + 1
            elif p.team == "blue":
                emit('finish', {"message": "You lost :("}, namespace='/game', room=p.sid)
                user.losses = user.losses + 1

    room.finished = datetime.utcnow()
    game = Game.query.filter_by(room_id=room.id).first()
    game.finished = room.finished
    db.session.commit()

    print(rooms)
    rooms.pop(session['room'])
    close_room(room)
    return


def thereIsPares(room):
    phase = room.round.getPhase()

    for p in phase.players:
        print(p.name+' has pares')

    teams = phase.noPares()
    if len(teams) == 0:
        msg = "Nobody has pares."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    if "blue" not in teams:
        msg = "Only red team has pares."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    if "red" not in teams:
        msg = "Only blue team has pares."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    return True


def thereIsJuego(room):
    phase = room.round.getPhase()

    for p in phase.players:
        print(p.name+' has juego')

    teams = phase.noJuego()
    if len(teams) == 0:
        msg = "Nobody has juego."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    if "blue" not in teams:
        msg = "Only red team has juego."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    if "red" not in teams:
        msg = "Only blue team has juego."
        move_db(room, msg)
        send(msg, namespace='/game', room=room)
        time.sleep(3)
        return False

    return True


def reconnect(room, player):
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

    cards = []
    for c in player.cards:
        cards.append([c.rank, c.suit])

    data_mus = {
        "cutMus": False,
        "cards": cards
    }
    emit('mus_turn', data_mus, namespace='/game', room=player.sid)

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


def start_db(room):
    game = Game(room_id=room.id, started=room.started)
    for p in room.players:
        user = User.query.filter_by(username=p.name).first()
        game.players.append(user)
    db.session.add(game)
    db.session.commit()
    return


def move_db(room, msg):
    game = Game.query.filter_by(room_id=room.id).first()
    timestamp = datetime.utcnow()
    phase = room.round.getPhase().getName()
    message = msg

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
