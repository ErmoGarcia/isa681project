import os

from flask import (
        Flask, render_template, render_template, flash, redirect, url_for
)

from flask_login import current_user

def create_app():
    # Create app object
    app = Flask(__name__, instance_relative_config=True)

    # Config from file
    app.config.from_object('config.DevConfig')

    # Initialize Database
    from game.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from game.auth import bp, bcrypt, login_manager
    bcrypt.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(bp)

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
