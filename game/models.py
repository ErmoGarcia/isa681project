###################
# DATABASE MODELS #
###################

from flask_sqlalchemy import SQLAlchemy

# Estension: sqlalchemy
db = SQLAlchemy()


players = db.Table('players',
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                             primary_key=True),
                   db.Column('game_id', db.Integer, db.ForeignKey('game.id'),
                             primary_key=True)
                   )


# User model for the db
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(25), nullable=False)

    wins = db.Column(db.Integer, nullable=False)
    losses = db.Column(db.Integer, nullable=False)

    games = db.relationship('Game', secondary=players,
                            backref=db.backref('players', lazy='subquery'),
                            lazy=True)

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
    room_id = db.Column(db.String(30), unique=True, nullable=False)
    started = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)

    moves = db.relationship('Move', backref='game', lazy=True)

    def __repr__(self):
        return '<Game %r>' % self.id


class Move(db.Model):
    __tablename__ = "move"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    phase = db.Column(db.String(6), nullable=False)
    message = db.Column(db.String(255), nullable=False)

    scoreBlue = db.Column(db.Integer, nullable=False)
    scoreRed = db.Column(db.Integer, nullable=False)

    card11 = db.Column(db.String(7), nullable=False)
    card12 = db.Column(db.String(7), nullable=False)
    card13 = db.Column(db.String(7), nullable=False)
    card14 = db.Column(db.String(7), nullable=False)

    card21 = db.Column(db.String(7), nullable=False)
    card22 = db.Column(db.String(7), nullable=False)
    card23 = db.Column(db.String(7), nullable=False)
    card24 = db.Column(db.String(7), nullable=False)

    card31 = db.Column(db.String(7), nullable=False)
    card32 = db.Column(db.String(7), nullable=False)
    card33 = db.Column(db.String(7), nullable=False)
    card34 = db.Column(db.String(7), nullable=False)

    card41 = db.Column(db.String(7), nullable=False)
    card42 = db.Column(db.String(7), nullable=False)
    card43 = db.Column(db.String(7), nullable=False)
    card44 = db.Column(db.String(7), nullable=False)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def getPlayer1Cards(self):
        return [self.card11, self.card12, self.card13, self.card14]

    def getPlayer2Cards(self):
        return [self.card21, self.card22, self.card23, self.card24]

    def getPlayer3Cards(self):
        return [self.card31, self.card32, self.card33, self.card34]

    def getPlayer4Cards(self):
        return [self.card41, self.card42, self.card43, self.card44]

    def __repr__(self):
        return '<Move %r>' % self.id
