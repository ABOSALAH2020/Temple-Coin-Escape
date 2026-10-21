from pygame import Rect
from scripts.objects import Coin, Spike, ExitDoor
from scripts.powerups import PowerUp
from scripts.enemies import Slime, Bat


class Level:
    def __init__(self, index):
        self.index = index
        self.name = ['THE JUNGLE TRAIL', 'THE TWILIGHT RUINS', 'THE EMBER SANCTUM'][index]
        self.width = [2400,2800,3300][index]
        self.background = [None,'backgrounds/twilight_ruins','backgrounds/ember_sanctum'][index]
        self.difficulty = ['EASY','MEDIUM','HARD'][index]
        self.spawn = (48, 520)
        self.platforms = [Rect(0, 560, self.width, 40)]
        # Every climb is 70-80px; all coins can be reached with the base jump.
        layouts = [
            [(160,480,192),(430,408,192),(710,336,192),(990,408,192),
             (1270,480,192),(1550,408,192),(1830,336,192),(2100,440,160)],
            [(170,480,192),(450,400,192),(730,320,192),(1010,400,192),
             (1290,480,192),(1570,400,192),(1850,320,192),(2130,400,192),(2410,480,192)],
            [(160,480,160),(440,400,160),(720,320,160),(1000,400,144),
             (1280,480,160),(1560,400,160),(1840,320,144),(2120,400,160),
             (2400,480,160),(2680,400,160),(2960,320,160)]]
        self.platforms += [Rect(x,y,w,20) for x,y,w in layouts[index]]
        self.coins = [Coin(x+w//2-10,y-38) for x,y,w in layouts[index]]
        self.coins += [Coin(1120,522), Coin(self.width-220,522)]
        self.required = len(self.coins)-2
        spikes=[[600,632,1450,1482,1990],
                [630,662,1200,1232,1760,1792,2300],
                [360,392,640,672,1190,1222,1750,1782,2030,2310,2342,2870]]
        self.spikes = [Spike(x) for x in spikes[index]]
        slime_platforms=[[1,5],[1,5,7],[1,3,5,9]][index]
        self.slimes=[]
        for number in slime_platforms:
            x,y,w=layouts[index][number]
            self.slimes.append(Slime(x+35,y,x+12,x+w-12,[64,76,88][index]))
        bat_positions=[[(1050,450),(1930,400)],
                       [(1050,450),(1930,400),(2480,450)],
                       [(790,410),(1420,465),(2020,410),(2770,450)]][index]
        self.bats = [Bat(x,y,[2.6,2.1,1.6][index],[185,210,235][index]) for x,y in bat_positions]
        self.powerups=[]
        for platform_index,kind in zip([0,2,4,7],['shield','double_jump','speed','extra_life']):
            x,y,w=layouts[index][platform_index]
            self.powerups.append(PowerUp(x+25,y-42,kind))
        self.door = ExitDoor(self.width-100)
        self.projectiles = []

