import pygame as pg
import math
from screeninfo import get_monitors
pg.init()

for ekraan in get_monitors():
    ek = ekraan.height
    el = ekraan.width


scale_height = ek/1440
scale_width = el/2560
ek = 1440 * scale_height - 62

running = True

screen = pg.display.set_mode((el,ek), pg.RESIZABLE)



tausta_värv = [230,230,230]
screen.fill(tausta_värv)



font = pg.font.SysFont("Arial", 36)
font2 = pg.font.SysFont("Arial", 72)

def start_menu():
    nuppud= [ava_fail_nupp]
    tausta_objektid = [top_bar, side_bar]
    running = True
    
    while running:
        screen.fill(tausta_värv)
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONUP:
                    if ava_fail_nupp.rectangle_object.collidepoint(event.pos):
                        
                        #sireen.play(0)
                        running = False
    
        for nupp in nuppud:
            joonista_nupp(nupp)
        for objekt in tausta_objektid:
            joonista_tausta_objekt(objekt)

        pg.display.flip()
class Nupp:
    def __init__(self, rectangle_object, color,tekst):
        self.rectangle_object = rectangle_object
        self.color = color
        self.tekst = tekst
class Tausta_objekt:
    def __init__(self, rectangle_object, color):
        self.rectangle_object = rectangle_object
        self.color = color
        
def joonista_nupp(nupp):
    tekst = font.render(nupp.tekst,1,"black")
    pg.draw.rect(screen,rect = nupp.rectangle_object,color = nupp.color)
    screen.blit(tekst,(nupp.rectangle_object.x+nupp.rectangle_object.width/2 - 8*len(nupp.tekst),nupp.rectangle_object.y+nupp.rectangle_object.height/2-17))

def joonista_tausta_objekt(tausta_objekt):
    pg.draw.rect(screen, rect = tausta_objekt.rectangle_object,color = tausta_objekt.color)
    
#start_nupp = Nupp(pg.Rect(el/2-100,ek/2-50,50,50),"red","")

ava_fail_nupp = Nupp(pg.Rect(el/2-100,ek/2-50,200,100),[255,255,255],"Ava fail")
top_bar = Tausta_objekt(pg.Rect(0,0,el, 1/6*ek), [200,200,200])
side_bar = Tausta_objekt(pg.Rect(0,1/6*ek,el/6, 7/8*ek), [255,255,255])


start_menu()
pg.quit()