import math

import pygame

BASE_WIDTH = 800
BASE_HEIGHT = 480
GRAVITY = 9.81
PIXELS_PER_METRE = 45
SCENE_TOP = 160
WHITE = (255, 255, 255)
BLACK = (28, 33, 40)
GRAY = (100, 110, 120)
BLUE = (50, 150, 255)
RED = (210, 70, 65)
GREEN = (190, 235, 80)
DEFAULT_SETTINGS = {"mass": "10", "friction": "0.20", "speed": "0", "angle": "20"}


def parse_settings(settings):
    try:
        mass, friction, speed, angle = (float(settings[key]) for key in ("mass", "friction", "speed", "angle"))
    except ValueError:
        raise ValueError("Enter a valid number in each field.") from None
    if not math.isfinite(mass) or not 0 < mass <= 1_000_000:
        raise ValueError("Mass must be greater than 0 and at most 1,000,000 kg.")
    if not math.isfinite(friction) or not 0 <= friction <= 10:
        raise ValueError("Friction coefficient must be between 0 and 10.")
    if not math.isfinite(speed) or not 0 <= speed <= 100:
        raise ValueError("Starting speed must be between 0 and 100 m/s.")
    if not math.isfinite(angle) or not 0 <= angle <= 60:
        raise ValueError("Ramp angle must be between 0 and 60 degrees.")
    return mass, friction, speed, angle


def downhill_acceleration(friction, angle):
    radians = math.radians(angle)
    return GRAVITY * (math.sin(radians) - friction * math.cos(radians))


def advance_motion(position, speed, elapsed, dt, friction, angle):
    """Slide downhill; use the same coefficient for static and kinetic friction."""
    acceleration = downhill_acceleration(friction, angle)
    if speed <= 0 and acceleration <= 1e-12:
        return position, 0.0, elapsed
    moving_time = min(dt, speed / -acceleration) if acceleration < 0 else dt
    position += speed * moving_time + 0.5 * acceleration * moving_time**2
    speed = max(0.0, speed + acceleration * moving_time)
    return position, speed, elapsed + moving_time

def main():
    pygame.init()
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Ramp - Friction Simulation")
    clock = pygame.time.Clock()
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    fonts = {size: pygame.font.SysFont("Arial", size) for size in (13, 15, 18, 24)}
    settings = DEFAULT_SETTINGS.copy()
    active_settings = parse_settings(settings)
    mass, friction, initial_speed, angle = active_settings
    position = speed = elapsed = 0.0
    started = False
    simulation_running = False
    focused_field = None
    select_all = False
    status = "Set the values, then press Start."
    running = True
    fields = {
        "mass": pygame.Rect(24, 89, 105, 32),
        "friction": pygame.Rect(144, 89, 110, 32),
        "speed": pygame.Rect(269, 89, 130, 32),
        "angle": pygame.Rect(414, 89, 110, 32),
    }
    buttons = {
        "start": pygame.Rect(542, 89, 70, 32),
        "stop": pygame.Rect(622, 89, 70, 32),
        "reset": pygame.Rect(702, 89, 74, 32),
    }

    def text(value, point, size=15, color=BLACK):
        canvas.blit(fonts[size].render(value, True, color), point)

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        width, height = screen.get_size()
        scale = max(0.001, min(width / BASE_WIDTH, height / BASE_HEIGHT))
        display_size = (max(1, round(BASE_WIDTH * scale)), max(1, round(BASE_HEIGHT * scale)))
        offset = ((width - display_size[0]) // 2, (height - display_size[1]) // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = ((event.pos[0] - offset[0]) / scale, (event.pos[1] - offset[1]) / scale)
                focused_field = next((key for key, rect in fields.items() if rect.collidepoint(mouse)), None)
                select_all = focused_field is not None
                if focused_field:
                    simulation_running = False
                    status = "Paused. Changed values start a new slide when you press Start."
                elif buttons["start"].collidepoint(mouse):
                    try:
                        new_settings = parse_settings(settings)
                    except ValueError as error:
                        status = str(error)
                        continue
                    if not started or new_settings != active_settings or speed <= 0:
                        active_settings = new_settings
                        mass, friction, initial_speed, angle = active_settings
                        position = elapsed = 0.0
                        speed = initial_speed
                        started = True
                    simulation_running = speed > 0 or downhill_acceleration(friction, angle) > 1e-12
                    status = "Sliding..." if simulation_running else "At rest: increase the ramp angle or starting speed, or reduce friction."
                elif buttons["stop"].collidepoint(mouse):
                    simulation_running = False
                    status = "Paused. Press Start to resume."
                elif buttons["reset"].collidepoint(mouse):
                    settings = DEFAULT_SETTINGS.copy()
                    active_settings = parse_settings(settings)
                    mass, friction, initial_speed, angle = active_settings
                    position = speed = elapsed = 0.0
                    started = simulation_running = False
                    status = "Reset. Set the values, then press Start."
            elif event.type == pygame.KEYDOWN and focused_field:
                value = settings[focused_field]
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    focused_field = None
                    select_all = False
                    continue
                if event.key == pygame.K_TAB:
                    keys = list(fields)
                    focused_field = keys[(keys.index(focused_field) + 1) % len(keys)]
                    select_all = True
                    continue
                if event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    select_all = True
                    continue
                if event.key == pygame.K_BACKSPACE:
                    value = "" if select_all else value[:-1]
                    select_all = False
                elif event.key == pygame.K_DELETE:
                    value = ""
                    select_all = False
                elif event.unicode and event.unicode in "0123456789.":
                    if select_all:
                        value = ""
                    select_all = False
                    if len(value) < 12 and (event.unicode != "." or "." not in value):
                        value += event.unicode
                settings[focused_field] = value

        if simulation_running:
            position, speed, elapsed = advance_motion(position, speed, elapsed, dt, friction, angle)
            if speed <= 0:
                simulation_running = False
                status = "The body has stopped. Press Start to repeat the slide."

        canvas.fill(WHITE)
        text("Sliding down a ramp", (24, 17), 24)
        text("Adjust the slope, mass, and friction. Start from rest or give the block an initial speed.", (24, 47), 13, GRAY)
        for key, label in (("mass", "Mass (kg)"), ("friction", "Friction coeff."), ("speed", "Start speed (m/s)"), ("angle", "Ramp angle (°)")):
            rect = fields[key]
            text(label, (rect.x, 68), 13)
            pygame.draw.rect(canvas, (235, 245, 255) if focused_field == key and select_all else WHITE, rect)
            pygame.draw.rect(canvas, BLUE if focused_field == key else GRAY, rect, 2, border_radius=4)
            text(settings[key], (rect.x + 8, rect.y + 6), 18)
        for key, label, color in (("start", "Start", GREEN), ("stop", "Stop", (245, 185, 180)), ("reset", "Reset", (230, 234, 239))):
            rect = buttons[key]
            pygame.draw.rect(canvas, color, rect, border_radius=5)
            label_image = fonts[15].render(label, True, BLACK)
            canvas.blit(label_image, label_image.get_rect(center=rect.center))
        text(status, (24, 135), 13, GRAY)

        # Follow the block along an extended incline as it moves downhill.
        radians = math.radians(angle)
        tangent = pygame.Vector2(math.cos(radians), math.sin(radians))
        normal = pygame.Vector2(tangent.y, -tangent.x)
        camera = max(0.0, position * PIXELS_PER_METRE - 120)
        origin = pygame.Vector2(110, 225)
        contact = origin + tangent * (position * PIXELS_PER_METRE - camera)
        previous_clip = canvas.get_clip()
        canvas.set_clip(pygame.Rect(0, SCENE_TOP, BASE_WIDTH, 218))
        left = origin - tangent * 1000
        right = origin + tangent * 1600
        pygame.draw.polygon(canvas, (237, 240, 243), [left, right, right + pygame.Vector2(0, 1800), left + pygame.Vector2(0, 1800)])
        pygame.draw.line(canvas, GRAY, left, right, 2)
        first_metre = math.floor(camera / PIXELS_PER_METRE) - 5
        for metre in range(first_metre, first_metre + 42):
            point = origin + tangent * (metre * PIXELS_PER_METRE - camera)
            pygame.draw.line(canvas, GRAY, point, point - normal * 8)
            if metre >= 0 and metre % 2 == 0:
                text(f"{metre} m", point - normal * 21, 13, GRAY)
        block_image = pygame.Surface((76, 44), pygame.SRCALPHA)
        pygame.draw.rect(block_image, BLUE, block_image.get_rect(), border_radius=4)
        pygame.draw.rect(block_image, BLACK, block_image.get_rect(), 2, border_radius=4)
        label_image = fonts[13].render(f"{mass:g} kg", True, BLACK)
        block_image.blit(label_image, label_image.get_rect(center=(38, 22)))
        rotated_block = pygame.transform.rotate(block_image, -angle)
        centre = contact + normal * 22
        canvas.blit(rotated_block, rotated_block.get_rect(center=(round(centre.x), round(centre.y))))
        if speed > 0:
            tail = contact + normal * 62 - tangent * 22
            tip = tail + tangent * 65
            pygame.draw.line(canvas, BLUE, tail, tip, 3)
            pygame.draw.polygon(canvas, BLUE, [tip, tip - tangent * 10 + normal * 5, tip - tangent * 10 - normal * 5])
            text("Velocity", tail + normal * 23, 13, BLUE)
        if friction > 0:
            tail = centre - tangent * 42
            tip = tail - tangent * 45
            pygame.draw.line(canvas, RED, tail, tip, 3)
            pygame.draw.polygon(canvas, RED, [tip, tip + tangent * 10 + normal * 5, tip + tangent * 10 - normal * 5])
            text("Friction", tail + normal * 23 - tangent * 40, 13, RED)
        canvas.set_clip(previous_clip)

        normal_force = mass * GRAVITY * math.cos(radians)
        downhill_force = mass * GRAVITY * math.sin(radians)
        friction_force = friction * normal_force if speed > 0 else min(downhill_force, friction * normal_force)
        acceleration = (downhill_force - friction_force) / mass
        text(f"Speed: {speed:.2f} m/s", (24, 390), 18)
        text(f"Along ramp: {position:.2f} m", (275, 390), 18)
        text(f"Time: {elapsed:.2f} s", (560, 390), 18)
        text(f"Friction force: {friction_force:.2f} N", (24, 421), 15)
        text(f"Downhill acceleration: {acceleration:.2f} m/s²", (350, 421), 15)
        text("Friction uses the same coefficient at rest and while sliding. The view follows the block downhill.", (24, 452), 13, GRAY)
        screen.fill(WHITE)
        screen.blit(pygame.transform.smoothscale(canvas, display_size), offset)
        pygame.display.flip()

    #pygame.quit()


if True:
    main()
