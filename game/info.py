#####################
# INFORMATION PAGES #
#####################

from flask import (
    Blueprint, request, session, redirect, render_template, url_for, flash
)

from game.models import User, Game, Move, db
from game.play import socketio

from flask_login import current_user
from flask_socketio import emit

# Create info blueprint
bp = Blueprint('info', __name__, url_prefix='/info')

# Home function: get user's home page
@bp.route('/home')
def home():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    return render_template('info/home.html')


@bp.route('/stats')
def stats():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    stats = {}
    users = User.query.order_by(User.username).all()
    for user in users:
        wins = float(user.wins)
        losses = float(user.losses)
        percentage = 100*wins/(wins+losses)
        stats[user.username] = (wins, losses, percentage)

    return render_template('info/stats.html', stats=stats)


# History function
@bp.route('/history')
def history():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # INCOMPLETE
    # Searches for games in the database
    user = User.query.filter_by(username=current_user.name).first()
    games = user.games
    return render_template('info/history.html', games=games)


# History function
@bp.route('/history/<id>')
def game_history(id):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    game = Game.query.filter_by(room_id=id).first()
    session['game'] = game
    session['move'] = -1

    return render_template('info/history.html')


@socketio.on('next')
def next(data):
    game = session['game']
    session['move'] = session['move'] + 1
    move = game.moves[session['move']]
    load_move(game, move)
    return


@socketio.on('prev')
def prev(data):
    game = session['game']
    session['move'] = session['move'] - 1
    move = game.moves[session['move']]
    load_move(game, move)
    return


def load_move(game, move):
    phase = move.phase
    message = move.message
    scoreBlue = move.scoreBlue
    scoreRed = move.scoreRed

    players = []
    for p in game.players:
        players.append(p.username)

    cards = list(move.getPlayer1Cards(), move.getPlayer2Cards(),
                 move.getPlayer3Cards(), move.getPlayer4Cards())

    data = {
        players: players,
        phase: phase,
        message: message,
        scoreBlue: scoreBlue,
        scoreRed: scoreRed,
        cards: cards
    }
    emit("move", data, request.sid)
