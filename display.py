from sprite import Sprite
from virus import Virus

DISPLAY_IDS=True

def display_simulation(window,virusList,environment):
    """Fucntion that diplays the whole simulation"""
    display_virus(window,virusList)
    display_environment(window,environment)

def display_environment(window,environment):

#    window.rectangle(0,0,700,700)
#    #dependiendo el numero de radares es la visibilidad del mapa
#    visibility = 1.0 - (environment.radar/200.0 + 0.4)
#    window.set_source_rgba(1,1,1,visibility)
#    window.fill()
    pass

def display_virus(window,virusList):
    """Fucntion that diplays the virus"""
    for virus in virusList:
        virus.paint(window)
