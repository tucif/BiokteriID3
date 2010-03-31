# coding: utf-8

import gtk
#import cairo
import gobject
import pygtk

import random


pygtk.require('2.0')

from sprite import Sprite
from virus import Virus 
from virus import DEFAULT_WIDTH as VIRUS_WIDTH, DEFAULT_HEIGHT as VIRUS_HEIGHT
from environment import Environment
from display import display_simulation
from hud import Hud
from constants import WINDOW_SIZE, TOTAL_VIRUS, TOTAL_ENVIRONMENTS

from genetics.geneticAlgorithm import evolve

virList =[Virus(
           random.randint(0,WINDOW_SIZE-VIRUS_WIDTH),
           random.randint(0,WINDOW_SIZE-VIRUS_HEIGHT),
           random.randint(0,127),
           random.randint(0,15),
           random.randint(0,127),
           random.randint(0,127)
            ) for i in xrange(TOTAL_VIRUS)]

environmentList=[Environment()for i in xrange(TOTAL_ENVIRONMENTS)]

for virus in virList:
    virus.update_fitness(environmentList[0])

def evolution(widget, lienzo):
    lienzo.virus =  evolve(lienzo.virus, environmentList[0])
    for virus in lienzo.virus:
        virus.update_fitness(environmentList[0])

#Lienzo es donde se pintara todo
class Lienzo(gtk.DrawingArea):
    def __init__(self, ventana):
        """"""
        super(Lienzo, self).__init__()
        
        #Cambiar el color de fondo de la ventana
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
        # Pedir el tamano de la ventana
        self.set_size_request(WINDOW_SIZE,WINDOW_SIZE)

        #Asignar la ventana que recibe de paramentro a la ventana que se
        #utilizara en el lienzo
        self.ventana=ventana

        #expose-event es una propiedad de DrawingArea que le dice como
        #dibujares, aqui le decimos que utilize nuestra funcion paint
        #para ese evento en vez del que trae por defaul.
        self.connect("expose-event", self.paint)
        #reconocer cuando oprimes y sueltas el mouse
        self.connect("button_press_event",self.button_press)
        self.connect("button_release_event",self.button_release)
        self.connect("motion_notify_event",self.actualizar_dragged)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK|gtk.gdk.POINTER_MOTION_MASK)

        #Inicializar todos los valores
        self.init_simulation()
        self.hud=Hud()
        
        #celulas
        self.virus=virList

        self.virus_meta = Virus((WINDOW_SIZE-VIRUS_WIDTH-130),40,
                                environmentList[0].temp,
                                environmentList[0].ph,
                                environmentList[0].reactivity,
                                environmentList[0].radar)
        self.virus_meta.update_fitness(environmentList[0])

        self.draggingObject = None
        self.corriendo = True

        self.objetoSeleccionado=[]
        #gobject.timeout_add(20, self.mainloop) ########################################################

    def actualizar_dragged(self,widget,event):
        if self.draggingObject:
            self.draggingObject.posX=event.x
            self.draggingObject.posY=event.y

    def on_timer(self):
        self.update()
        return True

    def init_simulation(self):
        """Inicializacion de valores"""
        gobject.timeout_add(20, self.on_timer)

    def update(self):
        self.queue_draw()
        self.virus_meta.update()
        for virus in self.virus:
            if not virus.isDead:
                virus.update()
            
    def paint(self, widget, event):
        """Nuestro metodo de pintado propio"""

        #Se crea un widget de cairo que despues se usara para desplegar
        #todo en la ventana
        cr = widget.window.cairo_create()
        #Le decimos a cairo que pinte su widget por primera vez.
        cr.set_source_rgb(0,0,0)
        cr.paint()


        #pintar a los agentes
        display_simulation(cr,self.virus,environmentList[0])
        self.virus_meta.paint(cr)
        self.hud.display_viruses(cr, self.virus+[self.virus_meta])
        self.hud.display_environment(cr,environmentList)

        #pintar efecto de selección sobre un agente
        if self.objetoSeleccionado:
            cr.set_line_width(2)
            cr.set_source_rgba(random.random(), 1, random.random(), 0.3)
            cr.rectangle(self.objetoSeleccionado.posX-20,self.objetoSeleccionado.posY-20,
                            self.objetoSeleccionado.width+40, self.objetoSeleccionado.height+40)

            cr.stroke()

        text="Average fitness: %d" % (self.average_virus_fitness(self.virus))
        cr.move_to(5,30)
        cr.set_source_rgba(1,1,1,0.7)
        cr.show_text(text)

        #pintar recuadro que envuelve a meta_virus (el meta virus se pinta solo en su paint)
        text="VIRUS IDEAL"
        cr.move_to(515,20)
        cr.set_source_rgba(1,1,1,1)
        cr.show_text(text)

        cr.set_line_width(5)
        cr.rectangle(500-5,5,100,100)
        cr.set_source_rgba(1,1,1,1)
        cr.stroke()

    def average_virus_fitness(self,virList):
        accum=0
        for virus in virList:
            accum+=virus.fitness

        return float(accum)/len(virList)
        
    #Para drag & drop
    def button_press(self,widget,event):
        if event.button == 1:
            self.objetoSeleccionado=[]
            lstTemp = self.virus
            for ob in lstTemp:
                if ob.drag(event.x,event.y):
                    self.draggingObject = ob
                    self.objetoSeleccionado=ob
                    break
                    
    def button_release(self,widget,event):
        if self.draggingObject:
            self.draggingObject.drop(event.x,event.y)
            self.draggingObject = None

    def pausar(self):
        self.corriendo=False

    def correr(self):
        self.corriendo=True
        
#    def mainloop(self):
#        while self.corriendo:
#            # Process all pending events.
#            self.update()
#            while gtk.events_pending():
#                gtk.main_iteration(False)
#                # Generate an expose event (could just draw here as well).
#            self.queue_draw()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Main(gtk.Window):
    def __init__(self):
        super(Main, self).__init__()
        self.set_title('Biokterii')
        self.set_size_request(WINDOW_SIZE,WINDOW_SIZE)
        self.set_resizable(True)
        self.set_position(gtk.WIN_POS_CENTER)
        #mainBox contiene el menu superior, contentBox(menu,lienzo) y el menu inferior
        self.mainBox = gtk.VBox(False,0)
        self.mainBox.set_size_request(WINDOW_SIZE,WINDOW_SIZE)
        
        #contentBox contiene el menu lateral y lienzo
        self.contentBox= gtk.HBox(False,0) #Recibe False para no se homogeneo
        
        self.lienzo=Lienzo(self)
        self.lienzo.set_size_request(WINDOW_SIZE-20,WINDOW_SIZE-20)
        
        self.contentBox.pack_start(self.lienzo, expand=True, fill=True, padding=0)

        #Menu bar
        menuBar = gtk.MenuBar()

        filemenu = gtk.Menu()
        filem = gtk.MenuItem("File")
        filem.set_submenu(filemenu)

        annealMenu = gtk.MenuItem("Evolve")
        annealMenu.connect("activate", evolution, self.lienzo)
        filemenu.append(annealMenu)

        exit = gtk.MenuItem("Exit")
        exit.connect("activate", gtk.main_quit)
        filemenu.append(exit)

        menuBar.append(filem)

        menuBox = gtk.HBox(False, 2)
        menuBox.pack_start(menuBar, False, False, 0)

        #Empaquetado de todos los controles
        self.mainBox.pack_start(menuBox,expand=True,fill=True,padding=0)
        self.mainBox.pack_start(self.contentBox,expand=True, fill=True, padding=0)

        #Agregar la caja que contiene todo a la ventana
        self.add(self.mainBox)
        self.connect("destroy", gtk.main_quit)
        self.show_all()

    def pausar_lienzo(self, widget):
        self.lienzo.pausar()

    def correr_lienzo(self, widget):
        self.lienzo.correr()

#    def cerrar_lienzo(self,widget):
#        self.lienzo.corriendo=False
#        gtk.main_quit

if __name__ == '__main__':
    Main()
    gtk.main()
