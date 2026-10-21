class Camera:
    def __init__(self):
        self.x = 0.0

    def update(self, player, world_width, dt):
        desired = max(0, min(world_width - 800, player.centerx - 360))
        self.x += (desired - self.x) * min(1, dt * 8)

    def reset(self):
        self.x = 0.0

