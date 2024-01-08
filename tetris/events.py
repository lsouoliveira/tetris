from tetris.entities.pieces import PieceType


class Event:
    pass


class Observable:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event: Event):
        for observer in self.observers:
            observer(event)


class PieceAddedEvent(Event):
    def __init__(self, piece_type: PieceType):
        self.piece_type = piece_type


class GameOverEvent(Event):
    pass


class LinesClearedEvent(Event):
    def __init__(self, number_of_lines: int):
        self.number_of_lines = number_of_lines
