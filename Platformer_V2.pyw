import os 
import pygame
import random
import math
import numpy as np
import threading
import time
pygame.init()
pygame.display.set_caption("A Platformer Game")
WIDTH,HEIGHT=1000,600
FPS=60
VEL=5
RAN=True
COLORS=["Brown"]
ANISPEED=3
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
file=os.path.abspath(__file__).split("\\")
file=file[0:len(file)-1]
fpath="\\".join(file)
PATH=os.path.join(fpath,"assets")
FILEPATH=fpath
print(PATH)
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
        print(name)
        all_anims[name + "_right"] = anims
        all_anims[name + "_left"] = flipimg(anims)
    return all_anims
SAW=loadSpriteSheets(os.path.join(PATH,"Traps\Saw\on.png"),None,38,38)
ICE=loadSpriteSheets(os.path.join(PATH,r"Traps\Iced\ball.png"),None,16,16)
ICED=loadSpriteSheets(os.path.join(PATH,"Traps\Iced\iced.png"),None,48,48)
FIRE=loadSpriteSheets(os.path.join(PATH,"Traps\Fire\on.png"),None,16,32)
SPIKEBLOCK=loadSpriteSheets(os.path.join(PATH,"Traps"),"Spike Head",54,52)
DISSAPEARING=loadSpriteSheets(r"C:\PYTHON\PyGame YAY!!!\Python-Platformer-main\assets\MainCharacters\Disappearing.png",None,32,32,2)
APPEARING=loadSpriteSheets(r"C:\PYTHON\PyGame YAY!!!\Python-Platformer-main\assets\MainCharacters\Appearing.png",None,32,32)
TRAMPOLINE_IDLE=loadSpriteSheets(os.path.join(PATH,"Traps\Trampoline\Idle.png"),None,28,28)
TRAMPOLINE_JUMP=loadSpriteSheets(os.path.join(PATH,"Traps\Trampoline\Jump.png"),None,28,28)
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
    def CheckExpire(self,outofScreen=True,expireT=3,hit=False):
        for trap in self.traps[:]:
            if not outofScreen:
                if time.time()-trap.start>=expireT:
                    trap.expired=True
            if outofScreen:
                if trap.rect.x>WIDTH or trap.rect.x<0:
                    trap.expired=True
            if hit:
                if self.trapped:
                    self.traps.remove(trap)
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
    def checkPress(self,player):
        currenttime=time.time()
        keys=pygame.key.get_pressed()
        if keys[self.key] and currenttime-self.lastTime>=self.cooldown:
            trap = TrapInstance(self.rect,self.player.direction,self.mask)
            self.traps.append(trap)
            self.lastTime=currenttime
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
    def collision(self,player1,player2):
        for trap in self.traps:
            if player1:
                if pygame.sprite.collide_mask(trap,player1):
                    player1.TrapColl()
                    self.trapped=True
            if pygame.sprite.collide_mask(trap,player2):
                player2.TrapColl()
                self.trapped=True
            else:
                self.trapped=False
class Fire(Traps):
    def __init__(self,player,key):
        super().__init__(player,FIRE,1,key,"on")
        self.w=32
        self.h=16
    def loop(self,player,player2):
        self.rect=pygame.Rect(self.player.rect.x+self.player.rect.width if self.player.direction=="right" else self.player.rect.x-self.player.rect.width,self.player.rect.bottom-32-BLOCKSIZE//2,self.w,self.h)
        super().CheckExpire(False,3)
        super().checkPress(player)
        super().updateAni()
        super().collision(player,player2)
class Trampoline(Traps):
    def __init__(self,player,key,x,y):
        super().__init__(player,TRAMPOLINE_IDLE,3,key,"Idle")
        self.w=28
        self.h=28
        self.x=x
        self.y=y
        self.jump=False
        self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
        # self.mask=pygame.mask.from_surface(TRAMPOLINE_IDLE["Idle_right"][0])
        super().spawnIndefinite()
    def collision(self,player1,player2):
        for trap in self.traps:
            currenttime=time.time()
            if pygame.sprite.collide_mask(trap,player1) and currenttime-self.lastTime>=self.cooldown:
                self.spritesheet=TRAMPOLINE_JUMP
                self.name="Jump"
                player1.fall_vel = -50
                player1.onground = False
                player1.onblock=False
                self.lastTime=currenttime
            if pygame.sprite.collide_mask(trap,player2) and currenttime-self.lastTime>=self.cooldown:
                self.spritesheet=TRAMPOLINE_JUMP
                self.name="Jump"
                player2.fall_vel = -50
                player2.onground = False
                player2.onblock=False
                self.lastTime=currenttime  
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
        super().__init__(player,SAW,1,key,"on")
        self.w=38
        self.h=38
    def loop(self,player,player2):
        self.rect=pygame.Rect(self.player.rect.x+self.player.rect.width if self.player.direction=="right" else self.player.rect.x-self.player.rect.width,self.player.rect.bottom-32-BLOCKSIZE//1.5,self.w,self.h)
        super().CheckExpire(True,None,True)
        super().checkPress(player)
        super().move(15)
        super().updateAni()
        super().collision(None,player2)
class Ice(Traps):
    def __init__(self,player,key):
        super().__init__(player,ICE,1,key,"ball")
        self.w=20
        self.h=17
    def collision(self,player2):
        for trap in self.traps:
            if pygame.sprite.collide_mask(trap,player2):
                player2.Iced()
    def loop(self,player,player2):
        self.rect=pygame.Rect(self.player.rect.x+self.player.rect.width if self.player.direction=="right" else self.player.rect.x-self.player.rect.width,self.player.rect.bottom-32-BLOCKSIZE//4,self.w,self.h)
        super().CheckExpire(True)
        super().checkPress(player)
        super().move(15)
        super().updateAni()
        self.collision(player2)
class SpikeBlock(Traps):
    def __init__(self,player,key,player2):
        super().__init__(player,SPIKEBLOCK,1,key,"blink")
        self.w=38
        self.h=38
        self.player2=player2
        self.rect=pygame.Rect(self.player2.rect.x,0,54,52)
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
        self.rect=pygame.Rect(self.player2.rect.x-25,0,54,52)
        super().CheckExpire(True)
        super().checkPress(player)
        super().move(15,False,player2,False,self.stop)
        super().updateAni(self.anicount,self.anispeed)
        super().collision(None,player2)
        self.checkGroundColl()
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
    if self.rect.colliderect(player2.rect):
        if self.y_vel>0:
            keys=pygame.key.get_pressed()
            if keys[up]:
                self.fall_vel-=self.jump*2
            self.rect.bottom=player2.rect.top
class Player(pygame.sprite.Sprite):
    fr2=genframeVal()
    def __init__(self,x,y,vel,grav,jump,player,dir="right"):
        super().__init__()
        self.sprites=loadSpriteSheets("MainCharacters",player,32,32,None,(80,80))
        exsprite=pygame.Surface.get_rect(self.sprites["idle_right"][0])
        self.rect=pygame.Rect(x,y,exsprite.width,exsprite.height)
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
        self.lastdash=0
        self.dashframes=10
        self.dash=False
    def handlemove(self,vel,player1v2,dashVel,player2,objs):
        if not self.iced:
            if player1v2:
                right,left,dash1=pygame.K_RIGHT,pygame.K_LEFT,pygame.K_DOWN
            else:
                right,left,dash1=pygame.K_d,pygame.K_a,pygame.K_s
            keys=pygame.key.get_pressed()
            coll_right=handle_horizontal_coll(self,objs,VEL,player2)
            coll_left=handle_horizontal_coll(self,objs,-VEL,player2)
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
                if keys[dash1] and time.time()-self.lastdash>=2:
                    self.dash=True
                    self.lastdash=time.time()
            elif self.dash:
                self.spritesheet=DISSAPEARING["Disappearing_right"]
                self.dashframes-=1
                self.rect.x+=dashVel if self.direction=="right" and self.rect.x<(WIDTH-self.rect.width) else -dashVel if self.rect.x>0 else 0
                if self.rect.colliderect(player2.rect):
                    player2.TrapColl()
                if self.dashframes<=0:
                    self.spritesheet=DISSAPEARING["Disappearing_right"]
                    self.dash=False
                    self.dashframes=10
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
    def TrapColl(self):
        self.hit=True
        self.AniIters=3
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
    # pygame.draw.rect(WIN,(0,0,0),hitbox1)
    WIN.blit(sprite1,hitbox1)
    if sprite2:
        # pygame.draw.rect(WIN,(0,0,0),hitbox2)
        WIN.blit(sprite2,hitbox2)
    
def cachebg(tile):
    img=pygame.Surface((WIDTH,HEIGHT))
    for i in tile:
        img.blit(i[1],i[0])
    return img

def main():
    player1=Player(64,HEIGHT-64-BLOCKSIZE//2,VEL,0.5,12,"VirtualGuy")
    player2=Player(WIDTH-128,HEIGHT-64-BLOCKSIZE//2,VEL,0.5,12,"MaskDude","left")
    blocks=[Genblock(i*BLOCKSIZE,HEIGHT-BLOCKSIZE//2,BLOCKSIZE,BLOCKSIZE) for i in range(-WIDTH//BLOCKSIZE,WIDTH*2//BLOCKSIZE)]
    blocks.append(Genblock(404,300,BLOCKSIZE,BLOCKSIZE))
    blocks.append(Genblock(500,300,BLOCKSIZE,BLOCKSIZE))
    blocks.append(Genblock(104,70,BLOCKSIZE,BLOCKSIZE))
    blocks.append(Genblock(200,70,BLOCKSIZE,BLOCKSIZE))
    blocks.append(Genblock(804,200,BLOCKSIZE,BLOCKSIZE))
    blocks.append(Genblock(900,200,BLOCKSIZE,BLOCKSIZE))
    tile=getBgPos(twh)
    clock=pygame.time.Clock()
    run=True
    fire1=Fire(player1,pygame.K_f)
    fire2=Fire(player2,pygame.K_p)
    saw1=Saw(player1,pygame.K_q)
    saw2=Saw(player2,pygame.K_l)
    ice1=Ice(player1,pygame.K_e)
    ice2=Ice(player2,pygame.K_o)
    spikeball1=SpikeBlock(player1,pygame.K_r,player2)
    spikeball2=SpikeBlock(player2,pygame.K_k,player1)
    tramp1=Trampoline(player1,None,100,HEIGHT-115)
    tramp2=Trampoline(player2,None,900,HEIGHT-115)
    img=cachebg(tile)
    tile=getBgPos(twh)
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False  
        WIN.blit(img,(0,0))
        player1.loop(False,blocks,player2)
        player2.loop(True,blocks,player1)
        draw(img,blocks,player1.rect,player1.spritetoDraw,player1.mask,player2.rect,player2.spritetoDraw,player2.mask)
        fire1.loop(player1,player2)
        fire2.loop(player2,player1)
        saw1.loop(player1,player2)
        saw2.loop(player2,player1)
        ice1.loop(player1,player2)
        ice2.loop(player2,player1)
        spikeball1.loop(player1,player2)
        spikeball2.loop(player2,player1)
        tramp1.loop(player1,player2)
        tramp2.loop(player1,player2)
        pygame.display.update()
    pygame.quit()
    quit()
if __name__=="__main__":
    main()