from functools import wraps

from flask import(
        Blueprint, request, redirect, render_template, url_for, flash
)

from game.forms import LoginForm, RegisterForm
from game.models import User, db

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required

bp = Blueprint('auth', __name__, url_prefix='/auth')

bcrypt = Bcrypt()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(username=request.form['username'], password=
                    bcrypt.generate_password_hash(request.form['password']),
                    email=request.form['email'])
            db.session.add(user)
            db.session.commit()
            flash('New user registered. Try to login.')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form = form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=request.form['username']).first()
            if user is not None and bcrypt.check_password_hash(user.password, 
                    request.form['password']):
                login_user(user)
                flash('You were just logged in!')
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials. Please try again.'
    return render_template('auth/login.html', form = form, error = error)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were just logged out!')
    return redirect(url_for('index'))
