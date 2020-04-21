import secrets

from datetime import datetime

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def getValue(self):
        if rank == 2:
            return 1
        elif rank == 3:
            return 10
        else:
            return self.rank

class Deck:
    def __init__(self):
        self.cards = []

        ranks = range(1,11)
        suits = ['Oros','Espadas','Copas','Bastos']
        for suit in suits:
            for rank in ranks:
                c = Card(rank, suit)
                self.cards.append(c)

    def shuffle(self):
        n = len(self.cards)
        while(n > 0):
            choice = secret.choice(self.cards[:n])
            self.cards.append(self.cards.pop(choice))
            n = n-1
        return

class Player:
    def __init__(self, name):
        self.name = name
        self.sid = None
        self.afk = False

    def connected(self, sid):
        self.sid = sid

    def disconnected(self):
        self.sid = None
        self.afk = True

# Room class: its id is the username of its creator
class Room:

    def __init__(self, id):
        self.id = id;
        self.created = datetime.utcnow()
        self.started = None
        self.finished = None

    # List of players in the room
    players = []
    afklist = []

    # Deck of cards
    deck = Deck()

    # The room is full if it has 4 players
    def isFull(self):
        if len(self.players) == 4:
            return True
        return False

    # The room is available if it has less than 4 players and has not started
    def isAvailable(self):
        if len(self.players) < 4 and self.started is None:
            return True
        return False

    def addPlayer(self, name):
        p = Player(name)
        if self.isAvailable:
            self.players.append(p)
        else:
            raise Exception('Game is not available.')
        return

    def getPlayers(self):
        names = []
        for p in self.players:
            names.append(p.name)
        return names

    def getByName(self, name):
        for p in self.players:
            if p.name == name:
                return p
        return None

    def getBySid(self, sid):
        for p in self.players:
            if p.sid == sid:
                return p
        return None
