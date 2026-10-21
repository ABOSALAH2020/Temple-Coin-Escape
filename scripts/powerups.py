from pygame import Rect
from scripts.animation import Animation
from scripts.settings import MAX_LIVES


class PowerUp:
    def __init__(self, x, y, kind):
        self.rect = Rect(x, y, 28, 28)
        self.kind = kind
        self.animation = Animation('powerups', {kind: (2, 4, True)})

    def apply(self, player):
        if self.kind == 'speed':
            player.speed_time = 7.0
        elif self.kind == 'shield':
            player.shield = True
        elif self.kind == 'double_jump':
            player.double_time = 10.0
        elif self.kind == 'extra_life':
            player.lives = min(MAX_LIVES, player.lives+1)

