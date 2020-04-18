#####################
# INFORMATION PAGES #
#####################

from flask import (
        Blueprint, request, redirect, render_template, url_for, flash
)

from game.models import User, Game, db
from flask_login import current_user

# Create info blueprint
bp = Blueprint('info', __name__, url_prefix='/info')

# Home function: get user's home page
@bp.route('/home')
def home():
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    return render_template('info/home.html')
