from flask import (
    Flask, render_template, redirect, url_for
)

from flask_login import current_user
from flask_bootstrap import Bootstrap4

from game.models import db
from game.auth import bp, bcrypt, login_manager

from . import play
from . import info


def create_app():
    # Create app object
    app = Flask(__name__, instance_relative_config=True)

    # Config from file
    app.config.from_object('config')

    # Initialize Database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login
    bcrypt.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(bp)

    # Initialize play
    play.socketio.init_app(app)
    app.register_blueprint(play.bp)

    # Initialize info
    app.register_blueprint(info.bp)

    # Initialize bootstrap
    Bootstrap4(app)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('info.home'))
        return render_template('index.html')

    return app
