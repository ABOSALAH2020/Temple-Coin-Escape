from pygame import Rect
from scripts.animation import Animation


class Coin:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 20, 20)
        self.animation = Animation('items', {'coin': (8, 10, True)})
        self.animation.elapsed = x * 0.001


class Spike:
    def __init__(self, x):
        self.rect = Rect(x+5, 544, 22, 16)


class ExitDoor:
    def __init__(self, x):
        self.rect = Rect(x, 500, 45, 60)

    def is_unlocked(self, score, required):
        return score >= required

