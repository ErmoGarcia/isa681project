#####################
# INFORMATION PAGES #
#####################

from flask import (
    Blueprint, request, session, redirect, render_template, url_for, flash
)

from game.models import User, Game
from game.play import socketio

from flask_login import current_user
from flask_socketio import emit

# Create info blueprint
bp = Blueprint('info', __name__, url_prefix='/info')

# Home page
@bp.route('/home')
def home():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    return render_template('info/home.html')


# Statistics page
@bp.route('/stats')
def stats():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the statistics for the player and everyone alse
    stats = {}
    users = User.query.order_by(User.username).all()
    for user in users:
        wins = float(user.wins)
        losses = float(user.losses)
        if wins+losses != 0:
            percentage = 100*wins/(wins+losses)
        else:
            percentage = 0
        stats[user.username] = (wins, losses, percentage)

    return render_template('info/stats.html', stats=stats)


# History page
@bp.route('/history')
def history():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets every game in history
    games = Game.query.filter(Game.finished != None).all()
    return render_template('info/history.html', games=games)


# History of a game page
@bp.route('/gamehistory/<id>')
def gamehistory(id):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Stores the game id and the current move in the players session
    session['game'] = id
    session['move'] = 0

    return render_template('info/gamehistory.html')


# When a player connects to a game history page
@socketio.on('connect', namespace='/history')
def connection():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the game id and the current move from the session
    # loads the from the DB
    game = Game.query.filter_by(room_id=session['game']).first()
    move = game.moves[session['move']]
    load_move(game, move)
    return


# When a user clicks next
@socketio.on('next', namespace='/history')
def next(data):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the game id and the current move from the session
    # loads the from the DB
    game = Game.query.filter_by(room_id=session['game']).first()
    if session['move'] == len(game.moves) - 1:
        return

    # Gets the following move
    session['move'] = session['move'] + 1
    move = game.moves[session['move']]

    load_move(game, move)
    return


# When a user clicks previous
@socketio.on('prev', namespace='/history')
def prev(data):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the game id and the current move from the session
    # loads the from the DB
    game = Game.query.filter_by(room_id=session['game']).first()
    if session['move'] == 0:
        return

    # Gets the previous move
    session['move'] = session['move'] - 1
    move = game.moves[session['move']]

    load_move(game, move)
    return


# Loads a move from the DB
def load_move(game, move):
    phase = move.phase
    message = move.message
    scoreBlue = move.scoreBlue
    scoreRed = move.scoreRed

    players = []
    for p in game.players:
        players.append(p.username)

    cards = [move.getPlayer1Cards(), move.getPlayer2Cards(),
             move.getPlayer3Cards(), move.getPlayer4Cards()]

    # Informs the user of the players names, the phase, the scores,
    # the explainatory message if the move, and the cards for all players
    data = {
        "players": players,
        "phase": phase,
        "message": message,
        "scoreBlue": scoreBlue,
        "scoreRed": scoreRed,
        "cards": cards
    }
    emit("move", data, namespace='/history', room=request.sid)
    return
