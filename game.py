import math
import random
import pgzrun
from pygame import Rect
from scripts.settings import WIDTH, HEIGHT, TITLE, TRACKS
from scripts.player import Player
from scripts.camera import Camera
from scripts.level_manager import LevelManager
from scripts.audio import Audio


class Particle:
    def __init__(self, x, y, color, rng):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = rng.uniform(-90,90), rng.uniform(-170,-35)
        self.life = rng.uniform(0.3,0.65)
        self.color = color

    def update(self, dt):
        self.life -= dt
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.vy += 360*dt


class Game:
    def __init__(self):
        self.audio = Audio(sounds, music)
        self.manager = LevelManager()
        self.player = Player()
        self.camera = Camera()
        self.state = 'welcome'
        self.time = 0.0
        self.level_coins = 0
        self.particles = []
        self.rng = random.Random(42)
        self.shake = 0.0
        self.banner = 0.0
        self.notice = ''
        self.notice_time = 0.0
        self.mouse = (-1,-1)
        self.buttons = {}
        self.unlocked_announced = False

    @property
    def level(self):
        return self.manager.level

    def start(self):
        self.manager.restart()
        self.player = Player(self.level.spawn)
        self.level_coins = 0
        self.camera.reset()
        self.particles.clear()
        self.unlocked_announced = False
        self.state = 'playing'
        self.banner = 2.0
        self.notice_time = 0
        self.audio.play('start')

    def burst(self, x, y, color, count=12):
        self.particles += [Particle(x,y,color,self.rng) for _ in range(count)]

    def message(self, text):
        self.notice, self.notice_time = text, 2.0

    def hurt(self):
        if self.player.invulnerable > 0 or self.state != 'playing':
            return
        if self.player.shield:
            self.player.shield = False
            self.player.invulnerable = 1.0
            self.audio.play('shield')
            self.burst(*self.player.rect.center,'cyan',20)
            self.message('SHIELD SAVED YOU')
            return
        self.player.lives -= 1
        self.shake = 0.25
        self.audio.play('hurt')
        self.burst(*self.player.rect.center,'salmon',16)
        if self.player.lives <= 0:
            self.state = 'lose'
            self.audio.play('lose')
        else:
            self.player.respawn()
            self.player.invulnerable = 1.8
            self.player.hurt_time = 0.28
            self.camera.reset()
            self.level.projectiles.clear()

    def update(self, dt):
        dt = min(dt,0.05)
        if not self.audio.started:
            self.audio.start()
        if self.state == 'paused':
            return
        self.time += dt
        if self.state in ('level_complete','win'):
            self.player.animation.set('celebrate')
            self.player.animation.update(dt)
        if self.state == 'playing':
            # Substeps keep thin platforms and hazards reliable during a slow frame.
            remaining = dt
            while remaining > 0 and self.state == 'playing':
                step = min(remaining,1/120)
                self.step(step)
                remaining -= step
            self.banner = max(0,self.banner-dt)
            self.notice_time = max(0,self.notice_time-dt)
        self.shake = max(0,self.shake-dt)
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    def step(self, dt):
        p = self.player
        jumped = p.update(dt,keyboard.left or keyboard.a,keyboard.right or keyboard.d,
                          self.level.platforms,self.level.width)
        if jumped:
            self.audio.play('jump')
            self.burst(p.rect.centerx,p.rect.bottom,'#c2e4cd',6)
        self.camera.update(p.rect,self.level.width,dt)
        for coin in self.level.coins[:]:
            coin.animation.update(dt)
            if p.rect.colliderect(coin.rect):
                self.level.coins.remove(coin)
                p.score += 1
                self.level_coins += 1
                self.audio.play('coin')
                self.burst(*coin.rect.center,'gold')
        for item in self.level.powerups[:]:
            item.animation.update(dt)
            if p.rect.colliderect(item.rect):
                item.apply(p)
                self.level.powerups.remove(item)
                self.audio.play('powerup')
                self.burst(*item.rect.center,'cyan',18)
                labels={'speed':'SPEED BOOST - 7s','shield':'SHIELD READY',
                        'double_jump':'DOUBLE JUMP - 10s','extra_life':'EXTRA HEART'}
                self.message(labels[item.kind])
        for enemy in self.level.slimes:
            enemy.update(dt)
        for enemy in self.level.bats:
            shot = enemy.update(dt,p.rect)
            if shot:
                self.level.projectiles.append(shot)
                if abs(enemy.rect.centerx-p.rect.centerx)<420:
                    self.audio.play('shoot')
        for shot in self.level.projectiles[:]:
            shot.update(dt)
            if shot.life <= 0 or shot.rect.right < 0 or shot.rect.left > self.level.width:
                self.level.projectiles.remove(shot)
            elif p.rect.colliderect(shot.rect):
                self.level.projectiles.remove(shot)
                self.hurt()
        hazards = self.level.spikes+self.level.slimes+self.level.bats
        if any(p.rect.colliderect(obj.rect) for obj in hazards):
            self.hurt()
        if p.rect.top > HEIGHT+100:
            self.hurt()
        unlocked = self.level_coins >= self.level.required
        if unlocked and not self.unlocked_announced:
            self.unlocked_announced = True
            self.message('EXIT OPEN - FOLLOW THE TEMPLE TRAIL')
            self.audio.play('unlock')
        if p.rect.colliderect(self.level.door.rect) and unlocked and self.state=='playing':
            self.state = 'level_complete' if self.manager.index < self.manager.COUNT-1 else 'win'
            self.audio.play('win')
            self.burst(*p.rect.center,'gold',36)

    def next_level(self):
        if self.manager.advance():
            self.player.spawn = self.level.spawn
            self.player.respawn()
            self.player.invulnerable = 1.0
            self.player.speed_time = self.player.double_time = 0
            self.player.shield = False
            self.level_coins = 0
            self.camera.reset()
            self.particles.clear()
            self.unlocked_announced = False
            self.banner = 2.0
            self.notice_time = 0
            self.state = 'playing'

    def background(self, menu=False):
        if not menu and self.level.background:
            screen.blit(self.level.background,(0,0))
            return
        screen.blit('backgrounds/sky',(0,0))
        camera = self.time*8 if menu else self.camera.x
        for name,factor in [('mountains',0.10),('temple_back',0.25)]:
            offset = int(camera*factor)%WIDTH
            screen.blit('backgrounds/'+name,(-offset,0))
            screen.blit('backgrounds/'+name,(WIDTH-offset,0))

    def text(self, text, pos, size=24, color='#f7e9bd', center=False):
        kwargs = {'fontsize':size,'color':color,'shadow':(1,2),'scolor':'#101d29'}
        kwargs['center' if center else 'topleft'] = pos
        screen.draw.text(str(text),**kwargs)

    def button(self, name, label, rect, enabled=True):
        self.buttons[name] = rect if enabled else None
        hovered = rect.collidepoint(self.mouse) and enabled
        screen.draw.filled_rect(rect,'#257f78' if hovered else '#173a48')
        screen.draw.rect(rect,'#ffd270' if hovered else '#739b87')
        self.text(label,rect.center,25,'#fff0c2' if enabled else '#8c9d9b',True)

    def panel(self, rect):
        screen.draw.filled_rect(rect,'#102b38')
        screen.draw.rect(rect,'#c8a85e')

    def draw_menu(self):
        self.background(True)
        self.panel(Rect(125,55,550,485))
        self.text('WELCOME TO',(400,89),23,'#9fcebd',True)
        self.text('TEMPLE COIN ESCAPE',(400,130),43,'#ffd778',True)
        self.text('Find the gold. Outsmart the ruins.',(400,171),22,center=True)
        frame = int(self.time*6)%6
        screen.blit(f'player/idle_{frame:02d}',(225,202))
        screen.blit('items/coin_00',(303,218))
        screen.blit('powerups/shield_00',(380,212))
        screen.blit('enemies/slime/idle_00',(460,218))
        screen.blit('enemies/bat/fly_02',(531,208))
        self.button('start','START ADVENTURE  [ENTER]',Rect(210,269,380,48))
        music_label = 'MUSIC BY KEVIN MACLEOD' if self.audio.track == 0 else 'CHOOSE YOUR MUSIC'
        self.text(music_label,(400,344),20,'#9fcebd',True)
        self.button('track_prev','<',Rect(210,364,44,42))
        self.text(TRACKS[self.audio.track][1],(400,385),27,center=True)
        self.button('track_next','>',Rect(546,364,44,42))
        self.button('music','MUSIC: '+('ON' if self.audio.music_enabled else 'OFF'),Rect(210,424,180,42))
        self.button('sfx','SFX: '+('ON' if self.audio.sfx_enabled else 'OFF'),Rect(410,424,180,42))
        self.button('exit','EXIT',Rect(300,483,200,36))
        self.text('ARROWS / A D: move    SPACE / UP: jump    ESC: pause',(400,567),20,center=True)

    def draw_world(self):
        self.background()
        cam = self.camera.x
        if self.shake:
            cam += math.sin(self.time*90)*4
        def sprite(name,x,y):
            if -100 < x-cam < WIDTH+100:
                screen.blit(name,(round(x-cam),round(y)))
        for platform in self.level.platforms:
            if platform.y == 560:
                start = max(0,int(cam//32)*32)
                for x in range(start,min(self.level.width,start+WIDTH+64),32):
                    sprite('tiles/ground_center',x,560)
                    sprite('tiles/ground_fill',x,592)
            else:
                count = math.ceil(platform.width/32)
                for i in range(count):
                    part = 'left' if i==0 else 'right' if i==count-1 else 'center'
                    x = min(platform.x+i*32,platform.right-32)
                    sprite('tiles/platform_'+part,x,platform.top)
        for x in range(90,self.level.width,370):
            sprite('tiles/fern_00',x,514)
        for coin in self.level.coins:
            sprite(coin.animation.image,coin.rect.centerx-12,coin.rect.centery-12)
        for item in self.level.powerups:
            bob = math.sin(self.time*3+item.rect.x)*3
            sprite(item.animation.image,item.rect.centerx-16,item.rect.centery-16+bob)
        for spike in self.level.spikes:
            sprite('tiles/spikes_00',spike.rect.x-5,536)
        for enemy in self.level.slimes:
            sprite(enemy.animation.image,enemy.rect.centerx-20,enemy.rect.bottom-32)
        for enemy in self.level.bats:
            sprite(enemy.animation.image,enemy.rect.centerx-24,enemy.rect.centery-20)
            if enemy.windup > 0:
                self.text('!',(enemy.rect.centerx-cam,enemy.rect.top-17),28,'#ffd778',True)
        for shot in self.level.projectiles:
            sprite(shot.animation.image,shot.rect.centerx-16,shot.rect.centery-12)
        unlocked = self.level_coins >= self.level.required
        sprite('tiles/exit_open_00' if unlocked else 'tiles/exit_locked_00',self.level.door.rect.centerx-32,480)
        p = self.player
        if not p.invulnerable or int(self.time*12)%2==0:
            sprite(p.animation.image,p.rect.centerx-24,p.rect.bottom-48)
        if p.shield:
            # A hollow aura leaves the character readable; no solid pickup icon overlay.
            center = (round(p.rect.centerx-cam),p.rect.centery)
            screen.draw.circle(center,29,'#80edfa')
            screen.draw.circle(center,31,'#317bba')
            for i in range(3):
                angle = self.time*1.8 + i*math.tau/3
                point = (round(center[0]+30*math.cos(angle)),round(center[1]+30*math.sin(angle)))
                screen.draw.filled_circle(point,2,'#d8fcff')
        for particle in self.particles:
            screen.draw.filled_circle((round(particle.x-cam),round(particle.y)),2,particle.color)
        self.draw_hud()
        if self.banner>0:
            self.panel(Rect(190,90,420,62))
            self.text(self.level.name+' - '+self.level.difficulty,(400,121),25,center=True)
        if self.notice_time>0:
            self.panel(Rect(150,510,500,34))
            self.text(self.notice,(400,527),21,center=True)

    def draw_hud(self):
        self.panel(Rect(12,12,776,62))
        for i in range(5):
            screen.blit('ui/heart_full_00' if i<self.player.lives else 'ui/heart_empty_00',(22+i*29,25))
        screen.blit('ui/coin_00',(205,25))
        self.text(f'{self.level_coins} / {self.level.required}',(243,30),25)
        self.text(f'TEMPLE {self.manager.index+1} / {self.manager.COUNT}',(400,31),22)
        self.button('pause','PAUSE',Rect(682,23,94,38))
        buffs=[]
        if self.player.shield: buffs.append('SHIELD')
        if self.player.speed_time>0: buffs.append(f'SPEED {math.ceil(self.player.speed_time)}s')
        if self.player.double_time>0: buffs.append(f'DOUBLE JUMP {math.ceil(self.player.double_time)}s')
        if buffs:
            self.text('  |  '.join(buffs),(20,80),20,'#d5fff2')

    def draw_overlay(self):
        self.panel(Rect(160,155,480,315))
        if self.state=='paused':
            title,sub='TAKE A BREATH','Your adventure is waiting.'
        elif self.state=='lose':
            title,sub='TRY ANOTHER TRAIL',f'You collected {self.player.score} coins. You can do this!'
        elif self.state=='level_complete':
            title,sub='TEMPLE CLEARED','A deeper temple awaits...'
        else:
            title,sub='YOU ESCAPED!',f'Three temples. {self.player.score} coins. One great adventure.'
        self.text(title,(400,199),36,'#ffd778',True)
        self.text(sub,(400,244),21,center=True)
        if self.state=='paused':
            self.button('resume','RESUME  [ESC]',Rect(240,280,320,44))
            self.button('music','MUSIC: '+('ON' if self.audio.music_enabled else 'OFF'),Rect(240,337,150,40))
            self.button('sfx','SFX: '+('ON' if self.audio.sfx_enabled else 'OFF'),Rect(410,337,150,40))
        else:
            label='NEXT TEMPLE  [ENTER]' if self.state=='level_complete' else 'PLAY AGAIN  [ENTER]'
            self.button('next' if self.state=='level_complete' else 'restart',label,Rect(240,289,320,46))
        self.button('menu','WELCOME SCREEN',Rect(240,402,320,42))

    def draw(self):
        self.buttons.clear()
        if self.state=='welcome':
            self.draw_menu()
        else:
            self.draw_world()
            if self.state!='playing':
                self.draw_overlay()

    def action(self, name):
        self.audio.play('click')
        if name in ('start','restart'): self.start()
        elif name=='next': self.next_level()
        elif name=='track_prev': self.audio.select(-1)
        elif name=='track_next': self.audio.select(1)
        elif name=='music': self.audio.toggle_music()
        elif name=='sfx': self.audio.toggle_sfx()
        elif name=='pause' and self.state=='playing': self.state='paused'
        elif name=='resume': self.state='playing'
        elif name=='menu': self.state='welcome'
        elif name=='exit': raise SystemExit


game = Game()


def draw():
    game.draw()


def update(dt):
    game.update(dt)


def on_key_down(key):
    if key==keys.ESCAPE:
        if game.state=='playing': game.action('pause')
        elif game.state=='paused': game.action('resume')
        elif game.state!='welcome': game.action('menu')
    elif key==keys.M:
        game.audio.toggle_music()
    elif game.state=='welcome':
        if key==keys.RETURN: game.action('start')
        elif key==keys.LEFT: game.action('track_prev')
        elif key==keys.RIGHT: game.action('track_next')
    elif game.state=='playing' and key in (keys.SPACE,keys.UP,keys.W):
        game.player.request_jump()
    elif game.state in ('win','lose','level_complete') and key in (keys.RETURN,keys.R):
        game.action('next' if game.state=='level_complete' else 'restart')


def on_mouse_move(pos):
    game.mouse = pos


def on_mouse_down(pos,button):
    if button!=mouse.LEFT: return
    for name,rect in list(game.buttons.items()):
        if rect and rect.collidepoint(pos):
            game.action(name)
            return


pgzrun.go()
