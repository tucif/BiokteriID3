from sprite import Sprite

ID_PADDING=[0,-5]

class Hud():
    def __init__(self):
        self.allVisible=True
        self.idVisible=True
        self.boundingBoxVisible=True
        self.window=None

    def display_viruses(self,window,objectList):

        if self.allVisible:
            if self.idVisible:
                for object in objectList:
                    if isinstance(object,Sprite):

                        #dibujar virusito en minimapa
                        posXMinimapa = (object.posX * 0.142857143) + 600
                        posYMinimapa = (object.posY * 0.142857143)
                        window.rectangle(posXMinimapa,posYMinimapa,7,7)
                        if object.fitnessPercentage<=25:
                            red=1
                            green=0
                        else:
                            green=((object.fitnessPercentage-25)*1.3333)/100
                            red = 1-green
                        window.set_source_rgba(red,green,0,1)
                        window.fill()



                        text=str(object)
                        posXText=object.posX+object.width/2-(len(text)/2)*5
                        posYText=object.posY+ID_PADDING[1]
                        window.move_to(posXText,posYText)
                        window.set_source_rgba(1,1,1,0.7)
                        window.show_text(text)

    def display_environment(self,window,environmentList):
        for environment in environmentList:
            posXText=environment.posX+5
            posYText=environment.posY+15
            text="Environment properties: temp:%d | ph:%d | reactivity: %d | radars: %d" % (environment.temp,environment.ph,environment.reactivity,environment.radar)

            window.move_to(posXText,posYText)
            window.set_source_rgba(1,1,1,0.7)
            window.show_text(text)

            window.rectangle(600-5,5,100,100)

            #show map
            visibility = 1.0 - (environment.radar/200.0 + 0.4)
            colorTempRed = environment.temp * 0.01
            colorTempBlue = 1.0 - colorTempRed
            window.set_source_rgba(colorTempRed,0,colorTempBlue,visibility)
            window.fill()

            window.set_line_width(5)
            window.rectangle(600-5,5,100,100)
            window.set_source_rgba(1,1,1,1)
            window.stroke()

            

            