##################
# AUTHENTICATION #
##################

import re

from flask import (
    Blueprint, request, redirect, render_template, url_for, flash
)

from game.forms import LoginForm, RegisterForm
from game.models import User, db

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user

# Create the auth blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Extensions: bcrypt and login manager
bcrypt = Bcrypt()
login_manager = LoginManager()

# Load user function (from login extension)
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

# Register function: user registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Imports the register form from the file forms.py
    form = RegisterForm(request.form)

    # When the form is submitted:
    if request.method == 'POST':
        if form.validate_on_submit():

            # Input that needs to be validated
            name = request.form['username']
            passwd = request.form['password']
            email = request.form['email']

            # Check that the username is a alphanumeric string
            # between 4 and 25 characters long (whitelist)
            if not re.search("^[0-9a-zA-Z]{4,25}$", name):
                flash('Username must contain 4-25 alphanumeric characters.')
                return redirect(url_for('auth.register'))

            # Check that the password is a alphanumeric string
            # between 6 and 40 characters long (whitelist)
            if not re.search("^[0-9a-zA-Z]{6,40}$", passwd):
                flash('Password must contain 6-40 alphanumeric characters.')
                return redirect(url_for('auth.register'))

            # Check that the email is a alphanumeric string
            # between 1 and 50 characters long (whitelist)
            # this one is less restrictive because email is never used
            if not re.search("^[0-9a-zA-Z@.]{5,50}$", email):
                flash('Wrong email.')
                return redirect(url_for('auth.register'))

            # Check that the username is not registered already
            exists = db.session.query(User.id).filter_by(username=name).scalar()
            if exists is not None:
                flash('Username already in use.')
                return redirect(url_for('auth.register'))

            # Check that the email is not registered already
            exists = db.session.query(User.id).filter_by(email=email).scalar()
            if exists is not None:
                flash('Email already in use.')
                return redirect(url_for('auth.register'))

            # User is registered in the DB
            user = User(username=name,
                        password=bcrypt.generate_password_hash(passwd),
                        email=email, wins=0, losses=0)
            db.session.add(user)
            db.session.commit()

            # Redirect to login
            flash('New user registered. Try to login.')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# Login function: user login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # Imports the login form from the file forms.py
    form = LoginForm(request.form)

    # When the form is submitted:
    if request.method == 'POST':
        if form.validate_on_submit():

            # Input that needs to be validated
            name = request.form['username']
            passwd = request.form['password']

            # Check that the username is a alphanumeric string
            # between 4 and 25 characters long (whitelist)
            if not re.search("^[0-9a-zA-Z]{4,25}$", name):
                flash('Invalid credentials. Please try again.')
                return redirect(url_for('auth.login'))

            # Check that the password is a alphanumeric string
            # between 6 and 40 characters long (whitelist)
            if not re.search("^[0-9a-zA-Z]{6,40}$", passwd):
                flash('Invalid credentials. Please try again.')
                return redirect(url_for('auth.login'))

            # Introduced user is searched in the DB
            user = User.query.filter_by(
                username=name
            ).first()

            # Check if username and password are correct
            if user is not None and bcrypt.check_password_hash(
                    user.password,
                    passwd
            ):

                # Login user (with login extension)
                login_user(user)

                # Redirect to home
                flash('You were just logged in!')
                return redirect(url_for('info.home'))

            else:
                error = 'Invalid credentials. Please try again.'

    return render_template('auth/login.html', form=form, error=error)


# Loguot function: user logout
@bp.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    # Logout with extension
    logout_user()
    flash('You were just logged out!')
    return redirect(url_for('index'))
