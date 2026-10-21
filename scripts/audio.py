from scripts.settings import TRACKS


class Audio:
    """Use only the sound and music services supplied by Pygame Zero."""
    def __init__(self, sounds, music):
        self.sounds = sounds
        self.music = music
        self.track = 0
        self.music_enabled = True
        self.sfx_enabled = True
        self.started = False

    def start(self):
        self.started = True
        self.music.set_volume(0.32)
        if self.music_enabled:
            self.music.play(TRACKS[self.track][0])

    def select(self, delta):
        self.track = (self.track + delta) % len(TRACKS)
        self.start()
        self.play('click')

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.start()
        else:
            self.music.stop()

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
        self.play('click')

    def play(self, name):
        if self.sfx_enabled:
            getattr(self.sounds, name).play()

