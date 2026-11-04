import pygame as pg
import math
from screeninfo import get_monitors
import sys
import sys
from pathlib import Path
import os

if getattr(sys, "frozen", False):
    # Running as a compiled EXE
    dir_path = Path(sys.executable).resolve().parent
else:
    # Running as a normal Python script
    dir_path = Path(__file__).resolve().parent

dir_gfx = dir_path / "gfx"
dir_sim = dir_path / "simulaatorid"


sims = [p.name for p in dir_sim.glob("*.py")]
pg.init()
käsi = pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)
tavaline = pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW)
pg.mouse.set_cursor(tavaline)


for ekraan in get_monitors():
    ek = ekraan.height
    el = ekraan.width


scale_height = ek/1440
scale_width = el/2560

scale = min (scale_height, scale_width)

ek = 800 * scale
el = 600 * scale
running = True


pg.display.set_icon(pg.image.load(dir_gfx / "logo2.png"))
screen = pg.display.set_mode((el,ek), pg.RESIZABLE)
pg.display.set_caption('Füstastic"')


''' KONSTANTID'''

top_bar_height = 1/6*ek
top_bar_width = el
side_bar_height = 7/8*ek
side_bar_wdith = el/6
font = pg.font.SysFont("Arial", 36)
font2 = pg.font.SysFont("Arial", 72)
tausta_värv = [230,230,230]







screen.fill(tausta_värv)
thumb = pg.image.load(dir_gfx / "thumb.jpg")

def start_menu():
    dragables = [side_bar_scroll_bar_slider]
    hoverables = [side_bar_scroll_bar_slider, side_bar_scroll_bar_arrow_up, side_bar_scroll_bar_arrow_down]
    nuppud= [side_bar_scroll_bar_slider, side_bar_scroll_bar_arrow_up, side_bar_scroll_bar_arrow_down]
    tausta_objektid = [top_bar]
    ikoonid = []
    ikoon_x = 20
    ikoon_y = ek/6
    ikoon_w = el - 20
    ikoon_h = int(ek/6)
    uus_color = [250,250,250]
    for sim in sims:
        
        uus_tekst = sim
        uus_tekst = Text(tekst = uus_tekst, offset=(100,-20), font_size = 24)
        uus_rect = pg.Rect(ikoon_x, ikoon_y, ikoon_w, ikoon_h)
        
        image_path = dir_gfx / f"{Path(sim).stem}.jpg"

        if image_path.is_file():
            uus_img = str(image_path)
        else:
            uus_img = str(dir_gfx / "ulpimine.jpg")
        if uus_color == [220,220,220]:
            uus_color = [240,240,240]
        else:
            uus_color=[220,220,220]
        uus_ikoon = Ikoon(uus_rect, color = uus_color, img = uus_img, tekst = uus_tekst, original_pos=(ikoon_x,ikoon_y))
        ikoonid.append(uus_ikoon)
        ikoon_y+= ikoon_h
    
    side_bar_scroll_bar_slider.rectangle_object.height = min( ek*5/6-40+1, ( (ek*5/6) / (len(ikoonid)*ikoon_h)*(ek*5/6-40+1) ))
    dragging_bar = False
    bar_offset = 0
    ikoon_offset = 0
    dragging = False
    hoverable = False
    running = True
    
    while running:
        ikoon_offset = 0
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
                    ikoon_offset = 0
                    
                    
                elif dragging_bar: # VAJAB MUUTUSI
                    if event.type == pg.MOUSEMOTION:
                        if bar_offset == 0:
                            bar_offset = dragging_bar.rectangle_object.y - event.pos[1]
                        new_pos = event.pos[1] + bar_offset
                        
                        if new_pos < top_bar_height+20:
                            dragging_bar.rectangle_object.y = top_bar_height +20
                            ikoon_offset = 0
                            
                        elif new_pos > ek-20-dragging_bar.rectangle_object.height:
                            dragging_bar.rectangle_object.y = ek - dragging_bar.rectangle_object.height-20
                            ikoon_offset = (len(ikoonid)-5)*ikoon_h
                        else:
                            dragging_bar.rectangle_object.y = new_pos
                            ikoon_offset = (len(ikoonid)-5)*ikoon_h  *(new_pos- (top_bar_height +20) )/ ((ek - dragging_bar.rectangle_object.height-20) - (top_bar_height +20))
                            
                        for ikoon in ikoonid:
                            ikoon.rectangle_object.y = ikoon.oy - ikoon_offset
                            
                                                    
                elif event.type == pg.MOUSEBUTTONUP and not (dragging or dragging_bar):
#                     if ava_fail_nupp.rectangle_object.collidepoint(event.pos):
#                         namespace = {}
#                         exec(open(dir_sim +'\\ulpimine.py', encoding='UTF-8').read(), namespace)
#                         pg.display.set_mode((el,ek), pg.RESIZABLE)
                    if True:
                        for ikoon in ikoonid:
                            if ikoon.rectangle_object.collidepoint(event.pos):
                                script_path = dir_sim / ikoon.tekst.tekst

                                namespace = {"__name__": "__main__","__file__": str(script_path),}

                                with open(script_path, "r", encoding="UTF-8") as f:
                                    code = f.read()

                                exec(compile(code, str(script_path), "exec"), namespace, namespace)
                                pg.display.set_mode((el,ek), pg.RESIZABLE)
                                pg.display.set_caption("Füstastic")
                    
                                
        if not dragging and not dragging_bar:
            if not (hoverable and hoverable.rectangle_object.collidepoint(pg.mouse.get_pos())):
                if hoverable:
                    hoverable.color = [210,210,210]
                    hoverable = False
                for obj in hoverables:
                    if obj.rectangle_object.collidepoint(pg.mouse.get_pos()):
                        hoverable = obj
                        hoverable.color = [190,190,190]
        
        for icon in ikoonid:
            joonista_sim_ikoon(icon)
        for nupp in nuppud:
            joonista_nupp(nupp)
        for objekt in tausta_objektid:
            joonista_tausta_objekt(objekt)
        screen.blit(thumb, (150,40))
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
        self.x = rectangle_object.x
        self.y = rectangle_object.y
        self.w = rectangle_object.width
        self.h = rectangle_object.height
class Tausta_objekt:
    def __init__(self, rectangle_object, color):
        self.rectangle_object = rectangle_object
        self.color = color

class Ikoon:
    def __init__(self, rectangle_object, color = [240,240,240], img = None, tekst = 'No Name', original_pos = (0,0)):
        image = pg.image.load(img) 
        self.rectangle_object = rectangle_object
        self.color = color
        self.pilt = image
        if isinstance(tekst, Text):
            self.tekst = tekst
        else:
            self.tekst = Text(tekst)
        self.gfx = img
        self.x = rectangle_object.x
        self.y = rectangle_object.y
        self.w = rectangle_object.width
        self.h = rectangle_object.height
        self.ox = original_pos[0]
        self.oy = original_pos[1]

def joonista_sim_ikoon(ikoon):
    pg.draw.rect(screen, rect = ikoon.rectangle_object, color = ikoon.color)
    tfont = pg.font.SysFont(ikoon.tekst.font_name, ikoon.tekst.font_size)
    size = tfont.size(ikoon.tekst.tekst)
    tekst = tfont.render(ikoon.tekst.tekst[0:-3].capitalize(),1,ikoon.tekst.color)
    screen.blit(tekst,(ikoon.rectangle_object.x + (ikoon.rectangle_object.width -size[0])/2 + ikoon.tekst.offset_x ,ikoon.rectangle_object.y + (ikoon.rectangle_object.height - size[1])/2+ ikoon.tekst.offset_y))
    
    img_w = int(ikoon.w/3)
    img_h = int(ikoon.h-10)
    img_x = int(ikoon.pilt.get_width()/2)- int(img_w/2)
    img_y = int(ikoon.pilt.get_height()/2)- int(img_h/2)
    
    screen.blit(ikoon.pilt, dest = (ikoon.rectangle_object.x+5, ikoon.rectangle_object.y+5), area = pg.Rect(img_x,img_y, img_w, img_h ))
    
def joonista_nupp(nupp):
    tfont = pg.font.SysFont(nupp.tekst.font_name, nupp.tekst.font_size)
    size = tfont.size(nupp.tekst.tekst)
    tekst = tfont.render(nupp.tekst.tekst,1,nupp.tekst.color)
    pg.draw.rect(screen,rect = nupp.rectangle_object,color = nupp.color)
    screen.blit(tekst,(nupp.rectangle_object.x + (nupp.rectangle_object.width -size[0])/2 + nupp.tekst.offset_x ,nupp.rectangle_object.y + (nupp.rectangle_object.height - size[1])/2+ nupp.tekst.offset_y))

def joonista_tausta_objekt(tausta_objekt):
    pg.draw.rect(screen, rect = tausta_objekt.rectangle_object,color = tausta_objekt.color)
    
'''NUPPUD'''

# ava_fail_nupp = Nupp(pg.Rect(el/2-100,ek/2-50,200,100),[255,255,255],"Ava fail")

side_bar_scroll_bar_arrow_up = Nupp(pg.Rect(0, top_bar_height, 20, 20), [210, 210, 210], Text("^", font_size = 20, offset = (0,5)))
side_bar_scroll_bar_arrow_down = Nupp(pg.Rect(0, ek-20, 20, 20), [210, 210, 210], Text("v", font_size = 16, offset = (0, -3)))
side_bar_scroll_bar_slider = Nupp(pg.Rect(0, top_bar_height + 20, 20, ek*5/6-40+1), [210, 210, 210])
# katse_ikoon = Ikoon(pg.Rect(100, 100, 50, 100))
'''RIBAD'''

top_bar = Tausta_objekt(pg.Rect(0,0,top_bar_width, top_bar_height), [200,200,200])
side_bar = Tausta_objekt(pg.Rect(0, top_bar_height, side_bar_wdith, side_bar_height), [255,255,255])

#scrollbarid
side_bar_scroll_bar = Tausta_objekt(pg.Rect(0,top_bar_height,20, side_bar_height), [230,230,230])

start_menu()
pg.quit()