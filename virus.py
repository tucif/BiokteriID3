import random
import gtk, gobject, cairo

from sprite import Sprite
from constants import VIRUS_IMAGE
from constants import WINDOW_SIZE
from constants import MAX_FITNESS

DEFAULT_WIDTH=50
DEFAULT_HEIGHT=50

class Virus(Sprite):
    def __init__(self, posX=0, posY=0,
                 tempLevel = 0,
                 phLevel= 0,
                 aggresiveness=0,
                 visibility=0
                 ):
        Sprite.__init__(self,posX,posY)
        self.width=DEFAULT_WIDTH
        self.height=DEFAULT_HEIGHT
        self.color=(1,1,1)
        self.maxHp=1000
        self.hp=self.maxHp
        self.isDead=False
        self.velX=0.0
        self.velY=0.0

        #properties transitional values
        self.deltaTrans=1.0
        self.transTempLevel= tempLevel    #0~127
        self.transPhLevel= phLevel       #0~15
        self.transAggresiveness=aggresiveness #0~127
        self.transVisibility=visibility    #0~127

        #properties value
        self.tempLevel= tempLevel    #0~127
        self.phLevel= phLevel       #0~15
        self.aggresiveness=aggresiveness #0~127
        self.visibility=visibility    #0~127

        self.fitness=0

        self.transFitnessPercentage=0
        self.fitnessPercentage=0

        self.imagen=VIRUS_IMAGE

        #rotation aggression
        self.deltaRotAggr=0
        self.rot=0

        #rotation radars
        self.deltaRotVis=0
        self.rotVis=0

    def __str__(self):
        return "[%d|%d|%d|%d]" % (self.transTempLevel, self.transPhLevel, self.transAggresiveness, self.transVisibility)

    def get_type(self):
        return "Virus"

    def update_fitness(self,environment):
        self.tempFitness=127-abs(environment.temp-self.tempLevel)
        self.phFitness=127-(abs(environment.ph-self.phLevel))*8.46
        self.reactFitness=127-abs(environment.reactivity-self.aggresiveness)
        self.radarFitness=127-abs(environment.radar-self.visibility)

        self.fitness=self.tempFitness+self.phFitness+self.reactFitness+self.radarFitness

        self.fitnessPercentage=float(self.fitness)*100/MAX_FITNESS

    def update(self):
        Sprite.update(self)
        self.deltaRot=(float(self.transAggresiveness)*100/127)*0.1/100
        self.rot+=self.deltaRot

        self.deltaRotVis=(float(self.transVisibility)*100/127)*0.1/100
        self.rotVis+=self.deltaRotVis

        if self.transTempLevel<self.tempLevel-1:
            self.transTempLevel+=self.deltaTrans
        elif self.transTempLevel>self.tempLevel+1:
            self.transTempLevel-=self.deltaTrans
        elif self.transTempLevel != self.tempLevel:
            self.transTempLevel=self.tempLevel

        if self.transPhLevel<self.phLevel-1:
            self.transPhLevel+=self.deltaTrans/10
        elif self.transPhLevel>self.phLevel+1:
            self.transPhLevel-=self.deltaTrans/10
        elif self.transPhLevel != self.phLevel:
            self.transPhLevel=self.phLevel

        if self.transAggresiveness<self.aggresiveness-1:
            self.transAggresiveness+=self.deltaTrans
        elif self.transAggresiveness>self.aggresiveness+1:
            self.transAggresiveness-=self.deltaTrans
        elif self.transAggresiveness != self.aggresiveness:
            self.transAggresiveness=self.aggresiveness

        if self.transVisibility<self.visibility-1:
            self.transVisibility+=self.deltaTrans
        elif self.transVisibility>self.visibility+1:
            self.transVisibility-=self.deltaTrans
        elif self.transVisibility != self.visibility:
            self.transVisibility=self.visibility

        if self.transFitnessPercentage<self.fitnessPercentage-1:
            self.transFitnessPercentage+=self.deltaTrans/2
        elif self.transFitnessPercentage>self.fitnessPercentage+1:
            self.transFitnessPercentage-=self.deltaTrans/2
        elif self.transFitnessPercentage != self.fitnessPercentage:
            self.transFitnessPercentage=self.fitnessPercentage

        self.posX+=self.velX
        self.posY+=self.velY
        if self.hp<=0:
            self.isDead=True
        else:
            self.isDead=False;

    def paint(self,window):
        pixbuf = self.imagen
        pixbuf1=pixbuf.scale_simple(self.width/4,self.height/4,gtk.gdk.INTERP_BILINEAR)

        #visibility representation
        window.save()
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        window.transform ( ThingMatrix )
        cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
        cairo.Matrix.rotate( ThingMatrix, -self.rotVis ) # Do the rotation
        cairo.Matrix.translate(ThingMatrix, 40,40)
        cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
        window.transform ( ThingMatrix ) # and commit it to the context
        window.set_source_pixbuf(pixbuf1,self.posX,self.posY)
        window.paint()
        window.restore()

        window.save()
        pixbuf=pixbuf.scale_simple(self.width,self.height,gtk.gdk.INTERP_BILINEAR)
        ThingMatrix = cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        ## Next, move the drawing to it's x,y
        window.transform ( ThingMatrix )

        cairo.Matrix.translate(ThingMatrix, self.posX+self.width/2,self.posY+self.height/2)
        #aggresiveness representation
        cairo.Matrix.rotate( ThingMatrix, self.rot ) # Do the rotation
        cairo.Matrix.translate(ThingMatrix, -(self.posX+self.width/2),-(self.posY+self.height/2))
        window.transform ( ThingMatrix ) # and commit it to the context

        window.set_source_pixbuf(pixbuf,self.posX,self.posY)
        window.paint()
        
        #temperature representation
        window.push_group()
        window.set_source_pixbuf(pixbuf, self.posX,self.posY)
        window.paint()
        src = window.pop_group()

        red=(self.transTempLevel*100.0/127)/100
        blue=1-red
        window.set_source_rgba(red,0,blue,0.25)
        window.mask(src)
        window.restore()
        
        #ph representation
        green=(self.transPhLevel*100.0/15)/100
        blue=1-green
        window.set_source_rgba(green,1,blue,1)
        window.rectangle((self.posX+self.width/2+1)-5,(self.posY+self.height/2)-5,10,10)
        window.fill()


        #draw fitness line
        if self.transFitnessPercentage<=25:
            red=1
            green=0
        else:
            green=((self.transFitnessPercentage-25)*1.3333)/100
            red = 1-green
        window.set_source_rgba(red,green,0,1)
        window.rectangle(self.posX+1,self.posY+self.height+1,float(self.transFitnessPercentage*(self.width-1)/100), 4)
        window.fill()

        #window.draw(handle, dst, src)

        #draw fitness line container
        window.set_line_width(1)
        window.set_source_rgba(1,1,1,1)
        window.rectangle(self.posX,self.posY+self.height,self.width, 5)
        window.stroke()

