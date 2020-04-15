import datetime

from flask import (
        Blueprint, request, redirect, render_template, url_for, flash
)

from game.models import User, Game, played_on, db
from flask_login import current_user

bp = Blueprint('play', __name__, url_prefix='/play')

@bp.route('/newgame', methods=['GET', 'POST'])
def newgame():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        game = Game(created = datetime.datetime.now())
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
