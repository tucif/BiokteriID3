import math
import random
import gtk, gobject, cairo

from sprite import Sprite
from dyingParticle import DyingParticle
from constants import WINDOW_SIZE

from operator import indexOf

DEFAULT_WIDTH=45
DEFAULT_HEIGHT=45

COLOR_LIST=[("Red",[0.8,0.2,0.1]),("Green",[0,0.8,0.3]),("Blue",[0,0.8,0.8])]

OUTER_SHAPE_LIST=["Simple","CircleStroke","CircleFill","Square","DoubleSquare"]
ROT_DIRECTION_LIST=[("Left",-1),("Right",1)]
INNER_SHAPE_LIST=["None","CircleStroke","CircleFill","SquareStroke","SquareFill"]

STATUS_LIST=["Dying","Dead","Repelled"]

MAX_DYING_PARTICLES=40

class Cell(Sprite):
    def __init__(self, posX=0, posY=0, velX=0, velY=0, type="TrainCell"):
        Sprite.__init__(self,posX,posY)
        self.width=DEFAULT_WIDTH
        self.height=DEFAULT_HEIGHT
        self.maxHp=200
        self.hp=self.maxHp
        self.isDead=False

        self.baseVelX=velX
        self.baseVelY=velY
        self.velX=velX
        self.velY=velY

        self.deltaTransX=0.05
        self.deltaTransY=0.05
        self.transVelX=velX
        self.transVelY=velY

        self.type=type
        self.name="Cell"
        #rotation
        self.deltaRot=0.05
        self.transDeltaRot=0.05
        self.deltaDeltaRot=0.0005
        self.rotDirection=-1
        self.rot=0
        self.status=None


        #movement
        self.degreeRot=0
        self.deltaDegreeRot=random.random()/15

        #effects
        self.dyingParticles=[]

        #attributes
        self.outerShape=random.choice(OUTER_SHAPE_LIST)
        self.outerColor,self.outerColorList=random.choice(COLOR_LIST)
        self.outerRotation,self.outerRotationVal=random.choice(ROT_DIRECTION_LIST)

        self.innerShape=random.choice(INNER_SHAPE_LIST)
        if self.innerShape=="None":
            self.innerColor,self.innerColorList=("Black",[0,0,0])
        else:
            self.innerColor,self.innerColorList=random.choice(COLOR_LIST)

    def get_characteristic(self,characName):
        if characName == "outerShape":
            return self.outerShape
        if characName == "outerColor":
            return self.outerColor
        if characName == "outerRotation":
            return self.outerRotation
        if characName == "innerShape":
            return self.innerShape
        if characName == "innerColor":
            return self.innerColor

    def __str__(self):
        return self.name

    def get_type(self):
        return "Cell"

    def update(self,state,limits=[0,WINDOW_SIZE,0,WINDOW_SIZE]):
        Sprite.update(self)

        self.rot+=self.transDeltaRot*self.rotDirection
        self.degreeRot+=self.deltaDegreeRot

        if self.hp<=0:
            self.isDead=True
        else:
            self.isDead=False;

        if state=="Running":
            if self.type=="TrainCell":
                self.posX+=self.velX
                self.posY+=self.velY*math.cos(self.degreeRot)
                if self.posX<=limits[0] or self.posX>=limits[1]:
                    self.velX*=-1
                if self.posY<=limits[2] or self.posY>=limits[3]:
                    self.velY*=-1
            else:
                if abs(self.transDeltaRot-self.deltaRot)<=self.deltaDeltaRot*2:
                    self.transDeltaRot=self.deltaRot
                elif self.transDeltaRot < self.deltaRot:
                    self.transDeltaRot+=self.deltaDeltaRot
                elif self.transDeltaRot > self.deltaRot:
                    self.transDeltaRot-=self.deltaDeltaRot

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

                self.posX+=self.transVelX
                self.posY+=self.transVelY

            if self.status == "defended":
                self.velX -= 0.1

            if self.status=="BeingEaten":
                self.deltaRot=0
                self.velX=0
                self.velY=0
                if self.hp>0:
                    self.hp-=1
                else:
                    self.hp=0
                    self.status="Eaten"

                if len(self.dyingParticles)<MAX_DYING_PARTICLES:
                    self.dyingParticles.append(DyingParticle(random.randint(int(self.posX),int(self.posX+self.width)),random.randint(int(self.posY),int(self.posY+self.height)),
                        random.random()*(pow(-1,random.randint(1,2)))*0.5,random.random()*(pow(-1,random.randint(1,2)))*0.5,0.7,100))

            elif self.status=="Eaten":
                #do something
                self.status="Dead"

            if self.status=="Dying":
                self.deltaRot=0
                self.velX=0
                self.velY=0
                if self.hp>0:
                    self.hp-=1
                else:
                    self.hp=0
                    self.status="LastBreath"

                if len(self.dyingParticles)<MAX_DYING_PARTICLES:
                    self.dyingParticles.append(DyingParticle(random.randint(int(self.posX),int(self.posX+self.width)),random.randint(int(self.posY),int(self.posY+self.height)),
                        random.random()*(pow(-1,random.randint(1,2))),random.random()*(pow(-1,random.randint(1,2)))))

            elif self.status=="LastBreath":
                for particle in self.dyingParticles:
                    (centerX,centerY)=particle.get_center()
                    (cellX,cellY)=self.get_center()
                    if centerX<cellX:
                        particle.velX=-10
                    else:
                        particle.velX=10

                    if centerY<cellY:
                        particle.velY=-10
                    else:
                        particle.velY=10
                    self.status="LastBreath2"

            elif self.status=="LastBreath2":
                angleDivision=360.0/MAX_DYING_PARTICLES
                newParticles=[DyingParticle(self.posX+self.width/2,self.posY+self.height/2,math.sin(angleDivision*i)*10,math.cos(angleDivision*i)*10) for i in xrange(MAX_DYING_PARTICLES)]
                newParticles2=[DyingParticle(self.posX+self.width/2,self.posY+self.height/2,math.sin(angleDivision*i)*5,math.cos(angleDivision*i)*5) for i in xrange(MAX_DYING_PARTICLES)]

                for particle in newParticles:
                    particle.lifeTime=100
                    self.dyingParticles.append(particle)
                for particle in newParticles2:
                    particle.lifeTime=200
                    self.dyingParticles.append(particle)

                self.status="Dead"

            particlesToPop=[]
            for particle in self.dyingParticles:
                particle.update()

                if particle.posX+particle.width<0 or particle.posX>WINDOW_SIZE or particle.posY+particle.height<0 or particle.posY>WINDOW_SIZE or particle.lifeTime<=0:
                    particlesToPop.append(particle)

            for particle in particlesToPop:
                self.dyingParticles.pop(indexOf(self.dyingParticles,particle))


    def paint(self,window):
        window.stroke() #patch to prevent a stray line from appearing between text and cells

        for particle in self.dyingParticles:
            particle.paint(window)

        window.save()
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        window.transform ( ThingMatrix )
        cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
        cairo.Matrix.rotate( ThingMatrix, self.outerRotationVal*self.rot)
        cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
        window.transform ( ThingMatrix ) # and commit it to the context

        #draw outer shape
        window.set_line_width(1)
        if self.outerShape=="Simple" or self.outerShape=="CircleStroke" or self.outerShape=="CircleFill":
            window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width/2, 0.5, 2 * math.pi)
            window.set_source_rgba(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2],self.hp*1.0/self.maxHp)
            window.set_line_width(1)
            window.stroke()
            window.restore()
            window.save()
            cairo.Matrix.translate(ThingMatrix, self.width/2,self.width*0.12)
            window.transform ( ThingMatrix )
            if self.outerShape=="CircleStroke":
                window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width*0.14, 0.0, 2 * math.pi)
                window.set_source_rgba(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2],self.hp*1.0/self.maxHp)
                window.stroke()
            if self.outerShape=="CircleFill":
                window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width*0.14, 0.0, 2 * math.pi)
                window.set_source_rgba(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2],self.hp*1.0/self.maxHp)
                window.fill_preserve()
                window.stroke()
            window.restore()

        if self.outerShape=="Square" or self.outerShape=="DoubleSquare":
            window.set_source_rgba(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2],self.hp*1.0/self.maxHp)
            window.rectangle(self.posX,self.posY,self.width, self.height)
            window.stroke()
            if self.outerShape=="DoubleSquare":
                window.save()
                ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
                window.transform ( ThingMatrix )
                cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
                cairo.Matrix.rotate( ThingMatrix, 4 )
                cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
                window.transform ( ThingMatrix ) # and commit it to the context
                window.rectangle(self.posX,self.posY,self.width, self.height)
                window.stroke()
                window.restore()
            window.restore()
 
        #draw inner shape "None","CircleStroke","CircleFill","SquareStroke","SquareFill"
        if self.innerShape!="None":
            window.set_source_rgba(self.innerColorList[0],self.innerColorList[1],self.innerColorList[2],self.hp*1.0/self.maxHp)

            window.save()
            window.set_line_width(1)

            if self.innerShape=="CircleStroke":
                window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width*0.2, 0, 2 * math.pi)
                window.stroke()
            if self.innerShape=="CircleFill":
                window.arc(self.posX+self.width/2, self.posY+self.height/2, self.width*0.2, 0, 2 * math.pi)
                window.fill()
            if self.innerShape=="SquareStroke" or self.innerShape=="SquareFill":
                ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
                window.transform ( ThingMatrix )
                cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
                cairo.Matrix.rotate( ThingMatrix, math.sin(self.rot))
                cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
                window.transform ( ThingMatrix ) # and commit it to the context
                if self.innerShape=="SquareStroke":
                    window.rectangle((self.posX+self.width/2)-self.width/6,(self.posY+self.height/2)-self.height/6,self.width/3, self.height/3)
                    window.stroke()
                if self.innerShape=="SquareFill":
                    window.rectangle((self.posX+self.width/2)-self.width/6,(self.posY+self.height/2)-self.height/6,self.width/3, self.height/3)
                    window.fill()
            window.restore()