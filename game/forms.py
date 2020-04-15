from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()], render_kw={"placeholder" : "username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder" : "password"})

class RegisterForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()], render_kw={"placeholder" : "username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder" : "password"})
