import math

import pygame

pygame.init()

BASE_WIDTH = 600
BASE_HEIGHT = 400
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Ballistic Simulator")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (190, 235, 80)
RED = (235, 100, 100)
BLUE = (50, 150, 255)
GRAY = (100, 100, 100)

GRAVITY = 500.0
PIXELS_PER_METER = 50.0
LAUNCH_IMPULSE_SECONDS = 0.2

PROJECTILES = [
    {"name": "Light", "mass": 0.5, "radius": 5, "color": BLUE},
    {"name": "Medium", "mass": 1.0, "radius": 8, "color": BLACK},
    {"name": "Heavy", "mass": 2.0, "radius": 11, "color": GRAY},
]

launcher_pos = pygame.Vector2(95, 355)
projectile = None
velocity = pygame.Vector2()
flying = False
trajectory = []

force_text = "60"
angle_text = "45"
projectile_index = 1
focused_field = None
dropdown_open = False
status_message = ""
status_color = RED
running = True


def get_scale():
    width, height = screen.get_size()
    return min(width / BASE_WIDTH, height / BASE_HEIGHT)


def to_screen(pos):
    pos = pygame.Vector2(pos)
    scale = get_scale()
    width, height = screen.get_size()
    offset_x = (width - BASE_WIDTH * scale) / 2
    offset_y = (height - BASE_HEIGHT * scale) / 2
    return pygame.Vector2(
        offset_x + pos.x * scale,
        offset_y + pos.y * scale,
    )


def from_screen(pos):
    scale = get_scale()
    width, height = screen.get_size()
    offset_x = (width - BASE_WIDTH * scale) / 2
    offset_y = (height - BASE_HEIGHT * scale) / 2
    return pygame.Vector2(
        (pos[0] - offset_x) / scale,
        (pos[1] - offset_y) / scale,
    )


def scaled_rect(x, y, width, height):
    first = to_screen((x, y))
    second = to_screen((x + width, y + height))
    return pygame.Rect(
        round(first.x),
        round(first.y),
        round(second.x - first.x),
        round(second.y - first.y),
    )


def font(size, bold=False):
    return pygame.font.SysFont("Arial", max(9, round(size * get_scale())), bold=bold)


def draw_text(text, position, size=12, color=BLACK, bold=False):
    image = font(size, bold).render(text, True, color)
    screen.blit(image, to_screen(position))


def draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, max(1, round(2 * get_scale())))
    image = font(13, True).render(text, True, BLACK)
    screen.blit(
        image,
        (rect.centerx - image.get_width() // 2, rect.centery - image.get_height() // 2),
    )


def draw_input(rect, value, active=False):
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(
        screen,
        BLUE if active else BLACK,
        rect,
        max(1, round((2 if active else 1) * get_scale())),
    )
    image = font(12).render(value, True, BLACK)
    screen.blit(
        image,
        (rect.x + round(4 * get_scale()), rect.centery - image.get_height() // 2),
    )


def draw_dotted_line(points, color=BLACK):
    if len(points) < 2:
        return

    scale = get_scale()
    spacing = 18 * scale
    radius = max(2, round(5 * scale))
    distance = 0

    for index in range(1, len(points)):
        first = to_screen(points[index - 1])
        second = to_screen(points[index])
        segment = second - first
        length = segment.length()
        if length == 0:
            continue
        direction = segment.normalize()
        while distance < length:
            point = first + direction * distance
            pygame.draw.circle(screen, color, (round(point.x), round(point.y)), radius)
            distance += spacing
        distance -= length


def start_simulation():
    global projectile, velocity, flying, trajectory, status_message

    try:
        force = float(force_text)
        angle = float(angle_text)
    except ValueError:
        status_message = "Enter a valid number for force and angle."
        return

    if not math.isfinite(force) or not 0 < force <= 500:
        status_message = "Force must be greater than 0 and at most 500 N."
        return
    if not math.isfinite(angle) or not 0 <= angle <= 90:
        status_message = "Angle must be between 0 and 90 degrees."
        return

    selected = PROJECTILES[projectile_index]
    speed = (
        force
        / selected["mass"]
        * LAUNCH_IMPULSE_SECONDS
        * PIXELS_PER_METER
    )
    radians = math.radians(angle)
    velocity = pygame.Vector2(
        math.cos(radians) * speed,
        -math.sin(radians) * speed,
    )
    projectile = launcher_pos.copy()
    flying = True
    trajectory = [projectile.copy()]
    status_message = ""


def stop_simulation():
    global flying, status_message
    flying = False
    status_message = "Simulation stopped."


def set_projectile(index):
    global projectile_index, dropdown_open
    projectile_index = index % len(PROJECTILES)
    dropdown_open = False


while running:
    dt = clock.tick(60) / 1000.0

    start_rect = scaled_rect(80, 7, 52, 32)
    stop_rect = scaled_rect(138, 7, 48, 32)
    force_rect = scaled_rect(223, 11, 55, 24)
    projectile_rect = scaled_rect(348, 11, 91, 24)
    angle_rect = scaled_rect(492, 11, 51, 24)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            focused_field = None

            if start_rect.collidepoint(event.pos):
                dropdown_open = False
                start_simulation()
            elif stop_rect.collidepoint(event.pos):
                dropdown_open = False
                stop_simulation()
            elif force_rect.collidepoint(event.pos):
                focused_field = "force"
                dropdown_open = False
            elif angle_rect.collidepoint(event.pos):
                focused_field = "angle"
                dropdown_open = False
            elif projectile_rect.collidepoint(event.pos):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                for index in range(len(PROJECTILES)):
                    option_rect = scaled_rect(
                        348,
                        35 + index * 24,
                        91,
                        24,
                    )
                    if option_rect.collidepoint(event.pos):
                        set_projectile(index)
                        break
                else:
                    dropdown_open = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                focused_field = None
                dropdown_open = False
            elif dropdown_open and event.key in (pygame.K_UP, pygame.K_DOWN):
                step = -1 if event.key == pygame.K_UP else 1
                set_projectile(projectile_index + step)
            elif focused_field:
                value = force_text if focused_field == "force" else angle_text
                if event.key == pygame.K_BACKSPACE:
                    value = value[:-1]
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    value = ""
                elif event.key == pygame.K_RETURN:
                    focused_field = None
                elif event.key == pygame.K_DELETE:
                    value = ""
                elif event.unicode and event.unicode in "0123456789.":
                    if event.unicode != "." or "." not in value:
                        value += event.unicode

                if focused_field == "force":
                    force_text = value
                elif focused_field == "angle":
                    angle_text = value

    if flying and projectile is not None:
        velocity.y += GRAVITY * dt
        projectile += velocity * dt
        trajectory.append(projectile.copy())

        if projectile.y >= BASE_HEIGHT - 12:
            projectile.y = BASE_HEIGHT - 12
            flying = False
        elif projectile.x > BASE_WIDTH or projectile.x < 72 or projectile.y < 48:
            flying = False

    screen.fill(WHITE)
    scale = get_scale()

    # Workspace and frame echo the reference's heavy black borders.
    pygame.draw.rect(screen, WHITE, scaled_rect(72, 48, 528, 352))
    pygame.draw.rect(screen, BLACK, scaled_rect(72, 48, 528, 352), max(2, round(3 * scale)))
    pygame.draw.rect(screen, WHITE, scaled_rect(0, 0, 72, 400))
    pygame.draw.line(
        screen,
        BLACK,
        to_screen((72, 47)),
        to_screen((600, 47)),
        max(2, round(4 * scale)),
    )

    # Left tool rail.
    for y in (55, 111, 167, 223, 279, 335):
        pygame.draw.rect(screen, WHITE, scaled_rect(5, y, 58, 46))
        pygame.draw.rect(screen, BLACK, scaled_rect(5, y, 58, 46), max(2, round(3 * scale)))

    pygame.draw.circle(screen, BLACK, tuple(map(round, to_screen((26, 78)))), max(3, round(7 * scale)))
    pygame.draw.line(screen, BLACK, to_screen((28, 78)), to_screen((49, 65)), max(2, round(3 * scale)))
    pygame.draw.line(screen, BLACK, to_screen((34, 120)), to_screen((34, 145)), max(2, round(3 * scale)))
    pygame.draw.polygon(screen, BLACK, [to_screen((27, 139)), to_screen((34, 148)), to_screen((41, 139))])
    pygame.draw.rect(screen, BLACK, scaled_rect(18, 177, 29, 22), max(2, round(2 * scale)))
    pygame.draw.circle(screen, BLACK, tuple(map(round, to_screen((32, 202)))), max(2, round(5 * scale)))
    pygame.draw.circle(screen, BLUE, tuple(map(round, to_screen((32, 247)))), max(3, round(13 * scale)), max(1, round(2 * scale)))
    pygame.draw.arc(screen, RED, scaled_rect(18, 233, 28, 28), 0, math.pi, max(1, round(2 * scale)))
    pygame.draw.line(screen, BLACK, to_screen((15, 291)), to_screen((48, 310)), max(2, round(3 * scale)))
    pygame.draw.polygon(screen, BLACK, [to_screen((48, 310)), to_screen((40, 300)), to_screen((39, 308))])
    pygame.draw.circle(screen, BLUE, tuple(map(round, to_screen((27, 358)))), max(3, round(12 * scale)))
    pygame.draw.circle(screen, GREEN, tuple(map(round, to_screen((39, 360)))), max(2, round(5 * scale)))

    # Top toolbar: launch controls and editable launch parameters.
    draw_button(start_rect, "Start", GREEN)
    draw_button(stop_rect, "Stop", RED)
    draw_text("Force", (190, 17), 12, bold=True)
    draw_input(force_rect, force_text, focused_field == "force")
    draw_text("N", (281, 17), 12)
    draw_text("Projectile", (291, 17), 11, bold=True)
    draw_input(projectile_rect, PROJECTILES[projectile_index]["name"])
    arrow = [
        to_screen((426, 20)),
        to_screen((433, 20)),
        to_screen((429.5, 25)),
    ]
    pygame.draw.polygon(screen, BLACK, arrow)
    draw_text("Angle", (454, 17), 12, bold=True)
    draw_input(angle_rect, angle_text, focused_field == "angle")
    draw_text("°", (548, 17), 12)

    # Trajectory path.
    if len(trajectory) > 1:
        draw_dotted_line(trajectory)

    # Launcher and projectile.
    launcher_screen = to_screen(launcher_pos)
    pygame.draw.circle(screen, BLACK, tuple(map(round, launcher_screen)), max(2, round(12 * scale)))
    barrel_angle = math.radians(float(angle_text)) if angle_text.replace(".", "", 1).isdigit() else math.pi / 4
    barrel_end = launcher_pos + pygame.Vector2(
        math.cos(barrel_angle) * 36,
        -math.sin(barrel_angle) * 36,
    )
    pygame.draw.line(
        screen,
        BLACK,
        launcher_screen,
        to_screen(barrel_end),
        max(2, round(8 * scale)),
    )

    if projectile is not None:
        selected = PROJECTILES[projectile_index]
        point = to_screen(projectile)
        radius = max(2, round(selected["radius"] * scale))
        pygame.draw.circle(screen, selected["color"], tuple(map(round, point)), radius)
        pygame.draw.circle(screen, BLACK, tuple(map(round, point)), radius, max(1, round(scale)))

    if status_message:
        message_rect = scaled_rect(82, 53, 510, 22)
        pygame.draw.rect(screen, WHITE, message_rect)
        draw_text(status_message, (87, 57), 11, status_color)

    if dropdown_open:
        for index, item in enumerate(PROJECTILES):
            option_rect = scaled_rect(348, 35 + index * 24, 91, 24)
            pygame.draw.rect(screen, WHITE, option_rect)
            pygame.draw.rect(screen, BLACK, option_rect, max(1, round(scale)))
            draw_text(f"{item['name']} ({item['mass']:g} kg)", (352, 41 + index * 24), 10)

    pygame.display.flip()

pygame.quit()
