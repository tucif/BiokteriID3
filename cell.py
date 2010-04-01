import math,random
import gtk, gobject, cairo

from sprite import Sprite
from constants import WINDOW_SIZE

DEFAULT_WIDTH=50
DEFAULT_HEIGHT=50

COLOR_LIST=[("Red",[0.8,0.2,0.1]),("Green",[0,0.8,0.3]),("Blue",[0,0.8,0.8])]

OUTER_SHAPE_LIST=["Simple","CircleStroke","CircleFill","Square","DoubleSquare"]
ROT_DIRECTION_LIST=[("Left",-1),("Right",1)]
INNER_SHAPE_LIST=["None","CircleStroke","CircleFill","SquareStroke","SquareFill"]

class Cell(Sprite):
    def __init__(self, posX=0, posY=0,
                 tempLevel = 0,
                 phLevel= 0,
                 aggresiveness=0,
                 visibility=0
                 ):
        Sprite.__init__(self,posX,posY)
        self.width=DEFAULT_WIDTH
        self.height=DEFAULT_HEIGHT
        self.maxHp=1000
        self.hp=self.maxHp
        self.isDead=False
        self.velX=0.0
        self.velY=0.0

        #rotation
        self.deltaRot=0.05
        self.rotDirection=-1
        self.rot=0

        #attributes
        self.outerShape=random.choice(OUTER_SHAPE_LIST)
        self.outerColor,self.outerColorList=random.choice(COLOR_LIST)
        self.outerRotation,self.outerRotationVal=random.choice(ROT_DIRECTION_LIST)

        self.innerShape=random.choice(INNER_SHAPE_LIST)
        self.innerColor,self.innerColorList=random.choice(COLOR_LIST)

    def __str__(self):
        return "Cell"

    def get_type(self):
        return "Cell"

    def update(self):
        Sprite.update(self)
        self.rot+=self.deltaRot*self.rotDirection

        if self.hp<=0:
            self.isDead=True
        else:
            self.isDead=False;

    def paint(self,window):
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
            window.arc(self.posX+self.width/2, self.posY+self.height/2, 25, 0.5, 2 * math.pi)
            window.set_source_rgb(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2])
            window.set_line_width(1)
            window.stroke()
            window.restore()
            window.save()
            cairo.Matrix.translate(ThingMatrix, 25,6)
            window.transform ( ThingMatrix )
            if self.outerShape=="CircleStroke":
                window.arc(self.posX+self.width/2, self.posY+self.height/2, 7, 0.0, 2 * math.pi)
                window.set_source_rgb(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2])
                window.stroke()
            if self.outerShape=="CircleFill":
                window.arc(self.posX+self.width/2, self.posY+self.height/2, 7, 0.0, 2 * math.pi)
                window.set_source_rgb(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2])
                window.fill_preserve()
                window.stroke()
            window.restore()

        if self.outerShape=="Square" or self.outerShape=="DoubleSquare":
            window.set_source_rgb(self.outerColorList[0],self.outerColorList[1],self.outerColorList[2])
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
        window.set_source_rgba(self.innerColorList[0],self.innerColorList[1],self.innerColorList[2])
        window.save()
        window.set_line_width(1)

        if self.innerShape=="CircleStroke":
            window.arc(self.posX+self.width/2, self.posY+self.height/2, 10, 0, 2 * math.pi)
            window.stroke()
        if self.innerShape=="CircleFill":
            window.arc(self.posX+self.width/2, self.posY+self.height/2, 10, 0, 2 * math.pi)
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