# Temple Coin Escape

A pixel-art platformer featuring three temple environments, animated enemies, collectible coins, and power-ups.

## Requirements

- Python 3
- Pygame Zero

Install Pygame Zero:

```bash
python -m pip install pgzero
```

## Running the Game

On Windows, double-click **Start Game.bat**.

Alternatively, open a terminal in the game folder and run:

```bash
python game.py
```

Keep the `scripts`, `images`, `music`, and `sounds` folders alongside `game.py`.

## Controls

| Key | Action |
|---|---|
| Left / Right or A / D | Move |
| Space / Up / W | Jump |
| Esc | Pause or resume |
| M | Toggle music |
| Enter | Start or continue to the next level |
| Enter / R | Restart after winning or losing |

Use the mouse to interact with menu buttons. Music and sound effects can be enabled or disabled separately.

## Objective

Collect enough coins to unlock the exit at the right end of each level. Complete all three temples to win.

| Level | Environment | Difficulty | Required Coins |
|---|---|---|---|
| The Jungle Trail | Daytime jungle | Easy | 8 of 10 |
| The Twilight Ruins | Temple ruins at sunset | Medium | 9 of 11 |
| The Ember Sanctum | Volcanic temple | Hard | 11 of 13 |

Later levels introduce faster enemies, more frequent projectiles, additional hazards, and narrower platforms.

## Health and Progress

You start with three hearts and can hold up to five.

Taking damage returns you to the beginning of the current level, while keeping the coins collected during that attempt. Brief protection prevents repeated damage immediately after respawning.

Hearts and total score carry over between levels. Each new level starts with a fresh level coin counter.

## Power-Ups

- **Shield:** Absorbs one hit. A hollow aura appears around the player while active.
- **Speed Boost:** Increases movement speed for seven seconds.
- **Double Jump:** Allows one additional jump in the air for ten seconds.
- **Extra Life:** Restores one heart, up to the five-heart limit.

## Enemies

- **Slimes:** Patrol platforms and reverse direction at their patrol boundaries.
- **Bats:** Hover and fire projectiles toward the player after a visible warning.

Avoid contact with enemies, fireballs, and spikes.

## Music Credits

The default soundtrack is **“8bit Dungeon Level” by Kevin MacLeod**.

See **MUSIC_CREDITS.md** for the source, license, and attribution details. Keep that file included when sharing the game.

Two alternative tracks are also available from the Welcome screen.
