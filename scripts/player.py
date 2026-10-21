from pygame import Rect
from scripts.animation import Animation
from scripts.settings import PLAYER_SPEED, GRAVITY, JUMP_SPEED, STARTING_LIVES


class Player:
    def __init__(self, spawn=(48, 520)):
        self.rect = Rect(*spawn, 28, 40)
        self.spawn = spawn
        self.x, self.y = map(float, spawn)
        self.vy = 0.0
        self.on_ground = False
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.air_jump_used = False
        self.lives = STARTING_LIVES
        self.score = 0
        self.invulnerable = 0.0
        self.hurt_time = 0.0
        self.speed_time = 0.0
        self.double_time = 0.0
        self.shield = False
        self.facing = 1
        self.animation = Animation('player', {
            'idle': (6, 6, True), 'run': (6, 10, True),
            'jump': (2, 8, False), 'fall': (2, 6, True),
            'hurt': (2, 8, False), 'celebrate': (6, 8, True)})

    def request_jump(self):
        self.jump_buffer = 0.14

    def respawn(self):
        self.x, self.y = map(float, self.spawn)
        self.rect.topleft = self.spawn
        self.vy = 0.0
        self.on_ground = False
        self.jump_buffer = 0.0
        self.coyote = 0.0
        self.air_jump_used = False

    def update(self, dt, left, right, platforms, world_width):
        self.invulnerable = max(0, self.invulnerable - dt)
        self.hurt_time = max(0, self.hurt_time - dt)
        self.speed_time = max(0, self.speed_time - dt)
        self.double_time = max(0, self.double_time - dt)
        self.coyote = 0.10 if self.on_ground else max(0, self.coyote - dt)
        self.jump_buffer = max(0, self.jump_buffer - dt)
        jumped = False
        if self.jump_buffer > 0:
            if self.on_ground or self.coyote > 0:
                self.vy = JUMP_SPEED
                self.coyote = 0
                self.on_ground = False
                self.jump_buffer = 0
                jumped = True
            elif self.double_time > 0 and not self.air_jump_used:
                self.vy = JUMP_SPEED * 0.92
                self.air_jump_used = True
                self.jump_buffer = 0
                jumped = True
        direction = int(right) - int(left)
        if direction:
            self.facing = direction
        self.animation.folder = 'player_left' if self.facing < 0 else 'player'
        speed = PLAYER_SPEED * (1.45 if self.speed_time > 0 else 1)
        movement = direction * speed * dt
        old = self.rect.copy()
        self.x += movement
        self.rect.x = round(self.x)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if movement > 0 and old.right <= platform.left:
                    self.rect.right = platform.left
                    self.x = float(self.rect.x)
                elif movement < 0 and old.left >= platform.right:
                    self.rect.left = platform.right
                    self.x = float(self.rect.x)
        self.x = max(0, min(world_width-self.rect.width, self.x))
        self.rect.x = round(self.x)
        self.vy = min(900, self.vy + GRAVITY * dt)
        old = self.rect.copy()
        self.y += self.vy * dt
        self.rect.y = round(self.y)
        self.on_ground = False
        for platform in platforms:
            if not self.rect.colliderect(platform):
                continue
            if self.vy > 0 and old.bottom <= platform.top:
                self.rect.bottom = platform.top
                self.y = float(self.rect.y)
                self.vy = 0
                self.on_ground = True
                self.air_jump_used = False
            elif self.vy < 0 and old.top >= platform.bottom:
                self.rect.top = platform.bottom
                self.y = float(self.rect.y)
                self.vy = 0
        # Touching edges are not colliderect intersections. Keep exact support
        # across substeps instead of alternating grounded/fall every few frames.
        if not self.on_ground and self.vy >= 0:
            for platform in platforms:
                if (self.rect.bottom == platform.top
                        and self.rect.right > platform.left
                        and self.rect.left < platform.right):
                    self.y = float(platform.top - self.rect.height)
                    self.rect.y = round(self.y)
                    self.vy = 0.0
                    self.on_ground = True
                    self.air_jump_used = False
                    break
        state = 'idle'
        if self.hurt_time > 0:
            state = 'hurt'
        elif not self.on_ground:
            state = 'jump' if self.vy < 0 else 'fall'
        elif direction:
            state = 'run'
        self.animation.set(state)
        self.animation.update(dt)
        return jumped

