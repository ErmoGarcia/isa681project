import time
import json
from datetime import datetime

from flask import session, request

from game.play import socketio, rooms
from game.mus import Card

from flask_socketio import emit, send, join_room, leave_room, close_room
from flask_login import current_user


def start(room):
    room.started = datetime.utcnow()
    room.makeTeams()

    for p in room.players:
        data = {
            "players": room.getPlayers(),
            "player_number": room.players.index(p)
        }
        emit('start_game', json.dumps(data), room=p.sid)
    new_round(room)
    return


def new_round(room):
    room.newRound()
    scoreBlue = room.scoreBlue
    scoreRed = room.scoreRed
    mano = room.getMano()

    data = {
        "scoreBlue": scoreBlue,
        "scoreRed": scoreRed,
        "mano": mano
    }
    emit('start_round', json.dumps(data), room=room)

    mus_turn(room, False)
    return


def new_phase(room):
    round = room.round
    phase = round.phase

    phase = round.nextPhase()
    if phase.isPares() and phase.noPares()[0]:
        if phase.noPares()[1] is not None:
            send("Only {} team has pares.".format(phase.noPares()[1]),
                 room=room)
        else:
            send("Nobody has pares.", room=room)
        phase = round.nextPhase()

    if phase.isJuego() and phase.noJuego()[0]:
        if phase.noJuego[1]:
            send("Nobody has juego.", room=room)
            round.thereIsPunto()
        send("Only {} team has juego.".format(phase.noJuego()[2]), room=room)
        phase = round.nextPhase()
    if phase is None:
        show_down(room)
        time.sleep(30)

        results = round.results
        for r in results:
            winner = r[0]
            points = r[1]
            if winner is None:
                pass
            if winner.team == "blue":
                room.scoreBlue = room.scoreBlue + points
            if winner.team == "red":
                room.scoreRed = room.scoreRed + points
            if room.scoreRed >= 40 or room.scoreBlue >= 40:
                finish(room)

        new_round(room)
        return
    game_turn(room)
    return


def mus_turn(room, cutMus=False):
    if cutMus:
        emit('mus_turn', json.dumps({"cutMus": True, "cards": None}),
             room=room)

        phase = room.round.nextPhase()
        if phase is None:
            return False
        if not phase.isGrande():
            return False

        data_mus = {
            "cutMus": True,
            "cards": None
        }
        emit('mus_turn', json.dumps(data_mus), room=room)

        game_turn(room)
        return

    for p in room.players:
        cards = []
        for c in p.cards:
            cards.append((c.rank, c.suit))

        data_mus = {
            "cutMus": False,
            "cards": cards
        }
        emit('mus_turn', json.dumps(data_mus), room=p.sid)

    return


def game_turn(room):
    phase = room.round.getPhase()
    turn = phase.getTurn()

    blueBid = None
    redBid = None
    if phase.lastBid is not None:
        if phase.lastBid.color == "blue":
            blueBid = phase.lastBid.value
            redBid = phase.prevBid.value
        if phase.lastBid.color == "red":
            redBid = phase.lastBid.value
            blueBid = phase.prevBid.value

    if phase.isGrande():
        phase_name = "grande"
    if phase.isChica():
        phase_name = "chica"
    if phase.isPares():
        phase_name = "pares"
    if phase.isJuego():
        phase_name = "juego"
    if phase.isPunto():
        phase_name = "punto"

    data = {
        "phase": phase_name,
        "blueBid": blueBid,
        "redBid": redBid,
        "turn": turn.name
    }

    send("{} speaks.".format(turn.name), room=room)
    emit('game_turn', json.dumps(data), room=room)
    return


def new_envite(room, player, envite, bid):
    phase = room.round.getPhase()
    turn = phase.getTurn()

    if envite is not None and bid < envite.value:
        return False

    send("{player} bets {value}.".format(
        player=player.name, value=bid
    ), room=room)
    phase.envidar(player, bid)

    while(turn.team == phase.lastBid.color):
        turn = phase.nexTurn()
    game_turn(room)
    return


def show_down(room):
    playerCards = {}
    for p in room.players:
        cards = []
        for c in p.cards:
            cards.append((c.rank, c.suit))
        playerCards[p.name] = cards

    winners = round.room.winners
    points = round.room.points
    grande = (winners[0].name, points[0])
    chica = (winners[1].name, points[1])
    pares = (winners[2].name, points[2])
    juego = (winners[3].name, points[3])
    if len(winners) > 4:
        punto = (winners[4].name, points[1])
    else:
        punto = None

    data = {
        "playerCards": playerCards,
        "grande": grande,
        "chica": chica,
        "pares": pares,
        "juego": juego,
        "punto": punto
    }

    emit('show_down', json.dumps(data), room=room)
    return


def finish(room):
    if room.scoreBlue > room.scoreRed:
        send("Game ended: blue team won.", room=room)
    if room.scoreRed > room.scoreBlue:
        send("Game ended: red team won.", room=room)

    room.finished = datetime.utcnow()
    rooms.pop(room.id)
    close_room(room)
    return


# Socket connection event
@socketio.on('connect')
def new_connection():
    if not current_user.is_authenticated:
        return False

    # Gets the room where the client is at form the session
    room = rooms.get(session['room'])

    # Gets the Player from the Room
    player = room.getByName(current_user.username)
    printPlayers(room)

    # Does nothing if the player has not already been added to the room
    # or if the player is already connected
    if player is None or player in room.connected:
        return False

    # Stores the connection SID for the player
    room.connect(player, request.sid)
    print('connected: '+player.name)

    # Adds the player to the room channel (to receive events)
    join_room(room)

    # If player was just afk, do nothing else
    if room.isStarted():
        return True

    # Sends event 'user has connected' to everyone in the room
    send("User {} has connected.".format(player.name), room=room)

    if room.isFull():
        start(room)


@socketio.on('disconnect')
def new_disconnection():

    # Gets the room where the client was at form the session
    room = rooms.get(session['room'])
    if room is None:
        raise Exception('No room available for disconnection.')

    player = room.getBySid(request.sid)
    if player is None:
        raise Exception(
            'Players should be in the game before they disconnect.'
        )

    printPlayers(room)

    room.disconnect(player)
    leave_room(room)

    if room.isStarted():
        time.sleep(60)

        if player not in room.connected:
            print('game over')
            send("User {} was afk for too long.".format(player.name),
                 room=room)
            if player.team == "blue":
                room.scoreRed = 100
            if player.team == "red":
                room.scoreBlue = 100
            finish(room)
            return

    room.players.remove(player)
    send("User {} has disconnected.".format(player.name), room=room)
    print('disconnected: '+player.name)
    return


def printPlayers(room):
    print('players:')
    for p in room.players:
        print('- '+p.name)
    return


@socketio.on('client_mus_turn')
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
    data = json.loads(data)

    if data.cutMus:
        send("{} cuts mus.".format(player.name), room=room)
        mus_turn(room, True)
        return True
    send("{} calls mus.".format(player.name), room=room)

    if data.discards is not None:
        for discard in data.discards:
            card = Card(data.discards[0], data.discards[1])
            player.addDiscard(card)
        if phase.allDiscarded():
            send("Everybody called mus.", room=room)
            phase.discardAll()
            mus_turn(room, False)

    return True


@socketio.on('client_game_turn')
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
    data = json.loads(data)

    envite = phase.lastBid

    if data.bid is not None and data.bid > 0:
        new_envite(room, player, envite, data.bid)
        return True

    if envite is not None:
        if data.see:
            send("{} sees the bet.".format(player.name), room=room)
            phase.see()
            new_phase(room)
            return True

        send("{} passes.".format(player.name), room=room)
        turn = phase.nextTurn()

        while(turn.team == envite.color):
            if turn == envite.player:
                phase.fold()
                new_phase(room)
            turn = phase.nextTurn()
        game_turn(room)
        return

    send("{} passes.".format(player.name), room=room)
    if phase.allPassed():
        new_phase()

    game_turn(room)
    return True
