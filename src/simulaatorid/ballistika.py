"""Orbit Lab: a Pygame projectile simulator. Run with `python gravity.py`."""

import math
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 1180, 760
GRAVITY = 10.0  # m/s²; matches the original 500 px/s² at 50 px/m.
IMPULSE_SECONDS = 0.2
BG = (12, 18, 30)
PANEL = (20, 29, 45)
FIELD = (13, 22, 36)
BORDER = (43, 58, 79)
TEXT = (231, 239, 250)
MUTED = (143, 161, 185)
CYAN = (74, 222, 204)
ORANGE = (255, 184, 107)
RED = (255, 128, 140)
PROJECTILES = (
    ("Light", 0.5, 6, (116, 189, 255)),
    ("Medium", 1.0, 8, CYAN),
    ("Heavy", 2.0, 11, ORANGE),
)


@dataclass(frozen=True)
class Shot:
    force: float
    angle: float
    kind: int

    @property
    def speed(self):
        return self.force * IMPULSE_SECONDS / PROJECTILES[self.kind][1]

    @property
    def vx(self):
        return self.speed * math.cos(math.radians(self.angle))

    @property
    def vy(self):
        return self.speed * math.sin(math.radians(self.angle))

    @property
    def duration(self):
        return 2 * self.vy / GRAVITY

    @property
    def distance(self):
        return self.vx * self.duration

    @property
    def apex(self):
        return self.vy**2 / (2 * GRAVITY)

    def position(self, time):
        return self.vx * time, max(0.0, self.vy * time - 0.5 * GRAVITY * time**2)


class Simulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Orbit Lab | Ballistic Simulator")
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {}
        self.values = {"force": "60", "angle": "45"}
        self.focus = None
        self.select_all = False
        self.kind = 1
        self.shot = None
        self.elapsed = 0.0
        self.state = "ready"
        self.error = ""
        self.slow = False
        self.mouse = (-1, -1)
        self.viewport = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.controls = {
            "force": pygame.Rect(44, 214, 228, 54),
            "angle": pygame.Rect(44, 316, 228, 54),
            "launch": pygame.Rect(44, 566, 228, 48),
            "pause": pygame.Rect(44, 626, 108, 42),
            "reset": pygame.Rect(164, 626, 108, 42),
            "slow": pygame.Rect(978, 121, 144, 32),
        }
        self.cards = [pygame.Rect(44 + i * 78, 431, 72, 92) for i in range(3)]

    def font(self, size, bold=False):
        key = size, bold
        if key not in self.fonts:
            self.fonts[key] = pygame.font.SysFont("segoeui", size, bold=bold)
        return self.fonts[key]

    def text(self, message, x, y, size=16, color=TEXT, bold=False):
        self.canvas.blit(self.font(size, bold).render(str(message), True, color), (x, y))

    def box(self, rect, color=PANEL, border=None, radius=14):
        pygame.draw.rect(self.canvas, color, rect, border_radius=radius)
        if border:
            pygame.draw.rect(self.canvas, border, rect, width=1, border_radius=radius)

    def button(self, name, title, primary=False, enabled=True):
        rect = self.controls[name]
        hover = rect.collidepoint(self.mouse) and enabled
        color = CYAN if primary else ((35, 49, 68) if hover else PANEL)
        if primary and hover:
            color = (110, 239, 221)
        self.box(rect, color, None if primary else BORDER, 10)
        ink = BG if primary else (TEXT if enabled else MUTED)
        label = self.font(16, True).render(title, True, ink)
        self.canvas.blit(label, label.get_rect(center=rect.center))

    def parameters(self):
        try:
            force, angle = float(self.values["force"]), float(self.values["angle"])
        except ValueError:
            raise ValueError("Enter a number in both fields.") from None
        if not math.isfinite(force) or not 0 < force <= 500:
            raise ValueError("Force must be between 0 and 500 N.")
        if not math.isfinite(angle) or not 0 <= angle <= 90:
            raise ValueError("Angle must be between 0 and 90°.")
        return Shot(force, angle, self.kind)

    def launch(self):
        try:
            shot = self.parameters()
        except ValueError as exc:
            self.error = str(exc)
            return
        self.shot = shot
        self.elapsed = 0.0
        self.state = "flying" if shot.duration > 1e-10 else "landed"
        self.error = ""
        self.focus = None

    def reset(self):
        self.shot = None
        self.elapsed = 0.0
        self.state = "ready"
        self.error = ""

    def pause(self):
        if self.state in ("flying", "paused"):
            self.state = "paused" if self.state == "flying" else "flying"

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = self.logical_position(event.pos)
            self.focus = None
            for name in ("force", "angle"):
                if self.controls[name].collidepoint(pos):
                    self.focus = name
                    self.select_all = True
                    return
            for i, card in enumerate(self.cards):
                if card.collidepoint(pos):
                    self.kind = i
                    return
            for name, action in (("launch", self.launch), ("pause", self.pause), ("reset", self.reset)):
                if self.controls[name].collidepoint(pos):
                    action()
                    return
            if self.controls["slow"].collidepoint(pos):
                self.slow = not self.slow
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.focus = None
            elif event.key == pygame.K_TAB:
                self.focus = "angle" if self.focus == "force" else "force"
                self.select_all = True
            elif self.focus:
                if event.key == pygame.K_RETURN:
                    self.launch()
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    self.select_all = True
                elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                    self.values[self.focus] = "" if self.select_all or event.key == pygame.K_DELETE else self.values[self.focus][:-1]
                    self.select_all = False
                elif event.unicode and event.unicode in "0123456789.":
                    value = "" if self.select_all else self.values[self.focus]
                    if len(value) < 9 and (event.unicode != "." or "." not in value):
                        self.values[self.focus] = value + event.unicode
                        self.select_all = False
                        self.error = ""
            elif event.key == pygame.K_SPACE:
                if self.state in ("flying", "paused"):
                    self.pause()
                else:
                    self.launch()
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key == pygame.K_RETURN:
                self.launch()

    def update(self, dt):
        if self.state == "flying" and self.shot:
            self.elapsed = min(self.shot.duration, self.elapsed + min(dt, 0.05) * (0.25 if self.slow else 1))
            if self.elapsed >= self.shot.duration:
                self.state = "landed"

    def logical_position(self, pos):
        return ((pos[0] - self.viewport.x) * WIDTH / self.viewport.width,
                (pos[1] - self.viewport.y) * HEIGHT / self.viewport.height)

    def draw_sidebar(self):
        self.box((24, 116, 268, 578), PANEL, BORDER, 18)
        self.text("LAUNCH SETUP", 44, 139, 13, CYAN, True)
        self.text("Set your trajectory.", 44, 163, 21, bold=True)
        for name, label, unit, y, hint in (
            ("force", "Launch force", "N", 190, "0 < force ≤ 500 N"),
            ("angle", "Launch angle", "°", 292, "0° horizontal  /  90° vertical"),
        ):
            self.text(label, 44, y, 14, MUTED)
            rect = self.controls[name]
            active = self.focus == name
            self.box(rect, FIELD, CYAN if active else BORDER, 10)
            if active and self.select_all:
                self.box((55, rect.y + 10, max(16, self.font(23, True).size(self.values[name])[0] + 5), 32), (43, 83, 100), radius=4)
            self.text(self.values[name], 58, rect.y + 10, 23, bold=True)
            self.text(unit, rect.right - 30, rect.y + 15, 18, MUTED)
            if active and not self.select_all and pygame.time.get_ticks() % 1000 < 500:
                x = 60 + self.font(23, True).size(self.values[name])[0]
                pygame.draw.line(self.canvas, CYAN, (x, rect.y + 14), (x, rect.y + 39), 2)
            self.text(hint, 46, rect.bottom + 5, 12, MUTED)
        self.text("Projectile mass", 44, 405, 14, MUTED)
        for i, (name, mass, radius, color) in enumerate(PROJECTILES):
            rect = self.cards[i]
            self.box(rect, (28, 49, 61) if i == self.kind else FIELD, CYAN if i == self.kind else BORDER, 10)
            pygame.draw.circle(self.canvas, color, (rect.centerx, rect.y + 22), radius)
            self.text(name, rect.x + 9, rect.y + 41, 13, bold=True)
            self.text(f"{mass:g} kg", rect.x + 12, rect.y + 63, 13, MUTED)
        self.text("Impulse duration  ·  0.20 s", 44, 537, 13, MUTED)
        self.button("launch", "Launch projectile  →", primary=True)
        self.button("pause", "Resume" if self.state == "paused" else "Pause", enabled=self.state in ("paused", "flying"))
        self.button("reset", "Reset")

    def draw_plot(self, shot):
        self.box((312, 116, 844, 450), PANEL, BORDER, 18)
        self.text("TRAJECTORY", 336, 132, 13, MUTED, True)
        self.text("Ideal motion  ·  no air resistance", 336, 156, 13, MUTED)
        self.button("slow", "0.25× speed" if self.slow else "1× speed")
        # One scale for both axes preserves the physical shape of the parabola.
        plot = pygame.Rect(365, 208, 742, 297)
        scale = min(plot.width / max(18, shot.distance * 1.16), plot.height / max(7, shot.apex * 1.3))
        origin = pygame.Vector2(plot.left, plot.bottom)

        def point(time):
            x, y = shot.position(time)
            return origin + pygame.Vector2(x * scale, -y * scale)

        span = plot.width / scale
        raw = span / 7
        base = 10 ** math.floor(math.log10(raw))
        step = next(n * base for n in (1, 2, 5, 10) if n * base >= raw)
        for i in range(int(span / step) + 1):
            x = round(origin.x + i * step * scale)
            pygame.draw.line(self.canvas, (31, 44, 62), (x, plot.top), (x, plot.bottom))
            self.text(f"{i * step:g}", x - 4, 516, 11, MUTED)
        for i in range(int(plot.height / scale / step) + 1):
            y = round(origin.y - i * step * scale)
            pygame.draw.line(self.canvas, (31, 44, 62), (plot.left, y), (plot.right, y))
            self.text(f"{i * step:g}", 327, y - 8, 11, MUTED)
        self.text("m", 330, 190, 11, MUTED)
        self.text("DISTANCE / m", 1006, 540, 10, MUTED, True)
        pygame.draw.line(self.canvas, (70, 99, 112), origin, (plot.right, plot.bottom), 2)

        for i in range(1, 81):
            pygame.draw.circle(self.canvas, (67, 97, 111), point(shot.duration * i / 80), 2)
        if shot.apex > 0.1:
            apex = point(shot.duration / 2)
            pygame.draw.circle(self.canvas, ORANGE, apex, 4)
            self.text(f"APEX  {shot.apex:.1f} m", min(apex.x + 12, plot.right - 125), apex.y - 22, 12, ORANGE, True)

        angle = math.radians(shot.angle)
        barrel = origin + pygame.Vector2(math.cos(angle), -math.sin(angle)) * 35
        pygame.draw.line(self.canvas, (45, 84, 94), origin, barrel, 15)
        pygame.draw.line(self.canvas, CYAN, origin, barrel, 7)
        pygame.draw.circle(self.canvas, (37, 57, 72), origin, 14)
        pygame.draw.circle(self.canvas, CYAN, origin, 6)
        if self.shot:
            points = [point(self.elapsed * i / 120) for i in range(121)]
            pygame.draw.lines(self.canvas, CYAN, False, points, 3)
            pos = point(self.elapsed)
            _, _, radius, color = PROJECTILES[shot.kind]
            glow = pygame.Surface((64, 64), pygame.SRCALPHA)
            for r, alpha in ((24, 12), (18, 20), (13, 30)):
                pygame.draw.circle(glow, (*color, alpha), (32, 32), r)
            self.canvas.blit(glow, (pos.x - 32, pos.y - 32))
            pygame.draw.circle(self.canvas, color, pos, radius)
            pygame.draw.circle(self.canvas, TEXT, pos, radius, 1)
            if self.state == "landed":
                self.text("LANDED", min(pos.x + 13, plot.right - 66), pos.y - 26, 11, CYAN, True)

    def draw(self):
        self.canvas.fill(BG)
        self.box((24, 28, 44, 44), (26, 57, 64), radius=13)
        pygame.draw.circle(self.canvas, CYAN, (46, 50), 12, 1)
        pygame.draw.circle(self.canvas, CYAN, (54, 41), 4)
        self.text("ORBIT LAB", 82, 23, 28, bold=True)
        self.text("Ballistic simulator / explore motion", 83, 62, 14, MUTED)
        status = {"ready": "READY TO LAUNCH", "flying": "IN FLIGHT", "paused": "SIMULATION PAUSED", "landed": "FLIGHT COMPLETE"}[self.state]
        self.box((928, 37, 228, 35), PANEL, BORDER, 17)
        pygame.draw.circle(self.canvas, ORANGE if self.state == "paused" else CYAN, (945, 54), 4)
        self.text(status, 958, 44, 12, bold=True)
        self.draw_sidebar()
        try:
            preview = self.parameters()
        except ValueError:
            preview = Shot(60, 45, self.kind)
        shot = self.shot or preview
        self.draw_plot(shot)
        self.text("FLIGHT TELEMETRY" if self.shot else "PREDICTED FLIGHT", 314, 584, 12, MUTED, True)
        _, altitude = shot.position(self.elapsed)
        speed = math.hypot(shot.vx, shot.vy - GRAVITY * self.elapsed)
        stats = (("SPEED", f"{speed:.1f}", "m/s"), ("ALTITUDE", f"{altitude:.1f}", "m"),
                 ("RANGE", f"{shot.distance:.1f}", "m"), ("FLIGHT TIME", f"{self.elapsed:.2f}" if self.shot else f"{shot.duration:.2f}", "s"))
        for i, (label, value, unit) in enumerate(stats):
            left = 312 + i * 214
            self.box((left, 610, 202, 84), PANEL, BORDER, 12)
            self.text(label, left + 16, 621, 11, MUTED, True)
            self.text(value, left + 16, 642, 27, CYAN if i == 0 else TEXT, True)
            self.text(unit, left + 154, 656, 13, MUTED)
        if self.error:
            self.text(self.error, 314, 708, 14, RED)
        else:
            self.text("SPACE  launch / pause     R  reset     TAB  switch input", 26, 715, 12, MUTED)
            self.text("g = 10 m/s²   ·   Scale adjusts to fit the full flight", 823, 715, 12, MUTED)
        width, height = self.screen.get_size()
        scale = min(width / WIDTH, height / HEIGHT)
        size = max(1, round(WIDTH * scale)), max(1, round(HEIGHT * scale))
        self.viewport = pygame.Rect((width - size[0]) // 2, (height - size[1]) // 2, *size)
        self.screen.fill(BG)
        self.screen.blit(pygame.transform.smoothscale(self.canvas, size), self.viewport)
        pygame.display.flip()

    def run(self):
        running = True
        try:
            while running:
                dt = self.clock.tick(60) / 1000
                self.mouse = self.logical_position(pygame.mouse.get_pos())
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    else:
                        self.event(event)
                self.update(dt)
                self.draw()
        finally:
            pygame.quit()



Simulator().run()
