from pygame import Rect
from scripts.animation import Animation


class Enemy:
    def __init__(self, x, y, width, height):
        self.rect = Rect(x, y, width, height)
        self.x = float(x)
        self.y = float(y)
        self.timer = 0.0


class Slime(Enemy):
    def __init__(self, x, top, patrol_left, patrol_right, speed=64):
        super().__init__(x, top-24, 30, 24)
        self.left, self.right = patrol_left, patrol_right
        self.direction = 1
        self.rest = 0.5
        self.speed = speed
        self.animation = Animation('enemies/slime', {'idle': (2, 4, True), 'move': (4, 8, True)})

    def update(self, dt):
        if self.rest > 0:
            self.rest -= dt
            self.animation.set('idle')
        else:
            self.x += self.speed * self.direction * dt
            if self.x <= self.left:
                self.x, self.direction, self.rest = float(self.left), 1, 0.6
            elif self.x + self.rect.width >= self.right:
                self.x, self.direction, self.rest = float(self.right-self.rect.width), -1, 0.6
            self.rect.x = round(self.x)
            self.animation.set('move')
        self.animation.folder = 'enemies/slime_left' if self.direction < 0 else 'enemies/slime'
        self.animation.update(dt)


class Fireball:
    def __init__(self, x, y, direction, speed=185):
        self.x, self.y = float(x), float(y)
        self.direction = direction
        self.speed = speed
        self.life = 3.0
        self.rect = Rect(round(x), round(y), 14, 12)
        self.animation = Animation('effects', {'fireball_left' if direction < 0 else 'fireball': (4, 12, True)})

    def update(self, dt):
        self.x += self.direction * self.speed * dt
        self.life -= dt
        self.rect.topleft = round(self.x), round(self.y)
        self.animation.update(dt)


class Bat(Enemy):
    def __init__(self, x, y, shot_interval=2.6, projectile_speed=185):
        super().__init__(x, y, 30, 22)
        self.base_y = y
        self.base_x = x
        self.shot_interval = shot_interval
        self.projectile_speed = projectile_speed
        self.cooldown = 1.8
        self.windup = 0.0
        self.direction = -1
        self.animation = Animation('enemies/bat', {'idle': (2, 4, True), 'fly': (6, 10, True), 'shoot': (2, 8, False)})

    def update(self, dt, player):
        import math
        self.timer += dt
        near = abs(player.centerx-self.rect.centerx) < 450
        self.y = self.base_y + math.sin(self.timer*2.4)*18
        self.x = self.base_x + math.sin(self.timer*1.3)*25
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)
        projectile = None
        if self.windup > 0:
            self.windup -= dt
            self.animation.set('shoot')
            if self.windup <= 0:
                projectile = Fireball(self.rect.centerx, self.rect.centery, self.direction,self.projectile_speed)
                self.cooldown = self.shot_interval
        elif near:
            self.cooldown -= dt
            self.animation.set('fly')
            if self.cooldown <= 0:
                self.direction = -1 if player.centerx < self.rect.centerx else 1
                self.windup = 0.45
        else:
            self.animation.set('idle')
        if self.windup <= 0 and projectile is None:
            self.direction = (-1 if player.centerx < self.rect.centerx else 1) if near else (1 if math.cos(self.timer*1.3) >= 0 else -1)
        self.animation.folder = 'enemies/bat_left' if self.direction < 0 else 'enemies/bat'
        self.animation.update(dt)
        return projectile

