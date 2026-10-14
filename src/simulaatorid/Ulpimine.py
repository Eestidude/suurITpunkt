import math
import sys

import pygame

# Seaded
W, H = 1100, 700
PANEL_W = 360
SCENE = pygame.Rect(PANEL_W, 0, W - PANEL_W, H)
FPS = 60
SUBSTEPS = 20
THICK = 1.0

# Värvid
PANEL_BG = (30, 34, 44)
TEXT = (230, 233, 240)
DIM = (125, 131, 146)
ACCENT = (70, 150, 250)
FIELD_BG = (45, 50, 64)
FIELD_ACTIVE = (58, 68, 94)
FIELD_BORDER = (75, 82, 100)
ERR = (225, 80, 80)
SKY = (208, 230, 247)
WATER = (30, 110, 200, 125)
WATER_LINE = (130, 195, 255)
TANK = (75, 80, 92)
BODY = (178, 122, 66)
BODY_EDGE = (92, 56, 26)
RED = (205, 45, 45)
GREEN = (25, 150, 65)
DARK = (30, 40, 60)


# Font
def make_font(size, bold=False):
    names = "arial,segoeui,dejavusans,liberationsans,freesans,helvetica"
    return pygame.font.SysFont(names, size, bold=bold)


# Vorming
def fmt(x):
    if abs(x) >= 1000:
        return f"{x:,.0f}".replace(",", " ")
    return f"{x:.3g}"


# Nool
def draw_arrow(surf, color, start, end, width=4):
    length = math.hypot(end[0] - start[0], end[1] - start[1])
    if length < 3:
        return
    pygame.draw.line(surf, color, start, end, width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    head = min(12, length)
    p1 = (end[0] - head * math.cos(ang - 0.45), end[1] - head * math.sin(ang - 0.45))
    p2 = (end[0] - head * math.cos(ang + 0.45), end[1] - head * math.sin(ang + 0.45))
    pygame.draw.polygon(surf, color, [end, p1, p2])


# Väli
class Field:
    # Konstruktor
    def __init__(self, key, label, value, lo, hi):
        self.key, self.label = key, label
        self.value, self.lo, self.hi = value, lo, hi
        self.text = f"{value:g}"
        self.rect = pygame.Rect(0, 0, 120, 28)
        self.enabled = True
        self.error = False
        self.fresh = False

    # Kinnitus
    def commit(self):
        try:
            v = float(self.text.replace(",", "."))
            self.value = min(self.hi, max(self.lo, v))
            self.error = False
        except ValueError:
            self.error = True
        self.text = f"{self.value:g}"
        self.fresh = False


# Füüsika
class Sim:
    # Konstruktor
    def __init__(self, shape, rho_b, a, b, rho_w, depth, cd, thick, g):
        self.shape = shape
        self.rho_b, self.rho_w = rho_b, rho_w
        self.depth, self.cd, self.g = depth, cd, g
        self.thick = thick
        if shape == "circle":
            self.r = a
            self.w = self.h = 2 * a
            self.area = math.pi * a * a
        else:
            self.w, self.h = a, b
            self.area = a * b
        self.mass = rho_b * self.area * self.thick
        self.y = depth + self.h / 2
        self.v = 0.0
        self.t = 0.0
        self.sub = 0.0
        self.fb = 0.0
        self.net = 0.0
        self.on_floor = False

    # Pindala
    def sub_area(self, y):
        if self.shape == "circle":
            r = self.r
            t = max(-1.0, min(1.0, (self.depth - y) / r))
            above = r * r * (math.acos(t) - t * math.sqrt(1.0 - t * t))
            return math.pi * r * r - above
        sub_h = min(max(self.depth - (y - self.h / 2), 0.0), self.h)
        return self.w * sub_h

    # Samm
    def step(self, dt):
        sub = self.sub_area(self.y)
        frac = sub / self.area
        self.sub = frac
        self.fb = self.rho_w * self.g * sub * self.thick
        self.net = self.fb - self.mass * self.g

        self.v += self.net / self.mass * dt

        # Takistus
        if frac > 0:
            k = 0.5 * self.rho_w * self.cd * self.w * THICK * frac * abs(self.v)
            if frac < 1:
                k += 0.5 * self.rho_w * self.cd * self.w * THICK * math.sqrt(self.g * self.w)
            self.v /= 1.0 + k / self.mass * dt

        self.y += self.v * dt

        # Põhi
        floor_y = self.h / 2
        if self.y <= floor_y:
            self.y = floor_y
            if self.v < 0:
                self.v = 0.0
            self.on_floor = True
        else:
            self.on_floor = False
        self.t += dt


# Rakendus
class App:
    # Konstruktor
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Upub või ujub?")
        self.clock = pygame.time.Clock()

        self.f_title = make_font(24, True)
        self.f_big = make_font(28, True)
        self.f_b = make_font(16, True)
        self.f = make_font(16)
        self.f_i = make_font(15)
        self.f_s = make_font(13)

        self.shape = "rect"
        self.fields = [
            Field("rho_b", "Keha tihedus, kg/m³", 600, 1, 25000),
            Field("a", "Laius, m", 0.5, 0.05, 3),
            Field("b", "Kõrgus, m", 0.3, 0.05, 3),
            Field("thick", "Paksus, m", 1.0, 0.05, 3),
            Field("rho_w", "Vee tihedus, kg/m³", 1000, 1, 20000),
            Field("depth", "Vee sügavus, m", 3, 0.5, 8),
            Field("cd", "Vee takistus (Cd)", 1.0, 0, 5),
            Field("g", "Kiirendus g, m/s²", 9.81, 0.5, 30),
        ]
        for i, fld in enumerate(self.fields):
            fld.rect.topleft = (226, 92 + i * 34)
        self.by_key = {f.key: f for f in self.fields}

        self.btn_shape = {"rect": pygame.Rect(14, 48, 160, 30),
                          "circle": pygame.Rect(186, 48, 160, 30)}
        self.btn_restart = pygame.Rect(14, 372, 160, 30)
        self.btn_pause = pygame.Rect(186, 372, 160, 30)

        self.active = None
        self.paused = False
        self.speed = 1.0
        self.water_surf = pygame.Surface((SCENE.w, H), pygame.SRCALPHA)
        self.sync_fields()
        self.restart()

    # Sünkroonimine
    def sync_fields(self):
        circle = self.shape == "circle"
        self.by_key["a"].label = "Raadius, m" if circle else "Laius, m"
        self.by_key["b"].enabled = not circle
        if self.active is not None and not self.active.enabled:
            self.active = None

    # Taaskäivitus
    def restart(self):
        v = {f.key: f.value for f in self.fields}
        self.sim = Sim(self.shape, v["rho_b"], v["a"], v["b"], v["rho_w"],
                       v["depth"], v["cd"], v["thick"], v["g"])
        self.wave_amp = 0.0
        self.wave_t = 0.0
        s = self.sim
        air = max(2.0, s.y + s.h / 2 + 0.6 - s.depth)
        self.scale = min((H - 70) / (s.depth + air),
                         SCENE.w * 0.6 / max(s.w, 0.5), 220)
        self.floor_px = H - 30

    # Uuendus
    def update(self, dt):
        if self.paused:
            return
        dt *= self.speed
        for _ in range(SUBSTEPS):
            self.sim.step(dt / SUBSTEPS)
        s = self.sim
        self.wave_t += dt
        if 0 < s.sub < 1:
            self.wave_amp = min(0.15, max(self.wave_amp, abs(s.v) * 0.05))
        self.wave_amp *= math.exp(-1.0 * dt)

    # Olek
    def status(self):
        s = self.sim
        if s.on_floor and s.net <= 0:
            return "Lamab põhjas"
        if s.sub == 0:
            return "Kukub vette" if s.v < -0.05 else "Õhus"
        if abs(s.v) < 0.03:
            return "Ujub pinnal" if s.sub < 1 else "Hõljub vees"
        return "Tõuseb" if s.v > 0 else "Upub"

    # Kinnitus
    def commit_active(self):
        f = self.active
        if f is None:
            return
        old = f.value
        f.commit()
        if f.value != old:
            self.restart()

    # Fookus
    def set_active(self, f):
        if self.active is not f:
            self.commit_active()
        self.active = f
        if f is not None:
            f.fresh = True

    # Liikumine
    def focus_step(self, step):
        en = [f for f in self.fields if f.enabled]
        i = en.index(self.active) if self.active in en else -1
        self.set_active(en[(i + step) % len(en)])

    # Klõps
    def on_click(self, pos):
        clicked = None
        for f in self.fields:
            if f.enabled and f.rect.collidepoint(pos):
                clicked = f
        self.set_active(clicked)
        for key, rect in self.btn_shape.items():
            if rect.collidepoint(pos) and key != self.shape:
                self.shape = key
                self.sync_fields()
                self.restart()
        if self.btn_restart.collidepoint(pos):
            self.restart()
        if self.btn_pause.collidepoint(pos):
            self.paused = not self.paused

    # Klahv
    def on_key(self, e):
        f = self.active
        if f is not None:
            if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.commit_active()
                self.active = None
                self.restart()
            elif e.key == pygame.K_TAB:
                shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                self.focus_step(-1 if shift else 1)
            elif e.key == pygame.K_ESCAPE:
                f.text = f"{f.value:g}"
                f.error = False
                self.active = None
            elif e.key == pygame.K_BACKSPACE:
                f.text = "" if f.fresh else f.text[:-1]
                f.fresh = False
            elif e.unicode and e.unicode in "0123456789.,-":
                if f.fresh:
                    f.text = ""
                    f.fresh = False
                if len(f.text) < 9:
                    f.text += e.unicode
                f.error = False
            return
        if e.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif e.key == pygame.K_r:
            self.restart()
        elif e.key == pygame.K_1:
            self.speed = 0.25
        elif e.key == pygame.K_2:
            self.speed = 1.0
        elif e.key == pygame.K_3:
            self.speed = 2.0

    # Tekst
    def text(self, s, font, color, pos):
        self.screen.blit(font.render(s, True, color), pos)

    # Nupp
    def button(self, rect, label, selected=False):
        pygame.draw.rect(self.screen, ACCENT if selected else FIELD_BG, rect, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT if selected else FIELD_BORDER, rect, 2, border_radius=6)
        img = self.f.render(label, True, (255, 255, 255) if selected else TEXT)
        self.screen.blit(img, img.get_rect(center=rect.center))

    # Paneel
    def draw_panel(self):
        s = self.screen
        sim = self.sim
        pygame.draw.rect(s, PANEL_BG, (0, 0, PANEL_W, H))
        self.text("Upub või ujub?", self.f_title, TEXT, (14, 10))

        self.button(self.btn_shape["rect"], "Ristkülik", self.shape == "rect")
        self.button(self.btn_shape["circle"], "Ring", self.shape == "circle")

        # Väljad
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        for f in self.fields:
            col = TEXT if f.enabled else DIM
            self.text(f.label, self.f, col, (14, f.rect.y + 5))
            bg = FIELD_ACTIVE if f is self.active else FIELD_BG
            pygame.draw.rect(s, bg, f.rect, border_radius=5)
            border = ERR if f.error else (ACCENT if f is self.active else FIELD_BORDER)
            pygame.draw.rect(s, border, f.rect, 2, border_radius=5)
            txt = f.text if f.enabled else "—"
            if f is self.active and blink and not f.fresh:
                txt += "|"
            tcol = ACCENT if (f is self.active and f.fresh) else col
            self.text(txt, self.f, tcol, (f.rect.x + 8, f.rect.y + 5))

        self.button(self.btn_restart, "Uuesti (R)")
        self.button(self.btn_pause, "Jätka" if self.paused else "Paus (Tühik)")

        # Arvutus
        y = 412
        self.text("Arvutus", self.f_b, ACCENT, (14, y))
        y += 24

        weight = sim.mass * sim.g
        fmax = sim.rho_w * sim.g * sim.area * sim.thick
        volume = sim.area * sim.thick

        lines = [
            f"Ruumala: {fmt(volume)} m³",
            f"Mass: {fmt(sim.mass)} kg",
            f"Raskusjõud mg: {fmt(weight)} N",
            f"Maks. Archimedese jõud: {fmt(fmax)} N",
        ]

        for line in lines:
            self.text(line, self.f_i, TEXT, (14, y))
            y += 20

        # Stseen
    def draw_scene(self):
        s = self.screen
        sim = self.sim
        sc = self.scale
        s.set_clip(SCENE)
        pygame.draw.rect(s, SKY, SCENE)

        cx = SCENE.centerx
        floor = self.floor_px
        surf_y = floor - sim.depth * sc
        left, right = SCENE.x + 30, SCENE.right - 30
        bx, by = cx, floor - sim.y * sc

        # Keha
        if sim.shape == "circle":
            rad = max(2, int(sim.r * sc))
            pygame.draw.circle(s, BODY, (int(bx), int(by)), rad)
            pygame.draw.circle(s, BODY_EDGE, (int(bx), int(by)), rad, 2)
        else:
            body = pygame.Rect(0, 0, max(2, int(sim.w * sc)), max(2, int(sim.h * sc)))
            body.center = (int(bx), int(by))
            pygame.draw.rect(s, BODY, body)
            pygame.draw.rect(s, BODY_EDGE, body, 2)

        # Vesi
        pts = []
        x = left
        while x <= right:
            dx = (x - cx) / sc
            off = self.wave_amp * math.sin(6 * abs(dx) - 7 * self.wave_t) * math.exp(-0.8 * abs(dx))
            pts.append((x - SCENE.x, surf_y - off * sc))
            x += 6
        poly = pts + [(right - SCENE.x, floor), (left - SCENE.x, floor)]
        self.water_surf.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.water_surf, WATER, poly)
        s.blit(self.water_surf, SCENE.topleft)
        pygame.draw.lines(s, WATER_LINE, False, [(px + SCENE.x, py) for px, py in pts], 3)

        # Mahuti
        wall_top = max(0, int(surf_y - 0.8 * sc))
        pygame.draw.rect(s, TANK, (left - 8, wall_top, 8, floor - wall_top + 12))
        pygame.draw.rect(s, TANK, (right, wall_top, 8, floor - wall_top + 12))
        pygame.draw.rect(s, TANK, (left - 8, floor, right - left + 16, 12))

        # Jõud
        weight = sim.mass * sim.g
        fmax = max(weight, sim.rho_w * sim.g * sim.area * sim.thick)
        lg, lb = 110 * weight / fmax, 110 * sim.fb / fmax
        draw_arrow(s, RED, (bx, by), (bx, by + lg))
        self.text("mg", self.f_b, RED, (bx + 8, by + lg - 8))
        if lb > 3:
            draw_arrow(s, GREEN, (bx, by), (bx, by - lb))
            self.text("FA", self.f_b, GREEN, (bx + 8, by - lb - 8))

        # Joonlaud
        pygame.draw.line(s, DARK, (SCENE.x + 8, floor), (SCENE.x + 8, floor - sc), 3)
        self.text("1 m", self.f_s, DARK, (SCENE.x + 3, floor - sc - 16))

        # Tekstid
        self.text(self.status(), self.f_big, DARK, (SCENE.x + 20, 14))
        info = f"t = {sim.t:.1f} s    simulatsiooni kiirus x{self.speed:g}"
        if self.paused:
            info += "    PAUS"
        self.text(info, self.f_i, DARK, (SCENE.x + 20, 50))
        self.text("— raskusjõud", self.f_i, RED, (SCENE.right - 170, 14))
        self.text("— Archimedese jõud", self.f_i, GREEN, (SCENE.right - 170, 34))
        s.set_clip(None)

    # Tsükkel
    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.on_click(e.pos)
                elif e.type == pygame.KEYDOWN:
                    self.on_key(e)
            self.update(dt)
            self.draw_scene()
            self.draw_panel()
            pygame.display.flip()


if __name__ == "__main__":
    App().run()