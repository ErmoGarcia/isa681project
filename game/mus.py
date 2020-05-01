import secrets

from datetime import datetime


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def getValue(self):
        if self.rank == 2:
            return 1
        elif self.rank == 3:
            return 10
        else:
            return self.rank
        return

    def getJuegoValue(self):
        if self.rank == 8 or self.rank == 9:
            return 10
        return self.getValue()


class Deck:
    def __init__(self):
        self.cards = []

        ranks = range(1, 11)
        suits = ['Oros', 'Espadas', 'Copas', 'Bastos']
        for suit in suits:
            for rank in ranks:
                c = Card(rank, suit)
                self.cards.append(c)

    def shuffle(self):
        n = len(self.cards)
        while(n > 0):
            choice = secrets.choice(self.cards[:n])
            self.cards.remove(choice)
            self.cards.append(choice)
            n = n-1
        return


class Player:
    def __init__(self, name):
        self.name = name
        self.sid = None
        self.afk = False

# Room class: its id is the username of its creator


class Round:

    def __init__(self, players, hand):
        self.phases = ["mus", "grande", "chica", "pares", "juego", "punto"]
        self.phase = 0
        self.players = players
        self.hand = hand
        self.turn = hand

    def getTurn(self):
        t = self.players[self.turn]
        return t

    def nextTurn(self):
        self.turn = (self.turn + 1) % 4
        if self.turn == self.hand:
            self.phase = (self.phase + 1) % 6
        return self.getTurn()

    def getPhase(self):
        return self.phases[self.phase]

    def nextPhase(self):
        self.phase = (self.phase + 1) % 6
        self.turn = self.hand
        return self.phases[self.phase]


class Room:

    def __init__(self, id):
        self.id = id

        self.created = datetime.utcnow()
        self.started = None
        self.finished = None

        self.hand = secrets.randbelow(4)
        self.round = None

    # List of players in the room
    players = []
    connected = []

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

    def isStarted(self):
        if self.started is not None:
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

    def connect(self, player, sid):
        player.sid = sid
        self.connected.append(player)
        return

    def disconnect(self, player):
        player.sid = None
        if player in self.connected:
            self.connected.remove(player)
        return

    def newRound(self):
        self.hand = (self.hand + 1) % 4
        self.round = Round(self.players, self.hand)
        return self.round

    def getHand(self):
        h = self.players[self.hand].name
        return h
