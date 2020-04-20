from datetime import datetime

# Room class: its id is the username of its creator
class Room:

    def __init__(self, id):
        self.id = id;
        self.created = datetime.utcnow()
        self.started = None
        self.finished = None

    # List of players in the room
    players = []

    # The room is full if it has 4 players
    def is_full(self):
        if len(self.players) == 4:
            return True
        return False

    # The room is available if it has less than 4 players and has not started
    def is_available(self):
        if len(self.players) < 4 and self.started is None:
            return True
        return False
