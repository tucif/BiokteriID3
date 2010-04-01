import random
import gtk, gobject, cairo

from sprite import Sprite
from constants import VIRUS_IMAGE
from constants import WINDOW_SIZE

DEFAULT_WIDTH=50
DEFAULT_HEIGHT=50

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
        self.velX=0.0
        self.velY=0.0
        self.imagen=VIRUS_IMAGE

        #rotation
        self.deltaRot=0.05
        self.rotDirection=-1
        self.rot=0

    def __str__(self):
        return "Virus"

    def get_type(self):
        return "Virus"

    def update(self):
        Sprite.update(self)
        self.rot+=self.deltaRot*self.rotDirection

        if self.hp<=0:
            self.isDead=True
        else:
            self.isDead=False;

    def paint(self,window):
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


