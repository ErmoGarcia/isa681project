###################
# DATABASE MODELS #
###################

from flask_sqlalchemy import SQLAlchemy

# Estension: sqlalchemy
db = SQLAlchemy()


# Many to many relation between users and games
players = db.Table('players',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
        db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True),
        db.Column('win', db.Boolean)
)


# User model for the db
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(25), nullable=False)

    # Login extension requires these functions:

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.username


# Game model for the db
class Game(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True)
    started = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)
    players = db.relationship('User', secondary=players, lazy='subquery',
            backref=db.backref('games', lazy=True))

    def __repr__(self):
        return '<Game %r>' % self.id
