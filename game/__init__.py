import os

from flask import (
        Flask, render_template, render_template, flash, redirect, url_for
)

from flask_login import current_user
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

def create_app():
    # Create app object
    app = Flask(__name__, instance_relative_config=True)

    # Config from file
    app.config.from_object('config')

    # Initialize Database
    from game.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login
    from game.auth import bp, bcrypt, login_manager
    bcrypt.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(bp)

    # Initialize play
    from . import play
    app.register_blueprint(play.bp)

    # Initialize navbar
    nav = Nav()
    @nav.navigation()
    def top_nav():
        if not current_user.is_authenticated:
            return Navbar('Game',
                View('Home', 'index'),
                View('Register', 'auth.register'),
                View('Login', 'auth.login'),
            )
        return Navbar('Game',
            View('{}'.format(current_user.username), 'home'),
            View('History', 'play.history'),
            View('Logout', 'auth.logout'),
        )
    nav.init_app(app)

    # Initialize bootstrap
    Bootstrap(app)

    @app.route('/home')
    def home():
        if not current_user.is_authenticated:
            flash('You need to login first.')
            return redirect(url_for('auth.login'))
        return render_template('home.html')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
