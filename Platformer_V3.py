import os 
import pygame
import random
import math
import numpy as np
import threading
import time
GAMETIME=60
DEBUG=False
GAMERESET=False
InvisTime,Parrytime,SpikeTime,BlackHoleTime=4,1,1,2
FRUIT_HEAL=5
FireDMG,SpikeFaceDMG,SawDMG,DashDMG,HeapBumpDMG,SwordDMG,SpikeDMG,SlashDMG,KickDMG,DeathBeamDMG=10,20,15,25,20,10,10,5,20,100
FireCD,SpikeFaceCD,SawCD,DashCD,IceCD,InvisCD,SwordCD,ParryCD,SpikeCD,BHCD,SlashCD,KickCD,DeathBeamCD=5,7,3,5,5,10,3,7,9,9,1,3,60
pygame.init()
pygame.display.set_caption("A Platformer Game")
WIDTH,HEIGHT=1000,600
FPS=60
VEL=5
RAN=False
COLORS=["Brown"]
ANISPEED=3
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
file=os.path.abspath(__file__).split("\\")
file=file[0:len(file)-1]
fpath="\\".join(file)
PATH=os.path.join(fpath,"assets")
FILEPATH=fpath
BLOCKSIZE=96
BLOCK=128 #Blocks at Differ of 64
BLOCKIMG=None
def genframeVal():
    num=0
    while True:
        yield num
        num+=1
def abimg(img):
    _,_,width,height=img.get_rect()
    return (img,width,height)
def flipimg(imgs):
    fimgs=[]
    for img in imgs:
        fimgs.append(pygame.transform.flip(img,1,0))
    return fimgs
def loadSpriteSheets(dir,dir2,width,height,size=None,scale_to=None):
    images=[]
    size=2.5 if not size else size
    fopath=os.path.join(PATH,dir)
    if dir2:
        cpath=os.path.join(fopath,dir2)
        for file in os.listdir(cpath):
            if os.path.isfile(os.path.join(cpath,file)):
                fpath=os.path.join(cpath,file)
                images.append(fpath)
    else:
        images.append(fopath)
    all_anims={}
    for image in images:
        sheet=pygame.image.load(image)
        anims=[]
        for i in range(sheet.get_width()//width):
            surface=pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect=pygame.Rect(i*width,0,width,height)
            surface.blit(sheet,(0,0),rect)
            if not scale_to:
                anims.append(pygame.transform.scale_by(surface,size))
            else:
                anims.append(pygame.transform.scale(surface,scale_to))        
        name = os.path.splitext(os.path.basename(image))[0]
        all_anims[name + "_right"] = anims
        all_anims[name + "_left"] = flipimg(anims)
    return all_anims
SAW=loadSpriteSheets(os.path.join(PATH,"Traps\Saw\on.png"),None,38,38)
ICE=loadSpriteSheets(os.path.join(PATH,r"Traps\Iced\ball.png"),None,16,16)
ICED=loadSpriteSheets(os.path.join(PATH,"Traps\Iced\iced.png"),None,48,48)
FIRE=loadSpriteSheets(os.path.join(PATH,"Traps\Fire\on.png"),None,16,32)
SPIKES=loadSpriteSheets(os.path.join(PATH,"Traps\Spikes\Idle.png"),None,16,16)
SPIKEBLOCK=loadSpriteSheets(os.path.join(PATH,"Traps"),"Spike Head",54,52)
DISSAPEARING=loadSpriteSheets(r"C:\PYTHON\PyGame YAY!!!\Python-Platformer-main\assets\MainCharacters\Disappearing.png",None,32,32,2)
APPEARING=loadSpriteSheets(r"C:\PYTHON\PyGame YAY!!!\Python-Platformer-main\assets\MainCharacters\Appearing.png",None,32,32)
TRAMPOLINE_IDLE=loadSpriteSheets(os.path.join(PATH,"Traps\Trampoline\Idle.png"),None,28,28)
TRAMPOLINE_JUMP=loadSpriteSheets(os.path.join(PATH,"Traps\Trampoline\Jump.png"),None,28,28)
APPLE=loadSpriteSheets(os.path.join(PATH,"Items\Fruits\Apple.png"),None,32,32)
CHERRIES=loadSpriteSheets(os.path.join(PATH,"Items\Fruits\Cherries.png"),None,32,32)
STRAWBERRY=loadSpriteSheets(os.path.join(PATH,"Items\Fruits\Strawberry.png"),None,32,32)
SWORD=loadSpriteSheets(os.path.join(PATH,"Traps\Sword.png"),None,300,320,None,(50,50))
KICK=loadSpriteSheets(os.path.join(PATH,"Traps\spritesheet.png"),None,50,53,None,(50,50))
BUBBLE=loadSpriteSheets(os.path.join(PATH,r"Traps\bubble.png"),None,164,197,None,(74,90))
BLACKHOLE_Open=loadSpriteSheets(os.path.join(PATH,r"Traps\blackholeOpen.png"),None,50,49,2)
BLACKHOLE_Close=loadSpriteSheets(os.path.join(PATH,r"Traps\blackholeClose.png"),None,50,49,None,(40,40))
def GetCooldown(last,maxCD):
    end=last+maxCD
    remain=max(0,end-time.time())
    return remain/maxCD
class TrapInstance(pygame.sprite.Sprite):
    def __init__(self, rect,dir,sur):
        super().__init__()
        self.start=time.time()
        self.rect = rect
        self.expired=False
        self.direction=dir
        self.mask=pygame.mask.from_surface(sur)
class Traps(pygame.sprite.Sprite):
    def __init__(self,player,spritesheet,cooldown,keys,name):
        super().__init__()
        self.lastTime=0
        self.traps=[]
        self.surftodraw=None
        self.i=0
        self.cooldown=cooldown
        self.expired=False
        self.key=keys
        self.spritesheet=spritesheet
        self.player=player
        self.name=name
        self.mask=self.spritesheet[self.name+"_right"][0]
        self.frcount=genframeVal()
        self.w=32
        self.h=16
        self.hitC=0
        self.trapped=False
        self.Respawned=False
    def CheckExpire(self,outofScreen=True,expireT=3,hit=False,Respawn=False):
        for trap in self.traps[:]:
            if not outofScreen:
                if time.time()-trap.start>=expireT:
                    trap.expired=True
                    if Respawn:
                        self.Respawned=True
            if outofScreen:
                if trap.rect.x>WIDTH or trap.rect.x<0:
                    trap.expired=True
                    if Respawn:
                        self.Respawned=True
            if hit:
                if self.trapped:
                    self.traps.remove(trap)
                    if Respawn:
                        self.Respawned=True
    def updateAni(self,anicount=None,anispeed=ANISPEED,changeTo="blink"):
        for trap in self.traps:
            if not trap.expired:
                if next(self.frcount)%anispeed==0:
                    if self.i<len(self.spritesheet[self.name+"_"+trap.direction]):
                        self.surftodraw=self.spritesheet[self.name+"_"+trap.direction][self.i]
                        self.i+=1
                    else:
                        self.i=0
                        if anicount:
                            self.hitC+=1
                            if self.hitC>=self.anicount:
                                self.traps.remove(trap)
                                self.hitC=0
                                self.name=changeTo
                trap.mask=pygame.mask.from_surface(self.surftodraw)
                WIN.blit(self.surftodraw,trap.rect)
            else:
                self.traps.remove(trap)
    def checkPress(self,player,ReturnCD=False):
        currenttime=time.time()
        keys=pygame.key.get_pressed()
        if self.key:
            if keys[self.key] and currenttime-self.lastTime>=self.cooldown:
                trap = TrapInstance(self.rect,self.player.direction,self.mask)
                self.traps.append(trap)
                self.lastTime=currenttime
        if ReturnCD:
            return GetCooldown(self.lastTime,self.cooldown)
    def spawnIndefinite(self):
        trap = TrapInstance(self.rect,self.player.direction,self.mask)
        self.traps.append(trap)
    def move(self,speed,towplayer=False,player2=None,moveinx=True,stop=False):
        if not stop:
            for trap in self.traps:
                if not towplayer:
                    if moveinx:
                        trap.rect.x+=speed if trap.direction=="right" else -speed
                    else:
                        trap.rect.y+=speed
                if towplayer:
                    pass
    def collision(self,player1,player2,DMG=None,HandleMulti=False):
        for trap in self.traps:
            if player1:
                if pygame.sprite.collide_mask(trap,player1):
                    if HandleMulti:
                        player1.TrapColl(DMG,player2) if not player1.hit and not player2.hit else None
                        self.trapped=True
                    else:
                        player1.TrapColl(DMG,player2)
                        self.trapped=True
            if pygame.sprite.collide_mask(trap,player2):
                if HandleMulti:
                    player2.TrapColl(DMG,player1) if not player2.hit and not player1.hit else None
                    self.trapped=True
                else:
                    player2.TrapColl(DMG,player1)
                    self.trapped=True
            else:
                self.trapped=False
class Kick(Traps):
    def __init__(self, player, key):
        super().__init__(player, KICK, KickCD, key, "spritesheet")
        self.w = 50
        self.h = player.rect.height

    def SpawnKick(self, player):
        if player.direction == "right":
            rect = pygame.Rect(player.rect.right+15, player.rect.top+32, self.w, self.h)
        else:
            rect = pygame.Rect(player.rect.left - self.w, player.rect.top+32, self.w, self.h)

        trap = TrapInstance(rect, player.direction, self.mask)
        self.traps.append(trap)

    def checkPress(self, player, ReturnCD=False):
        currenttime = time.time()
        keys = pygame.key.get_pressed()
        if keys[self.key] and currenttime - self.lastTime >= self.cooldown:
            self.SpawnKick(player)
            self.lastTime = currenttime
        if ReturnCD:
            return GetCooldown(self.lastTime,self.cooldown)

    def loop(self, player, player2):
        cooldown = self.checkPress(player, True)
        for trap in self.traps:
            if trap.rect.colliderect(player2.rect):
                player2.TrapColl(KickDMG,player)
                if trap.direction == "right":
                    player2.rect.x += 30
                    player2.rect.y-=15
                else:
                    player2.rect.x -= 30
                    player2.rect.y-=15
                self.traps.remove(trap)
        super().CheckExpire(False, 0.3, False, False) 
        super().updateAni()
        return cooldown
class SwordSlash(Traps):
    def __init__(self, player, key):
        super().__init__(player, SWORD, SlashCD, key, "Sword")
        self.w = 50
        self.h = player.rect.height
    def SpawnSlash(self, player):
        if player.direction == "right":
            rect = pygame.Rect(player.rect.right+20, player.rect.top+27, self.w, self.h)
        else:
            rect = pygame.Rect(player.rect.left - self.w, player.rect.top+27, self.w, self.h)

        trap = TrapInstance(rect, player.direction, self.mask)
        self.traps.append(trap)

    def checkPress(self, player, ReturnCD=False):
        currenttime = time.time()
        keys = pygame.key.get_pressed()
        if keys[self.key] and currenttime - self.lastTime >= self.cooldown:
            self.SpawnSlash(player)
            self.lastTime = currenttime
        if ReturnCD:
            return GetCooldown(self.lastTime,self.cooldown)

    def loop(self, player, player2):
        cooldown = self.checkPress(player, True)
        super().collision(None, player2, SwordDMG)
        super().CheckExpire(False, 0.2, True, False)
        super().updateAni()
        return cooldown
class BlackHole(Traps):
    def __init__(self,player,key):
        super().__init__(player,BLACKHOLE_Open,BHCD,key,"blackholeOpen")
        self.w=50
        self.h=49
        self.rect=pygame.Rect(player.rect.x+player.rect.width+75 if player.direction=="right" else player.rect.x-player.rect.width-25,player.rect.y+player.rect.height//2,self.w,self.h)
        self.center = pygame.Vector2(self.rect.x, self.rect.y)
        self.radius = 700
    def apply_gravity(self, player):
        for trap in self.traps:
            min_pull = 2
            max_pull = 20
            player_center = pygame.Vector2(player.rect.center)
            self.center = pygame.Vector2(trap.rect.x, trap.rect.y)
            direction = self.center - player_center
            distance = direction.length()
            if distance < self.radius:  # inside black hole range
                if distance > 0:
                    strength = min_pull + (max_pull - min_pull) * (1 - distance / self.radius)
                    force = direction.normalize() * strength
                    player.rect.x += int(force.x)
                    player.rect.y += int(force.y)
    def checkPress(self,player,ReturnCD=False):
        currenttime=time.time()
        keys=pygame.key.get_pressed()
        if self.key:
            if keys[self.key] and currenttime-self.lastTime>=self.cooldown:
                self.rect=pygame.Rect(player.rect.x+player.rect.width+75 if player.direction=="right" else player.rect.x-player.rect.width-25,player.rect.y-player.rect.height//4,self.w,self.h)
                trap = TrapInstance(self.rect,player.direction,self.mask)
                self.traps.append(trap)
                self.lastTime=currenttime
        if ReturnCD:
            return GetCooldown(self.lastTime,self.cooldown)
    def loop(self,player,player2):
        super().CheckExpire(False,BlackHoleTime,False,False)
        cooldown=self.checkPress(player,True)
        self.apply_gravity(player2)
        super().updateAni(None,10)
        return cooldown
class SpikeGround(Traps):
    def __init__(self,player,key):
        super().__init__(player,SPIKES,SpikeCD,key,"Idle")
        self.w=16
        self.h=16
    def SpawnTrap(self,player,ReturnCD):
        keys=pygame.key.get_pressed()
        if keys[self.key] and time.time()-self.lastTime>=self.cooldown:
            startPt_x,y=player.rect.x+player.rect.width+20 if player.direction=="right" else player.rect.x-player.rect.width-20,HEIGHT-40-BLOCKSIZE//2
            num=min(16,(WIDTH-startPt_x)//16) if self.player.direction=="right" else min(16,(startPt_x)//16)
            for i in range(num):
                self.rect=pygame.Rect(startPt_x,y,self.w,self.h)
                trap = TrapInstance(self.rect,player.direction,self.mask)
                self.traps.append(trap)
                startPt_x-=16 if player.direction=="left" else -16
            self.lastTime=time.time()
        if ReturnCD:
            return GetCooldown(self.lastTime,self.cooldown)
    def loop(self,player,player2):
        cooldown=self.SpawnTrap(player,True)
        super().updateAni()
        super().collision(player,player2,SpikeDMG,True)
        super().CheckExpire(False,SpikeTime,False,False)
        return cooldown
class Fruits(Traps):
    def __init__(self,player):
        fruit=random.choice(["Apple","Strawberry","Cherries"])
        key=None
        super().__init__(player,APPLE if fruit=="Apple" else CHERRIES if fruit=="Cherries" else STRAWBERRY,1,key,fruit)
        self.w=32
        self.h=32
        self.rect=pygame.Rect(random.randint(0,WIDTH),random.randint(0,HEIGHT-115),self.w,self.h)
        super().spawnIndefinite()
    def collision(self,player2,player):
        for trap in self.traps:
            if pygame.sprite.collide_mask(trap,player2):
                player2.heal(5)
                self.traps.remove(trap)
                self.Respawned=True
            if pygame.sprite.collide_mask(trap,player):
                player.heal(5)
                self.Respawned=True
                self.traps.remove(trap)
    def loop(self,player,player2):
        if self.Respawned:
            self.Respawned=False
            self.rect=pygame.Rect(random.randint(0,WIDTH),random.randint(0,HEIGHT-BLOCKSIZE//4),self.w,self.h)
            super().spawnIndefinite()
        super().CheckExpire(False,10,False,True)
        super().updateAni()
        self.collision(player2,player)
class Fire(Traps):
    def __init__(self,player,key):
        super().__init__(player,FIRE,FireCD,key,"on")
        self.w=32
        self.h=16
    def loop(self,player,player2):
        self.rect=pygame.Rect(self.player.rect.x+self.player.rect.width+10 if self.player.direction=="right" else self.player.rect.x-self.player.rect.width,self.player.rect.bottom-32-BLOCKSIZE//2,self.w,self.h)
        super().CheckExpire(False,3)
        cooldown=super().checkPress(player,True)
        super().updateAni()
        super().collision(player,player2,FireDMG,True)
        return cooldown
class Trampoline(Traps):
    def __init__(self,player,key,x,y):
        super().__init__(player,TRAMPOLINE_IDLE,3,key,"Idle")
        self.w=28
        self.h=28
        self.x=x
        self.y=y
        self.jump=False
        self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
        super().spawnIndefinite()
    def collision(self,player1,player2):
        for trap in self.traps:
            if pygame.sprite.collide_mask(trap,player1):
                # self.spritesheet=TRAMPOLINE_JUMP
                # self.name="Jump"
                player1.fall_vel = -(player1.jump+3)
                player1.onground = False
                player1.onblock=False
            if pygame.sprite.collide_mask(trap,player2):
                # self.spritesheet=TRAMPOLINE_JUMP
                # self.name="Jump"
                player2.fall_vel = -(player2.jump+3)
                player2.onground = False
                player2.onblock=False
            else:
                self.spritesheet=TRAMPOLINE_IDLE
                self.name="Idle"
    def loop(self,player,player2):
        if self.jump:
            super().updateAni(1,anispeed=ANISPEED,changeTo="Jump")
        else:
            super().updateAni()
        self.collision(player,player2)
class Saw(Traps):
    def __init__(self,player,key):
        super().__init__(player,SAW,SawCD,key,"on")
        self.w=38
        self.h=38
    def loop(self,player,player2):
        self.rect=pygame.Rect(self.player.rect.x+self.player.rect.width if self.player.direction=="right" else self.player.rect.x-self.player.rect.width,self.player.rect.bottom-32-BLOCKSIZE//1.5,self.w,self.h)
        super().CheckExpire(True,None,True)
        cooldown=super().checkPress(player,True)
        super().move(15)
        super().updateAni()
        super().collision(None,player2,SawDMG)
        return cooldown
class Ice(Traps):
    def __init__(self,player,key):
        super().__init__(player,ICE,IceCD,key,"ball")
        self.w=20
        self.h=17
    def collision(self,player2):
        for trap in self.traps:
            if pygame.sprite.collide_mask(trap,player2):
                player2.Iced()
    def loop(self,player,player2):
        self.rect=pygame.Rect(self.player.rect.x+self.player.rect.width if self.player.direction=="right" else self.player.rect.x-self.player.rect.width,self.player.rect.bottom-32-BLOCKSIZE//4,self.w,self.h)
        super().CheckExpire(True)
        cooldown=super().checkPress(player,True)
        super().move(15)
        super().updateAni()
        self.collision(player2)
        return cooldown
class SpikeBlock(Traps):
    def __init__(self,player,key):
        super().__init__(player,SPIKEBLOCK,SpikeFaceCD,key,"blink")
        self.w=38
        self.h=38
        # self.player2=player2
        # self.rect=pygame.Rect(self.player2.rect.x,0,54,52)
        self.hitC=0
        self.anicount=0
        self.stop=False
        self.anispeed=ANISPEED
    def checkGroundColl(self):
        for trap in self.traps:
            if trap.rect.bottom>HEIGHT-120:
                self.name="bottom"
                self.anicount=1
                self.stop=True
                self.anispeed=2
            else:
                self.name="blink"
                self.i = 0
                self.hitC = 0
                self.anicount=0
                self.stop=False
                self.anispeed=ANISPEED
    def loop(self,player,player2):
        self.rect=pygame.Rect(player2.rect.x-25,0,54,52)
        super().CheckExpire(True)
        cooldown=super().checkPress(player,True)
        super().move(15,False,player2,False,self.stop)
        super().updateAni(self.anicount,self.anispeed)
        super().collision(player,player2,SpikeFaceDMG,True)
        self.checkGroundColl()
        return cooldown
class DeathBeam(Traps):
    def __init__(self,player,key):
        super().__init__(player,SPIKEBLOCK,DeathBeamCD,key,"blink")
        self.w=38
        self.h=38
        # self.player2=player2
        # self.rect=pygame.Rect(self.player2.rect.x,0,54,52)
        self.hitC=0
    def checkGroundColl(self):
        for trap in self.traps:
            if trap.rect.bottom>HEIGHT-120:
                self.name="bottom"
                self.anicount=1
                self.stop=True
                self.anispeed=2
            else:
                self.name="blink"
                self.i = 0
                self.hitC = 0
                self.anicount=0
                self.stop=False
                self.anispeed=ANISPEED
    def loop(self,player,player2):
        self.rect=pygame.Rect(player2.rect.x-25,0,54,52)
        super().CheckExpire(True)
        cooldown=super().checkPress(player,True)
        super().move(15,False,player2,False)
        super().updateAni()
        super().collision(player,player2,DeathBeamDMG,True)
        self.checkGroundColl()
        return cooldown
def handle_horizontal_coll(self, objs,dx,player2):
    self.rect.x+=dx
    collidedobjs = None
    for obj in objs:
        if pygame.sprite.collide_mask(obj,self):
            collidedobjs=obj
    if self.rect.colliderect(player2.rect):
        if pygame.sprite.collide_mask(self,player2):
            collidedobjs=player2
    self.rect.x-=dx
    return collidedobjs
def handle_vertical_coll(self,objs,player2,isplayer2):
    up=pygame.K_UP if isplayer2 else pygame.K_w
    for obj in objs:
        if pygame.sprite.collide_mask(self,obj):
            if self.y_vel>0:
                self.rect.bottom=obj.rect.top
                self.land()
            if self.y_vel<0:
                self.rect.top=obj.rect.bottom
                self.hitHead()
    # headRect=pygame.Rect(player2.rect.x+13,player2.rect.y,player2.rect.width-25,player2.rect.height)
    if self.rect.colliderect(player2.rect):
        if self.y_vel>0:
            self.rect.bottom=player2.rect.top
class Player(pygame.sprite.Sprite):
    fr2=genframeVal()
    def __init__(self,x,y,vel,grav,jump,player,dir="right",player2=None):
        super().__init__()
        self.sprites=loadSpriteSheets("MainCharacters",player,32,32,None,(80,80))
        exsprite=pygame.Surface.get_rect(self.sprites["idle_right"][0])
        self.rect=pygame.Rect(x,y,exsprite.width-20,exsprite.height)
        self.direction=dir
        self.mask=pygame.mask.from_surface(self.sprites["idle_right"][0])
        self.vel=vel
        self.jump=jump
        self.grav=grav
        self.fall_vel=0
        self.fall=0
        self.spritetoDraw=self.sprites["idle_right"][0]
        self.i=0
        self.frcount=genframeVal()
        self.spritesheet="idle"
        self.y_vel=0
        self.x_vel=0
        self.onground=True
        self.onblock=False
        self.jumpcount=0
        self.state="idle_"
        self.hit=False
        self.AniIters=0
        self.hitC=0
        self.icedC=0
        self.iced=False
        self.lastdash,self.lastinvis=0,0
        self.dashframes=10
        self.dash=False
        self.health=100
        self.keys=[pygame.K_f,pygame.K_q,pygame.K_e,pygame.K_r,pygame.K_3,pygame.K_4,pygame.K_TAB,pygame.K_CAPSLOCK,pygame.K_5] if not player2 else [pygame.K_p,pygame.K_l,pygame.K_m,pygame.K_k,pygame.K_SLASH,pygame.K_COMMA,pygame.K_COLON,pygame.K_i,pygame.K_j]
        self.fire=Fire(self,self.keys[0])
        self.saw=Saw(self,self.keys[1])
        self.ice=Ice(self,self.keys[2])
        self.slash=SwordSlash(self,self.keys[6])
        self.kick=Kick(self,self.keys[7])
        self.deathbeam=DeathBeam(self,self.keys[8])
        self.spikeball=SpikeBlock(self,self.keys[3])
        self.blackhole=BlackHole(self,self.keys[4])
        self.spikeGND=SpikeGround(self,self.keys[5])
        self.tramp=Trampoline(self,None,404,230) if not player2 else Trampoline(self,None,625,HEIGHT-115)
        self.fruits=Fruits(self)
        self.traps=[self.fire,self.saw,self.ice,self.slash,self.kick,self.deathbeam,self.spikeball,self.blackhole,self.spikeGND]
        self.Invis=False
        self.Parry=False
        self.lastParry=False
        self.Cooldowns=[FireCD,SawCD,IceCD,SpikeFaceCD,BHCD,SpikeCD,SwordCD,KickCD,DeathBeamCD,DashCD,InvisCD,ParryCD]
    def handlemove(self,vel,player1v2,dashVel,player2,objs):
        if not self.iced:
            if player1v2:
                right,left,dash1,invis,parry=pygame.K_RIGHT,pygame.K_LEFT,pygame.K_DOWN,pygame.K_RCTRL,pygame.K_RALT
            else:
                right,left,dash1,invis,parry=pygame.K_d,pygame.K_a,pygame.K_s,pygame.K_1,pygame.K_2
            keys=pygame.key.get_pressed()
            coll_right=handle_horizontal_coll(self,objs,VEL,player2)
            coll_left=handle_horizontal_coll(self,objs,-VEL,player2)
            CurrentTime=time.time()
            if not self.dash:
                if keys[right] and self.rect.x<(WIDTH-self.rect.width) and not coll_right:
                    self.x_vel=vel
                    if self.direction!="right":
                        self.direction="right"
                    self.rect.x+=self.x_vel
                elif keys[left] and self.rect.x>0 and not coll_left:
                    self.x_vel=-vel
                    if self.direction!="left":
                        self.direction="left"
                    self.rect.x+=self.x_vel
                else:
                    self.x_vel=0
                if keys[dash1] and CurrentTime-self.lastdash>=DashCD:
                    self.dash=True
                    self.lastdash=CurrentTime
                if keys[invis] and CurrentTime-self.lastinvis>=InvisCD:
                    self.Invis=True
                    self.lastinvis=CurrentTime
                if keys[parry] and CurrentTime-self.lastParry>=ParryCD:
                    self.Parry=True
                    self.lastParry=CurrentTime
            elif self.dash:
                self.spritesheet=DISSAPEARING["Disappearing_right"]
                self.dashframes-=1
                self.rect.x+=dashVel if self.direction=="right" and self.rect.x<(WIDTH-self.rect.width) else -dashVel if self.rect.x>0 else 0
                if self.rect.colliderect(player2.rect):
                    if not player2.hit:
                        player2.TrapColl(DashDMG,self)
                if self.dashframes<=0:
                    self.dash=False
                    self.dashframes=10
            if self.Invis:
                self.spritesheet=APPEARING["Appearing_right"]
                if CurrentTime-self.lastinvis>=InvisCD:
                    self.Invis=False
            if self.Parry:
                if CurrentTime-self.lastParry>=Parrytime:
                    self.Parry=False
            self.Cooldowns[9]=GetCooldown(self.lastdash,DashCD)
            self.Cooldowns[10]=GetCooldown(self.lastinvis,InvisCD)
            self.Cooldowns[11]=GetCooldown(self.lastParry,ParryCD)
    def checkOut(self):
        if self.rect.y<0:
            self.rect.y=0
            self.fall_vel=5
        elif self.rect.y>HEIGHT-64-BLOCKSIZE//2:
            self.rect.y=HEIGHT-64-BLOCKSIZE//2
    def heal(self,hlPoint):
        if not self.health>=100:
            self.health+=hlPoint
        if DEBUG:
            print(F'New Health = {self.health}')
    def handleJump(self,player1v2):
        if not self.iced:
            if player1v2:
                up,dup=pygame.K_UP,pygame.K_RSHIFT
            else:
                up,dup=pygame.K_w,pygame.K_LSHIFT
            keys = pygame.key.get_pressed()
            if keys[up] and self.onground:
                self.jumpcount=1
                self.fall_vel = -self.jump
                self.onground = False
                self.onblock=False
            if keys[dup] and not self.onground and self.jumpcount==1:
                self.jumpcount=2
                self.fall_vel = -self.jump
    def handleGravity(self,objs):
        if not self.iced:
            GRAVITY = self.grav
            TERMINAL_VELOCITY = 10
            if not self.onblock:
                if not self.onground:
                    self.fall_vel += GRAVITY
                    if self.fall_vel > TERMINAL_VELOCITY:
                        self.fall_vel = TERMINAL_VELOCITY
                    self.rect.y += self.fall_vel
                else:
                    self.fall_vel = 0
                if self.rect.y >= HEIGHT - self.rect.height and not self.onblock:
                    self.rect.y = HEIGHT - self.rect.height
                    self.onground = True
                else:
                    self.onground = False
                self.y_vel = self.fall_vel
            else:
                self.check_on_block(objs)
    def handleAnims(self):
        if self.x_vel!=0 and not self.dash:
            self.state="run_"
        elif self.y_vel<0:
            self.state="fall_"
        elif self.y_vel>0:
            if self.jumpcount==1:
                self.state="jump_"
            elif self.jumpcount==2:
                self.state="fall_"
        else:
            self.state="idle_"
        if self.hit:
            self.state="hit_"
        self.spritesheet=self.sprites[self.state+self.direction]
        if self.iced:
            if self.onblock:
                self.rect.bottom=HEIGHT-87
            self.spritesheet=ICED["iced_right"]
    def handleDraw(self):
        if self.i<len(self.spritesheet):
            if (next(self.frcount)+3)%ANISPEED==0:
                self.spritetoDraw=self.spritesheet[self.i]
                self.i+=1
            else:
                self.spritetoDraw=self.spritetoDraw
        else:
            self.spritetoDraw=self.spritetoDraw
            self.i=0
            if self.hit:
                self.hitC+=1
                if self.hitC>self.AniIters:
                    self.hit=False
                    self.hitC=0
            if self.iced:
                self.icedC+=1
                if self.icedC>self.AniIters:
                    self.iced=False
                    self.icedC=0
    def updatemasks(self):
        self.mask=pygame.mask.from_surface(self.spritetoDraw)
    def land(self):
        self.onground=True
        self.fall_vel=0
        self.onblock=True
        self.y_vel=0
    def hitHead(self):
        self.fall_vel=0
    def check_on_block(self, objs):
        self.onblock = False
        self.onground = False
        margin = int(self.rect.width * 0.2)
        stand_width = self.rect.width - 2 * margin
        self.standing_rect = pygame.Rect(self.rect.x + margin,self.rect.bottom + 1,stand_width,2)
        for obj in objs:
            if self.standing_rect.colliderect(obj.rect):
                self.onblock = True
                self.onground = True
                break
    def TrapColl(self,DMG,player2):
        global GAMERESET
        if not self.Parry:
            self.hit=True
            self.health-=DMG
            if self.health<=0:
                GAMERESET=True
            if DEBUG:
                print(F'New Health = {self.health}')
            self.AniIters=3
        else:
            player2.TrapColl(DMG,self)
    def Iced(self):
        self.iced=True
        self.AniIters=60
    def loop(self, isplayer2, objs,player2):
        handle_vertical_coll(self,objs,player2,isplayer2)
        self.handleJump(isplayer2)
        self.handleGravity(objs)
        self.handleAnims()
        self.handlemove(self.vel, isplayer2,40,player2,objs)
        self.updatemasks()
        self.handleDraw()
        self.checkOut()
        for i,trap in enumerate(self.traps):
            Cd=trap.loop(self,player2)
            self.Cooldowns[i]=Cd
        # self.tramp.loop(self,player2)
        if self.Parry:
            WIN.blit(BUBBLE["bubble_right"][0],self.rect)
def settingupVars(ran=False,colors=["Blue"]):
    global dts,twh
    tpath=os.path.join(PATH,"Background")
    if ran==True:
        dts=[]
        for tile in os.listdir(tpath):
            dts.append(os.path.join(tpath,tile))
        twh=[]
        for i in dts:
            img=pygame.image.load(i)
            s=abimg(img)
            twh.append(s)
    else:
        twh=[]
        for i in colors:
            path=os.path.join(tpath,i+".png")
            img=pygame.image.load(path)
            s=abimg(img)
            twh.append(s)
settingupVars(RAN,COLORS)
def load_block(size,blocksize):
    path=os.path.join(PATH,"Terrain","Terrain.png")
    img=pygame.image.load(path)
    surface=pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect=pygame.Rect(96,BLOCK,size,size)
    surface.blit(img,(0,0),rect)
    return pygame.transform.scale(surface,(blocksize,blocksize))
class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__()
        self.rect=pygame.Rect(x,y,width,height)
        self.image=pygame.Surface((width,height),pygame.SRCALPHA)
        self.width=width
        self.heigh=height
        self.name=name
class Genblock(Object):
    def __init__(self,x,y,width,height):
        super().__init__(x,y,width,height)
        block=load_block(48,BLOCKSIZE)
        self.image.blit(block,(0,0))
        self.mask=pygame.mask.from_surface(self.image)
    def Draw(self):
        WIN.blit(self.image,self.rect)
def getBgPos(twh):
    tpos=[]
    for i in range(WIDTH//2+1):
        for j in range(HEIGHT//2+1):
            randtile=random.choice(twh)
            pos=(i*twh[0][1],j*twh[0][2])
            tpos.append((pos,randtile[0]))
    return tpos
fr1=genframeVal()
def draw(bg,objs,hitbox1,sprite1,mask1,hitbox2=None,sprite2=None,mask2=None):
    for obj in objs:
        obj.Draw()
    if DEBUG:
        pygame.draw.rect(WIN,(0,0,0),hitbox1)
        pygame.draw.rect(WIN,(0,0,0),hitbox2)
    WIN.blit(sprite1,hitbox1)
    WIN.blit(sprite2,hitbox2)

def cachebg(tile):
    img=pygame.Surface((WIDTH,HEIGHT))
    for i in tile:
        img.blit(i[1],i[0])
    return img
class Game:
    def __init__(self):
        self.player2=Player(WIDTH-128,HEIGHT-64-BLOCKSIZE//2,VEL,0.5,12,"MaskDude","left",True)
        self.player1=Player(64,HEIGHT-64-BLOCKSIZE//2,VEL,0.5,12,"VirtualGuy","right",False)
        self.blocks=[Genblock(i*BLOCKSIZE,HEIGHT-BLOCKSIZE//2,BLOCKSIZE,BLOCKSIZE) for i in range(-WIDTH//BLOCKSIZE,WIDTH*2//BLOCKSIZE)]
        self.blocks.append(Genblock(404,300,BLOCKSIZE,BLOCKSIZE))
        self.blocks.append(Genblock(500,300,BLOCKSIZE,BLOCKSIZE))
        self.blocks.append(Genblock(104,140,BLOCKSIZE,BLOCKSIZE))
        self.blocks.append(Genblock(200,140,BLOCKSIZE,BLOCKSIZE))
        self.blocks.append(Genblock(804,200,BLOCKSIZE,BLOCKSIZE))
        self.blocks.append(Genblock(900,200,BLOCKSIZE,BLOCKSIZE))
        self.tile=getBgPos(twh)
        self.clock=pygame.time.Clock()
        self.run=True
        self.img=cachebg(self.tile)
        self.tile=getBgPos(twh)
    def Loop(self):
        self.clock.tick(FPS)
        WIN.blit(self.img,(0,0))
        self.player1.loop(False,self.blocks,self.player2)
        self.player2.loop(True,self.blocks,self.player1)
        draw(self.img,self.blocks,self.player1.rect,self.player1.spritetoDraw,self.player1.mask,self.player2.rect,self.player2.spritetoDraw,self.player2.mask)
        pygame.display.update()
def clamp(v, scale=50):
    return max(-1, min(1, v/scale))
def calculateNearestTrap(p1, p2):
    def nearest_for(player, traps, enemy):
        nearest = None
        min_dist = float("inf")
        for trap in traps:
            for instance in trap.traps:
                trap_center = pygame.Vector2(instance.rect.center)
                enemy_center = pygame.Vector2(enemy.rect.center)
                dist = (trap_center - enemy_center).length()
                if dist < min_dist:
                    min_dist = dist
                    nearest = trap_center - enemy_center
        if nearest is None:
            return [0, 0, 0, 0]
        dx, dy = nearest.x, nearest.y
        return [
            1 if dy < 0 else 0,
            1 if dy > 0 else 0,
            1 if dx < 0 else 0,
            1 if dx > 0 else 0
        ]

    outP1 = nearest_for(p1, p2.traps, p1)
    outP2 = nearest_for(p2, p1.traps, p2)
    return [outP1, outP2]
             
def getState(p1,p2):
    p1Pos_x,p1Pos_y,p1Vel_x,p1Vel_y,p1_OnGND,p1Dir,p1Health,p1CDS=p1.rect.x/WIDTH if not p1.Invis else 0,p1.rect.y/HEIGHT  if not p1.Invis else 0,p1.x_vel,p1.fall_vel,1 if p1.onground else 0,1 if p1.direction=="right" else 0,p1.health/100,p1.Cooldowns
    p2Pos_x,p2Pos_y,p2Vel_x,p2Vel_y,p2_OnGND,p2Dir,p2Health,p2CDS=p2.rect.x/WIDTH  if not p2.Invis else 0 ,p2.rect.y/HEIGHT  if not p2.Invis else 0,p2.x_vel,p2.fall_vel ,1 if p2.onground else 0,1 if p2.direction=="right" else 0,p2.health/100,p2.Cooldowns
    dx = (p2.rect.centerx - p1.rect.centerx)/WIDTH
    dy = (p2.rect.centery - p1.rect.centery)/HEIGHT
    p1perAbs=[1 if p1.dash else 0, 1 if p1.Invis else 0, 1 if p1.Parry else 0]
    p2perAbs=[1 if p2.dash else 0, 1 if p2.Invis else 0, 1 if p2.Parry else 0]
    p1Vel_x,p1Vel_y,p2Vel_x,p2Vel_y=clamp(p1Vel_x),clamp(p1Vel_y),clamp(p2Vel_x),clamp(p2Vel_y)
    nearestTrap=calculateNearestTrap(p1,p2)
    p1NearTraps,p2NearTraps=nearestTrap[0],nearestTrap[1]
    p1Out=[p1Pos_x,p1Pos_y,p1Vel_x,p1Vel_y,p1_OnGND,p1Dir,p1Health,dx,dy]
    p1Out.extend(p1CDS)
    p1Out.extend(p1NearTraps)
    p1Out.extend(p1perAbs)
    p1Out.extend(p2perAbs)
    p2Out=[p2Pos_x,p2Pos_y,p2Vel_x,p2Vel_y,p2_OnGND,p2Dir,p2Health,dx,dy]
    p2Out.extend(p2CDS)
    p2Out.extend(p2NearTraps)
    p2Out.extend(p2perAbs)
    p2Out.extend(p1perAbs)
    return [p1Out,p2Out]
if __name__=="__main__":
    game=Game()
    run=True
    startTime=0
    while run:
        CurrentTime=time.time()
        game.Loop()
        state=getState(game.player1,game.player2)
        print(state)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
                pygame.quit()
        if GAMERESET:
            GAMERESET=False
            time.sleep(0.5)
            game.__init__()
        if CurrentTime-startTime>=GAMETIME:
            GAMERESET=True
            startTime=CurrentTime
            