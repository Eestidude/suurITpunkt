import pygame as pg
import math
from screeninfo import get_monitors
import sys
from pathlib import Path
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

pg.init()
print(dir_path)
for ekraan in get_monitors():
    ek = ekraan.height
    el = ekraan.width


scale_height = ek/1440
scale_width = el/2560

scale = min (scale_height, scale_width)

ek = 1440 * scale - 60
el = 2560 * scale
running = True

screen = pg.display.set_mode((el,ek), pg.RESIZABLE)



''' KONSTANTID'''

top_bar_height = 1/6*ek
top_bar_width = el
side_bar_height = 7/8*ek
side_bar_wdith = el/6
font = pg.font.SysFont("Arial", 36)
font2 = pg.font.SysFont("Arial", 72)
tausta_värv = [230,230,230]







screen.fill(tausta_värv)

def start_menu():
    dragables = [side_bar_scroll_bar_slider]
    hoverables = [side_bar_scroll_bar_slider, side_bar_scroll_bar_arrow_up, side_bar_scroll_bar_arrow_down]
    nuppud= [ava_fail_nupp, side_bar_scroll_bar_slider, side_bar_scroll_bar_arrow_up, side_bar_scroll_bar_arrow_down]
    tausta_objektid = [top_bar, side_bar, side_bar_scroll_bar]
    dragging_bar = False
    bar_offset = 0
    dragging = False
    hoverable = False
    running = True
    
    while running:
        screen.fill(tausta_värv)
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    for obj in dragables:
                        if obj.rectangle_object.collidepoint(event.pos):
                            dragging_bar = obj
                            obj.color = [160,160,160]
                            
                elif event.type == pg.MOUSEBUTTONUP and dragging_bar:
                    dragging_bar.color = [210,210,210]
                    dragging_bar = False
                    bar_offset = 0
                elif dragging_bar: # VAJAB MUUTUSI
                    if event.type == pg.MOUSEMOTION:
                        if bar_offset == 0:
                            bar_offset = dragging_bar.rectangle_object.y - event.pos[1]
                        new_pos = event.pos[1] + bar_offset
                        
                        if new_pos < top_bar_height+20:
                            dragging_bar.rectangle_object.y = top_bar_height +20
                            
                        elif new_pos > ek-20-dragging_bar.rectangle_object.height:
                            dragging_bar.rectangle_object.y = ek - dragging_bar.rectangle_object.height-20
            
                        else:
                            dragging_bar.rectangle_object.y = new_pos
                
                elif event.type == pg.MOUSEBUTTONUP and not (dragging or dragging_bar):
                    if ava_fail_nupp.rectangle_object.collidepoint(event.pos):
                        
                        running = False
                        
        if not dragging and not dragging_bar:
            if not (hoverable and hoverable.rectangle_object.collidepoint(pg.mouse.get_pos())):
                if hoverable:
                    hoverable.color = [210,210,210]
                    hoverable = False
                for obj in hoverables:
                    if obj.rectangle_object.collidepoint(pg.mouse.get_pos()):
                        hoverable = obj
                        hoverable.color = [190,190,190]
        for objekt in tausta_objektid:
            joonista_tausta_objekt(objekt)
        for nupp in nuppud:
            joonista_nupp(nupp)
        joonista_sim_ikoon(katse_ikoon)
        pg.display.flip()
class Text:
    def __init__(self, tekst = "", font_name = "Arial", font_size = 36, color = "black", offset = (0,0)):
        self.tekst = tekst
        self.color = color
        self.font_name = font_name
        self.font_size = font_size
        self.offset = offset
        self.offset_x = offset[0]
        self.offset_y = offset[1]
class Nupp:
    def __init__(self, rectangle_object, color,tekst = Text()):
        self.rectangle_object = rectangle_object
        self.color = color
        if isinstance(tekst, Text):
            self.tekst = tekst
        else:
            self.tekst = Text(tekst)
class Tausta_objekt:
    def __init__(self, rectangle_object, color):
        self.rectangle_object = rectangle_object
        self.color = color

class simulaatori_ikoon:
    def __init__(self, rectangle_object, color = [240,240,240], img = "C:/Users/Omanik/Documents/GitHub/suurITpunkt/src/gfx/ulpimine.jpg", text = 'No Name'):
        image = pg.image.load(img) 
        self.rectangle_object = rectangle_object
        self.color = color
        self.pilt = image
        self.text = text
        self.gfx = img

def joonista_sim_ikoon(ikoon):
    pg.draw.rect(screen, rect = ikoon.rectangle_object, color = ikoon.color)
    screen.blit(ikoon.pilt, ikoon.rectangle_object, ikoon.rectangle_object)


def joonista_nupp(nupp):
    tfont = pg.font.SysFont(nupp.tekst.font_name, nupp.tekst.font_size)
    size = tfont.size(nupp.tekst.tekst)
    tekst = tfont.render(nupp.tekst.tekst,1,nupp.tekst.color)
    pg.draw.rect(screen,rect = nupp.rectangle_object,color = nupp.color)
    screen.blit(tekst,(nupp.rectangle_object.x + (nupp.rectangle_object.width -size[0])/2 + nupp.tekst.offset_x ,nupp.rectangle_object.y + (nupp.rectangle_object.height - size[1])/2+ nupp.tekst.offset_y))

def joonista_tausta_objekt(tausta_objekt):
    pg.draw.rect(screen, rect = tausta_objekt.rectangle_object,color = tausta_objekt.color)
    
'''NUPPUD'''

ava_fail_nupp = Nupp(pg.Rect(el/2-100,ek/2-50,200,100),[255,255,255],"Ava fail")
side_bar_scroll_bar_slider = Nupp(pg.Rect(0, top_bar_height + 20, 20, 100), [210, 210, 210])
side_bar_scroll_bar_arrow_up = Nupp(pg.Rect(0, top_bar_height, 20, 20), [210, 210, 210], Text("^", font_size = 20, offset = (0,5)))
side_bar_scroll_bar_arrow_down = Nupp(pg.Rect(0, ek-20, 20, 20), [210, 210, 210], Text("v", font_size = 16, offset = (0, -3)))
katse_ikoon = simulaatori_ikoon(pg.Rect(100, 100, 50, 100))
'''RIBAD'''

top_bar = Tausta_objekt(pg.Rect(0,0,top_bar_width, top_bar_height), [200,200,200])
side_bar = Tausta_objekt(pg.Rect(0, top_bar_height, side_bar_wdith, side_bar_height), [255,255,255])

#scrollbarid
side_bar_scroll_bar = Tausta_objekt(pg.Rect(0,top_bar_height,20, side_bar_height), [230,230,230])

start_menu()
pg.quit()