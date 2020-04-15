from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()], 
            render_kw={"placeholder" : "username"})
    password = PasswordField('Password', validators=[DataRequired()], 
            render_kw={"placeholder" : "password"})

class RegisterForm(FlaskForm):
    username = TextField('Username', 
            validators=[DataRequired(), Length(min=4, max=25)],
            render_kw={"placeholder" : "username"})
    email = TextField('Email', validators=
            [DataRequired(), Email(message=None), Length(min=6, max=40)],
            render_kw={"placeholder" : "email"})
    password = PasswordField('Password', 
            validators=[DataRequired(), Length(min=6, max=25)], 
            render_kw={"placeholder" : "password"})
    confirm = PasswordField("Repeat password", validators=[DataRequired(), 
        EqualTo("password", message='Passwords must be equal')],
        render_kw={"placeholder" : "confirm password"})
