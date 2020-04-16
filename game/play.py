from datetime import datetime

from flask import (
        Blueprint, request, redirect, render_template, url_for, flash
)

from game.models import User, Game, players, db
from flask_login import current_user
from flask_socketio import SocketIO, emit

bp = Blueprint('play', __name__, url_prefix='/play')

socketio = SocketIO()

@bp.route('/newgame', methods=['GET', 'POST'])
def newgame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        game = Game(created = datetime.utcnow())
        game.players.append(current_user)
        db.session.add(game)
        db.session.commit()
        flash('New game created ({}).'.format(game.created))
        return redirect(url_for('home'))
    return render_template('play/newgame.html')


@bp.route('/history')
def history():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))
    games = Game.query.order_by(Game.created).all()
    return render_template('play/history.html', games = games)

@socketio.on('connect')
def new_connection():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return False
    print('New connection')
    msg = 'User {} has connected.'.format(current_user.username)
    emit("new_connection", {"msg" : msg}, broadcast=True)

@socketio.on('disconnect')
def new_disconnection():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return False
    print('New connection')
    msg = 'User {} has disconnected.'.format(current_user.username)
    emit("new_disconnection", {"msg" : msg}, broadcast=True)
