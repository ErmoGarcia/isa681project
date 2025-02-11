##################################
# OBJECTS USED DURING A MUS GAME #
##################################

import secrets

from datetime import datetime, timezone


# A Spanish naipe (card)
class Card:

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

        if self.suit == 'o':
            self.suit = 'oros'
        elif self.suit == 'b':
            self.suit = 'bastos'
        elif self.suit == 'e':
            self.suit = 'espadas'
        elif self.suit == 'c':
            self.suit = 'copas'

    # The actual value of the card
    def getValue(self):
        if self.rank == 2:
            return 1
        elif self.rank == 3:
            return 10
        else:
            return self.rank
        return

    # The value of the card during Juego
    def getJuegoValue(self):
        if self.rank == 8 or self.rank == 9:
            return 10
        return self.getValue()


# A deck of Spanish cards
class Deck:

    def __init__(self):
        self.cards = []
        self.discards = []

        ranks = range(1, 11)
        suits = ['oros', 'espadas', 'copas', 'bastos']
        for suit in suits:
            for rank in ranks:
                c = Card(rank, suit)
                self.cards.append(c)

    # Shuffles the deck
    def shuffle(self):
        n = len(self.cards)
        while (n > 0):
            choice = secrets.choice(self.cards[:n])
            self.cards.remove(choice)
            self.cards.append(choice)
            n = n-1
        return

    # Reshuffle the discards when there are no cards left in the main deck
    def reshuffle(self):
        while (len(self.discards) > 0):
            card = self.discards.pop()
            self.cards.append(card)
        self.shuffle()
        return

    # Gets one card from the top of the deck
    def pop(self):
        if len(self.cards) == 0:
            self.reshuffle()
        card = self.cards.pop()
        self.discards.append(card)
        return card

    # Deal cards to all players unil thir hands are full
    def deal(self, players):
        allFull = False
        while (not allFull):
            allFull = True
            for p in players:
                if not p.fullHand():
                    allFull = False
                    card = self.pop()
                    p.addCard(card)
        return


# A player in the game
class Player:
    def __init__(self, name):
        self.name = name
        self.sid = None
        self.afk = False
        self.team = None

        self.cards = []
        self.discards = []

    # A hand is full with 4 cards
    def fullHand(self):
        if len(self.cards) == 4:
            return True
        return False

    # Adds one card to the hand
    def addCard(self, card):
        if self.fullHand():
            return
        self.cards.append(card)
        return

    # Adds one card to the list of discards
    def addDiscard(self, card):
        if len(self.discards) == 4:
            return
        self.discards.append(card)
        return

    # Drops the cards from the list of discards
    def discard(self):
        while (len(self.discards) > 0):
            discard = self.discards.pop()
            for card in self.cards:
                if discard.rank == card.rank and discard.suit == card.suit:
                    self.cards.remove(card)
        return

    # Gets the values of the cards in decreasing order
    def getGrande(self):
        values = []
        for c in self.cards:
            values.append(c.getValue())
        values.sort()
        return values

    # Gets the values of the cards in increasing order
    def getChica(self):
        values = []
        for c in self.cards:
            values.append(c.getValue())
        values.sort(reverse=True)
        return values

    # Gets a list of the cards of the hand that form pares in increasing order
    def getPares(self):
        pares = []
        for c in self.cards:
            pares.append(c.getValue())

        for i in range(0, 4):
            c = pares.pop()
            if c in pares:
                pares.insert(0, c)

        pares.sort()
        return pares

    # Gets the total juego value of the cards
    def getJuego(self):
        juego = 0
        for c in self.cards:
            juego = juego + c.getJuegoValue()
        return juego

    # The kind of pares the player has
    def hasPares(self):
        pares = len(self.getPares())
        has = None
        if pares == 2:
            has = "pares"
        if pares == 3:
            has = "medias"
        if pares == 4:
            has = "duples"
        return has

    # True if the player has juego (>30)
    def hasJuego(self):
        juego = self.getJuego()
        return juego >= 31

    # The amount of points from pares in the hand
    def pointsPares(self):
        has = self.hasPares()
        if has == "pares":
            return 1
        if has == "medias":
            return 2
        if has == "duples":
            return 3
        return 0

    # The amount of points from juego in the hand
    def pointsJuego(self):
        juego = self.getJuego()
        if juego == 31:
            return 3
        if juego in range(31, 40):
            return 2
        return 0


# An envite is how a bet is called in mus
class Envite:
    def __init__(self, player):
        self.player = player
        self.color = player.team
        self.value = 2


# Class for the mus phase
class Mus():
    def __init__(self, players, deck):
        self.players = players
        self.deck = deck

    def isMus(self):
        return True

    # Check wheter all players chose their discards or not
    def allDiscarded(self):
        allDiscarded = True
        for p in self.players:
            playerDiscarded = len(p.discards) > 0
            allDiscarded = allDiscarded and playerDiscarded
        return allDiscarded

    # Drops the selected cards from each player's hand
    def discardAll(self):
        for p in self.players:
            p.discard()
        self.deck.deal(self.players)
        return

    def getName(self):
        return "mus"


# Class from which every phase inherits
class Phase:
    def __init__(self, players, mano):
        # Envites in this round (tuples of team and quantity)
        self.lastBid = None
        self.prevBid = None

        # Players list, mano and turn
        self.players = players
        self.mano = mano
        self.turn = mano

        # The winner of the phase and the points earned
        self.winner = None
        self.points = 0

    def isMus(self):
        return False

    def isGrande(self):
        return False

    def isChica(self):
        return False

    def isPares(self):
        return False

    def isJuego(self):
        return False

    # def isPunto(self):
    #     return False

    # Checks wheter ever player passed in the phase
    def allPassed(self):
        return (self.turn == self.mano)

    # Gets the player who moves next
    def getTurn(self):
        t = self.players[self.turn]
        return t

    # Selects the next player to move
    def nextTurn(self):
        self.turn = (self.turn + 1) % 4
        return self.getTurn()

    # Adds a new envite (bet) to the table
    def envidar(self, player, n=2):
        envite = Envite(player)
        envite.value = n
        self.prevBid = self.lastBid
        self.lastBid = envite
        return envite

    # Gets the last two bets (the only ones that matter)
    def getLastBids(self):
        blueBid = 0
        redBid = 0
        if self.lastBid is not None:
            if self.lastBid.color == "blue":
                blueBid = self.lastBid.value
                if self.prevBid is not None:
                    redBid = self.prevBid.value
            if self.lastBid.color == "red":
                redBid = self.lastBid.value
                if self.prevBid is not None:
                    blueBid = self.prevBid.value
        return blueBid, redBid

    # When a team folds from a bet, the other team is the winner
    def fold(self):
        self.winner = self.lastBid.player
        self.points = 1
        if self.prevBid is not None:
            self.points = self.prevBid.value
        return self.winner, self.points

    # When a team sees a bet, the cards have to be checked to decide the winner
    def see(self):
        self.winner = self.getWinner()
        self.points = self.lastBid.value
        return self.winner, self.points

    def getWinner(self):
        return

    def getResults(self):
        return self.winner, self.points


# Class for grande phase
class Grande(Phase):

    def isGrande(self):
        return True

    # Selects the mano as the winner (in case of a tie)
    # compares his cards with the next one (rival)
    # whoever wins is the new winner
    def getWinner(self):
        winner = self.players[self.mano]
        i = (self.mano + 1) % 4
        while (i != self.mano):
            rival = self.players[i]
            if self.defeat(winner.getGrande(), rival.getGrande()):
                winner = rival
            i = (i + 1) % 4
        return winner

    # Checks if the rival defeats the current winner
    # whoever has the biggest card wins
    # if there is a tie, the next biggest cards are compared
    # if they have the same cards, the closest player to the mano wins
    def defeat(self, winner, rival):
        if len(winner) == 0:
            return False
        if len(rival) == 0:
            return False
        w = winner.pop()
        r = rival.pop()
        if r > w:
            return True
        if r == w:
            return self.defeat(winner, rival)
        return False

    def getName(self):
        return "grande"


class Chica(Phase):

    def isChica(self):
        return True

    # Selects the mano as the winner (in case of a tie)
    # compares his cards with the next one (rival)
    # whoever wins is the new winner
    def getWinner(self):
        winner = self.players[self.mano]
        i = (self.mano + 1) % 4
        while (i != self.mano):
            rival = self.players[i]
            if self.defeat(winner.getChica(), rival.getChica()):
                winner = rival
            i = (i + 1) % 4
        return winner

    # Checks if the rival defeats the current winner
    # whoever has the smallest card wins
    # if there is a tie, the next smallest cards are compared
    # if they have the same cards, the closest player to the mano wins
    def defeat(self, winner, rival):
        if len(winner) == 0:
            return False
        if len(rival) == 0:
            return False
        w = winner.pop()
        r = rival.pop()
        if r < w:
            return True
        if r == w:
            return self.defeat(winner, rival)
        return False

    # If everyone passed, whoever has the best chica wins 1 point
    # this is called "chica en paso"
    def getResults(self):
        if self.points == 0:
            self.winner = self.getWinner()
            self.points = 1
        return self.winner, self.points

    def getName(self):
        return "chica"


class Pares(Phase):

    def isPares(self):
        return True

    def nextTurn(self):
        self.turn = (self.turn + 1) % len(self.players)
        return self.getTurn()

    # Returns the team of the players that have pares
    def noPares(self):
        teams = []
        for p in self.players:
            teams.append(p.team)
        return teams

    # Removes the players that don't have pares from the phase
    def recalculatePlayers(self):
        for i in range(0, 4):
            p = self.players.pop()
            if p.hasPares() is not None:
                self.players.insert(0, p)
            if self.mano >= len(self.players):
                self.mano = 0

        self.turn = self.mano
        return

    # Selects the mano as the winner (in case of a tie)
    # compares his cards with the next one (rival)
    # whoever wins is the new winner
    def getWinner(self):
        winner = self.players[self.mano]
        i = (self.mano + 1) % len(self.players)
        while (i != self.mano):
            rival = self.players[i]
            if self.defeat(winner.getPares(), rival.getPares()):
                winner = rival
            i = (i + 1) % len(self.players)
        return winner

    # Checks if the rival defeats the current winner
    # whoever has the longest pares wins
    # if there is a tie, same as grande but only with the cards in the pares
    def defeat(self, winner, rival):
        if len(winner) == 0:
            return False
        if len(rival) == 0:
            return False
        if len(rival) > len(winner):
            return True
        if len(rival) == len(winner):
            w = winner.pop()
            r = rival.pop()
            if r > w:
                return True
            if r == w:
                return self.defeat(winner, rival)
        return False

    # Regardless of what happened during the phase,
    # the team with the best pares gets for each player
    # 1 point for 2 pares
    # 2 points for 3 pares (medias)
    # 3 points for 4 pares (duples)
    def getResults(self):
        if self.winner is None and len(self.players) > 0:
            self.winner = self.getWinner()
        for p in self.players:
            if p.team == self.winner.team:
                self.points = self.points + p.pointsPares()
        return self.winner, self.points

    def getName(self):
        return "pares"


class Juego(Phase):

    def isJuego(self):
        return True

    def nextTurn(self):
        self.turn = (self.turn + 1) % len(self.players)
        return self.getTurn()

    # Returns the team of the players that have pares
    def noJuego(self):
        teams = []
        for p in self.players:
            teams.append(p.team)
        return teams

    # Removes the players that don't have juego from the phase
    def recalculatePlayers(self):
        for i in range(0, 4):
            p = self.players.pop()
            if p.hasJuego():
                self.players.insert(0, p)
                self.mano = self.mano + 1
            if self.mano >= len(self.players):
                self.mano = 0

        self.turn = self.mano
        return

    # Selects the mano as the winner (in case of a tie)
    # compares his cards with the next one (rival)
    # whoever wins is the new winner
    def getWinner(self):
        winner = self.players[self.mano]
        i = (self.mano + 1) % len(self.players)
        while (i != self.mano):
            rival = self.players[i]
            if self.defeat(winner.getJuego(), rival.getJuego()):
                winner = rival
            i = (i + 1) % len(self.players)
        return winner

    # Checks if the rival defeats the current winner
    # whoever has a juego of 31 wins
    # if there is a tie, the closest to the mano wins
    # if nobody has 31, same thing with 32, then same thing with 40, 39, 38...
    def defeat(self, winner, rival):
        if winner > 31:
            if rival == 31:
                return True
            if rival == 32 and winner > 32:
                return True
            if rival > winner:
                return True
        return False

    # Regardless of what happened during the phase,
    # the team with the best juego gets for each player
    # 3 point for 31
    # 2 points for any other juego
    def getResults(self):
        if self.winner is None and len(self.players) > 0:
            self.winner = self.getWinner()
        for p in self.players:
            if p.team == self.winner.team:
                self.points = self.points + p.pointsJuego()
        return self.winner, self.points

    def getName(self):
        return "juego"


# class Punto(Phase):
#
#     def isPunto(self):
#         return True
#
#     def getWinner(self):
#         winner = self.players[self.mano]
#         i = (self.mano + 1) % len(self.players)
#         while(i != self.mano):
#             rival = self.players[i]
#             if self.defeat(winner.getJuego(), rival.getJuego()):
#                 winner = rival
#             i = (i + 1) % len(self.players)
#         return winner
#
#     def defeat(self, winner, rival):
#         if rival > winner:
#             return True
#         return False
#
#     def getResults(self):
#         if self.winner is None:
#             self.winner = self.getWinner()
#         self.points = self.points + 1
#         return self.winner, self.points
#
#     def getName(self):
#         return "punto"


# A game round
class Round:

    def __init__(self, players, mano):
        # Players list, mano and turn
        self.players = players
        self.mano = mano

        # Deck of cards
        self.deck = Deck()
        self.deck.shuffle()
        self.deck.deal(self.players)

        # Phases in the round
        self.phases = ['juego', 'pares', 'chica', 'grande']
        self.phase = Mus(self.players, self.deck)

        self.winners = []
        self.points = []

    # Gets the phase which the game is in
    def getPhase(self):
        return self.phase

    # Selects the next phase to play
    def nextPhase(self):
        if not self.phase.isMus():
            results = self.phase.getResults()
            self.winners.append(results[0])
            self.points.append(results[1])

        if len(self.phases) > 0:
            name = self.phases.pop()

            if name == 'juego':
                self.phase = Juego(self.players.copy(), self.mano)
                self.phase.recalculatePlayers()
            if name == 'pares':
                self.phase = Pares(self.players.copy(), self.mano)
                self.phase.recalculatePlayers()
            if name == 'chica':
                self.phase = Chica(self.players, self.mano)
            if name == 'grande':
                self.phase = Grande(self.players, self.mano)

            return self.phase
        return None

    # def thereIsPunto(self):
    #     self.phases.append(Punto(self.players, self.mano))
    #     return


# Room class: its id is randomly generated
class Room:

    def __init__(self, id):
        self.id = id

        # Times of creation, beginning and end
        self.created = datetime.now(timezone.utc)
        self.started = None
        self.finished = None

        # The mano and the round the game is in
        self.mano = secrets.randbelow(4)
        self.round = None

        # List of players in the room
        self.players = []
        self.connected = []

        # Scores
        self.scoreRed = 0
        self.scoreBlue = 0

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

    # The room has started the game
    def isStarted(self):
        if self.started is not None:
            return True
        return False

    # Adds a new player to the room
    def addPlayer(self, name):
        p = Player(name)
        if self.isAvailable:
            self.players.append(p)
        else:
            raise Exception('Game is not available.')
        return

    # Gets the names of the players in the room
    def getPlayers(self):
        names = []
        for p in self.players:
            names.append(p.name)
        return names

    # Gets a player in the room by name
    def getByName(self, name):
        for p in self.players:
            if p.name == name:
                return p
        return None

    # Gets a player in the room by sid
    def getBySid(self, sid):
        for p in self.players:
            if p.sid == sid:
                return p
        return None

    # Adds a player to the connected list and registers the sid
    def connect(self, player, sid):
        player.sid = sid
        self.connected.append(player)
        return

    # Removes a player from the connected list
    def disconnect(self, player):
        player.sid = None
        if player in self.connected:
            self.connected.remove(player)
        return

    # Creates a new round
    def newRound(self):
        for p in self.players:
            p.cards.clear()
        self.mano = (self.mano + 1) % 4
        self.round = Round(self.players, self.mano)
        return self.round

    # Gets the mano (first player to move in each phase of a round)
    def getMano(self):
        h = self.players[self.mano]
        return h

    # Divides the players in 2 teams
    def makeTeams(self):
        self.players[0].team = "blue"
        self.players[2].team = "blue"
        self.players[1].team = "red"
        self.players[3].team = "red"
        return
