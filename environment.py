import random


from constants import WINDOW_SIZE

class Environment:
    def __init__(self,posX=0,posY=0,width=WINDOW_SIZE,height=WINDOW_SIZE):
        self.posX=posX
        self.posY=posY
        self.width=width
        self.height=height
        
        #properties
        self.temp= random.randint(0,127)    #0~100
        self.ph=random.randint(0,15)       #0~14
        self.reactivity=random.randint(0,127) #0~100
        self.radar=random.randint(0,127)    #0~100



