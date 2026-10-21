class Animation:
    """Select PNG frames with elapsed time, independent of drawing."""
    def __init__(self, folder, states):
        self.folder = folder
        self.states = states
        self.state = next(iter(states))
        self.elapsed = 0.0

    def set(self, state):
        if state != self.state:
            self.state = state
            self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt

    @property
    def image(self):
        count, fps, loop = self.states[self.state]
        index = int(self.elapsed * fps)
        index = index % count if loop else min(index, count - 1)
        return f'{self.folder}/{self.state}_{index:02d}'

