import random
import math
import gtk, gobject, cairo

from sprite import Sprite
from constants import VIRUS_IMAGE
from constants import WINDOW_SIZE
from constants import TRAINING_ZONE_LIMIT

DEFAULT_WIDTH=50
DEFAULT_HEIGHT=50

MAX_PUSH_PARTICLES=50

STATUS=["NoTarget","Analyzing","Attacking","Defending"]

class Virus(Sprite):
    def __init__(self, posX=0, posY=0,
                 ):
        Sprite.__init__(self,posX,posY)
        self.width=DEFAULT_WIDTH
        self.height=DEFAULT_HEIGHT
        self.color=(1,1,1)
        self.maxHp=1000
        self.hp=self.maxHp
        self.isDead=False
        self.baseVelX=2
        self.baseVelY=2
        self.velX=0
        self.velY=0

        self.deltaTransX=0.1
        self.deltaTransY=0.1
        self.transVelX=0
        self.transVelY=0

        self.imagen=VIRUS_IMAGE
        self.targetCell=None
        self.status="Attacking"

        #movement
        self.degreeRotY=random.random()
        self.degreeRotX=random.random()

        self.limitMax=100
        self.limitMin=100

        #effects
        self.pushParticles=[]
    
        #rotation
        self.transDeltaRot=0
        self.deltaRot=0.1
        self.deltaDeltaRot=0.001

        self.rotDirection=1
        self.rot=0

    def __str__(self):
        return "Virus: %s" % (self.status)

    def get_type(self):
        return "Virus"

    def attack(self):
        self.status="Attacking"

    def analyze(self):
        self.status="Analyzing"

    def defend(self):
        self.status="Defending"

    def eat(self):
        self.status="Eating"

    def update(self,state):
        Sprite.update(self)
        
        if state=="Running":
            for particle in self.pushParticles:
                particle.update()
            if abs(self.transVelY-self.velY)<=self.deltaTransY*2:
                self.trasnVelY=self.velY
            elif self.transVelY < self.velY:
                self.transVelY+=self.deltaTransY
            elif self.transVelY > self.velY:
                self.transVelY-=self.deltaTransY

            if abs(self.transVelX-self.velX)<=self.deltaTransX*2:
                self.transVelX=self.velX
            elif self.transVelX < self.velX:
                self.transVelX+=self.deltaTransX
            elif self.transVelX > self.velX:
                self.transVelX-=self.deltaTransX

            if abs(self.transDeltaRot-self.deltaRot)<=self.deltaDeltaRot*2:
                self.transDeltaRot=self.deltaRot
            elif self.transDeltaRot < self.deltaRot:
                self.transDeltaRot+=self.deltaDeltaRot
            elif self.transDeltaRot > self.deltaRot:
                self.transDeltaRot-=self.deltaDeltaRot

            self.rot+=self.transDeltaRot*self.rotDirection

            self.degreeRotY+=self.deltaRot
            if self.degreeRotY>360:
                self.degreeRotY=0

            if self.hp<=0:
                self.isDead=True
            else:
                self.isDead=False;

            self.posX+=self.transVelX
            self.posY+=self.transVelY
            self.posY+=math.sin(self.degreeRotY)
            self.posX+=math.sin(self.degreeRotX)

            if self.targetCell:
                #Get close to target
                (myX,myY)=self.get_center()
                (targetX,targetY)=self.targetCell.get_center()
                absX=abs(myX-targetX)
                absY=abs(myY-targetY)

                if absX >self.limitMax:
                    if myX<targetX:
                        self.velX=self.baseVelX
                    elif self.posX+self.width:
                        self.velX=-self.baseVelX

                elif absX<self.limitMin:
                    if myX<targetX:
                        self.velX=-self.baseVelX
                    else:
                        self.velX=+self.baseVelX
                else:
                    self.velX=0

                if absY >self.limitMax:
                    if myY<targetY:
                        self.velY=self.baseVelY
                    else:
                        self.velY=-self.baseVelY
                elif absY<self.limitMin:
                    if myY<targetY:
                        self.velY=-self.baseVelY
                    else:
                        self.velY=+self.baseVelY
                else:
                    self.velY=0
                if self.status=="Analyzing":
                    self.deltaRot=0
                    self.limitMax=100
                    self.limitMin=100
                    if self.degreeRotX==0:
                        self.degreeRotX=random.random()
                    if self.degreeRotY==0:
                        self.degreeRotY=random.random()
                if self.status=="Attacking":
                    self.deltaRot=0.1
                    self.limitMax=20
                    self.limitMin=1
                    self.degreeRotY=0
                    self.degreeRotX=0
                if self.status=="Defending":
                    self.limitMax=350
                    self.limitMin=200
                if self.status=="Eating":
                    self.limitMax=100
                    self.limitMin=50
                    
            else:
                self.velX=0
                self.velY=0
                self.deltaRot=0
                self.status="NoTarget"

            if self.posY<=0:
                self.posY=0
            if self.posY+self.height>=TRAINING_ZONE_LIMIT:
                self.posY=TRAINING_ZONE_LIMIT-self.width
            if self.posX<=0:
                self.posX=0
            if self.posX+self.width>=WINDOW_SIZE:
                self.posX=WINDOW_SIZE-self.width

    def paint(self,window):
        for particle in self.pushParticles:
            particle.paint(window)

        pixbuf = self.imagen
        pixbuf1=pixbuf.scale_simple(self.width,self.height,gtk.gdk.INTERP_BILINEAR)

        #visibility representation
        window.save()
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        window.transform ( ThingMatrix )
        cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
        cairo.Matrix.rotate( ThingMatrix, self.rot) # Do the rotation
        cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
        window.transform ( ThingMatrix ) # and commit it to the context
        window.set_source_pixbuf(pixbuf1,self.posX,self.posY)
        window.paint()
        window.restore()

        if self.targetCell!=None:
            window.save()
            window.move_to(self.posX+self.width/2,self.posY+self.height/2)
            window.line_to(self.targetCell.posX+self.targetCell.width/2,
                self.targetCell.posY+self.targetCell.height/2)
            if self.status=="Analyzing":
                window.set_source_rgb(1,1,0)
            if self.status=="Attacking":
                window.set_source_rgb(1,0,0)
            if self.status=="Defending":
                window.set_source_rgb(0,1,1)
            if self.status=="Eating":
                window.set_source_rgb(0,1,0)

            window.stroke()
            window.restore()


