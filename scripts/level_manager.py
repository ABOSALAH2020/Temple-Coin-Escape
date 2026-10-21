from scripts.level import Level


class LevelManager:
    COUNT = 3
    def __init__(self):
        self.index = 0
        self.level = Level(0)

    def restart(self):
        self.index = 0
        self.level = Level(0)

    def advance(self):
        if self.index >= self.COUNT - 1:
            return False
        self.index += 1
        self.level = Level(self.index)
        return True
