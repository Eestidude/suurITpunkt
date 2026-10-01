import pygame
import math

pygame.init()

# ============================================================
# WINDOW
# ============================================================

BASE_WIDTH = 600
BASE_HEIGHT = 400

screen = pygame.display.set_mode(
    (BASE_WIDTH, BASE_HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption("Ballistic Simulator")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (190, 235, 80)
RED = (235, 100, 100)
BLUE = (50, 150, 255)
GRAY = (100, 100, 100)

# ============================================================
# SIMULATION
# ============================================================

GRAVITY = 500.0
POWER = 2.0

launcher_pos = pygame.Vector2(105, 350)

projectile = None
velocity = pygame.Vector2()
flying = False

aiming = False
mouse_pos = pygame.Vector2()

trajectory = []

# ============================================================
# UI / SCALING
# ============================================================

def get_scale():
    w, h = screen.get_size()

    return min(
        w / BASE_WIDTH,
        h / BASE_HEIGHT
    )


def to_screen(pos):
    pos = pygame.Vector2(pos)

    scale = get_scale()

    w, h = screen.get_size()

    offset_x = (w - BASE_WIDTH * scale) / 2
    offset_y = (h - BASE_HEIGHT * scale) / 2

    return pygame.Vector2(
        offset_x + pos.x * scale,
        offset_y + pos.y * scale
    )


def from_screen(pos):
    """
    Convert screen coordinates back into simulation coordinates.
    """
    scale = get_scale()

    w, h = screen.get_size()

    offset_x = (w - BASE_WIDTH * scale) / 2
    offset_y = (h - BASE_HEIGHT * scale) / 2

    return pygame.Vector2(
        (pos[0] - offset_x) / scale,
        (pos[1] - offset_y) / scale
    )


def scaled_rect(x, y, w, h):
    p1 = to_screen((x, y))
    p2 = to_screen((x + w, y + h))

    return pygame.Rect(
        int(p1.x),
        int(p1.y),
        int(p2.x - p1.x),
        int(p2.y - p1.y)
    )


# ============================================================
# BUTTON
# ============================================================

def draw_button(rect, text, color):

    pygame.draw.rect(
        screen,
        color,
        rect
    )

    pygame.draw.rect(
        screen,
        BLACK,
        rect,
        max(1, int(2 * get_scale()))
    )

    font_size = max(10, int(14 * get_scale()))

    font = pygame.font.SysFont(
        "Arial",
        font_size
    )

    text_surface = font.render(
        text,
        True,
        BLACK
    )

    screen.blit(
        text_surface,
        (
            rect.centerx - text_surface.get_width() // 2,
            rect.centery - text_surface.get_height() // 2
        )
    )


# ============================================================
# DOTTED TRAJECTORY
# ============================================================

def draw_dotted_line(points, color=BLACK):

    if len(points) < 2:
        return

    scale = get_scale()

    spacing = 18 * scale
    radius = max(2, int(6 * scale))

    distance = 0

    for i in range(1, len(points)):

        p1 = to_screen(points[i - 1])
        p2 = to_screen(points[i])

        segment = p2 - p1
        length = segment.length()

        if length == 0:
            continue

        direction = segment.normalize()

        while distance < length:

            point = p1 + direction * distance

            pygame.draw.circle(
                screen,
                color,
                (int(point.x), int(point.y)),
                radius
            )

            distance += spacing

        distance -= length


# ============================================================
# RESET
# ============================================================

def reset():

    global projectile
    global velocity
    global flying
    global trajectory

    projectile = None
    velocity = pygame.Vector2()
    flying = False
    trajectory = []


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(60) / 1000.0

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ----------------------------------------------------
        # Mouse down
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_sim = from_screen(event.pos)

            # Stop button
            if scaled_rect(155, 33, 55, 30).collidepoint(event.pos):

                reset()

            # Launcher
            elif (
                mouse_sim.distance_to(launcher_pos) < 35
            ):

                aiming = True
                mouse_pos = mouse_sim

        # ----------------------------------------------------
        # Mouse movement
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEMOTION:

            if aiming:
                mouse_pos = from_screen(event.pos)

        # ----------------------------------------------------
        # Mouse release
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if aiming:

                aiming = False

                mouse_sim = from_screen(event.pos)

                direction = (
                    mouse_sim - launcher_pos
                )

                if direction.length() > 5:

                    direction.normalize_ip()

                    speed = 300 * POWER

                    velocity = direction * speed

                    projectile = launcher_pos.copy()

                    flying = True

                    trajectory = [
                        projectile.copy()
                    ]

    # --------------------------------------------------------
    # PHYSICS
    # --------------------------------------------------------

    if flying and projectile is not None:

        velocity.y += GRAVITY * dt

        projectile += velocity * dt

        trajectory.append(
            projectile.copy()
        )

        # Ground collision
        if projectile.y >= BASE_HEIGHT - 10:

            projectile.y = BASE_HEIGHT - 10

            flying = False

        # Outside world
        if (
            projectile.x < 70
            or projectile.x > BASE_WIDTH
            or projectile.y < 60
        ):

            flying = False

    # ========================================================
    # DRAW
    # ========================================================

    screen.fill(WHITE)

    scale = get_scale()

    # --------------------------------------------------------
    # Canvas
    # --------------------------------------------------------

    canvas = scaled_rect(
        75,
        0,
        BASE_WIDTH - 85,
        BASE_HEIGHT
    )

    pygame.draw.rect(
        screen,
        WHITE,
        canvas
    )

    pygame.draw.rect(
        screen,
        BLACK,
        canvas,
        max(1, int(3 * scale))
    )

    # --------------------------------------------------------
    # LEFT TOOL PANEL
    # --------------------------------------------------------

    left_panel = scaled_rect(
        0,
        0,
        72,
        BASE_HEIGHT
    )

    pygame.draw.rect(
        screen,
        BLACK,
        left_panel
    )

    # --------------------------------------------------------
    # TOOL BUTTONS
    # --------------------------------------------------------

    tool_y = [
        8,
        63,
        118,
        173,
        228,
        283
    ]

    for y in tool_y:

        rect = scaled_rect(
            5,
            y,
            58,
            45
        )

        pygame.draw.rect(
            screen,
            WHITE,
            rect
        )

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
            max(1, int(3 * scale))
        )

    # --------------------------------------------------------
    # TOOL 1
    # --------------------------------------------------------

    p = to_screen((28, 29))

    pygame.draw.circle(
        screen,
        BLACK,
        (int(p.x), int(p.y)),
        max(2, int(7 * scale))
    )

    pygame.draw.line(
        screen,
        BLACK,
        to_screen((36, 30)),
        to_screen((52, 20)),
        max(1, int(3 * scale))
    )

    # --------------------------------------------------------
    # TOOL 2 - arrows
    # --------------------------------------------------------

    pygame.draw.line(
        screen,
        BLACK,
        to_screen((33, 72)),
        to_screen((33, 95)),
        max(1, int(3 * scale))
    )

    pygame.draw.polygon(
        screen,
        BLACK,
        [
            to_screen((27, 90)),
            to_screen((33, 99)),
            to_screen((39, 90))
        ]
    )

    # --------------------------------------------------------
    # TOOL 3 - object
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        BLACK,
        scaled_rect(18, 128, 28, 22),
        max(1, int(2 * scale))
    )

    p = to_screen((32, 149))

    pygame.draw.circle(
        screen,
        BLACK,
        (int(p.x), int(p.y)),
        max(2, int(5 * scale))
    )

    # --------------------------------------------------------
    # TOOL 4 - graph
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        BLUE,
        tuple(map(int, to_screen((32, 195)))),
        max(2, int(13 * scale)),
        max(1, int(2 * scale))
    )

    pygame.draw.arc(
        screen,
        RED,
        scaled_rect(18, 181, 28, 28),
        0,
        math.pi,
        max(1, int(2 * scale))
    )

    # --------------------------------------------------------
    # TOOL 5 - vector
    # --------------------------------------------------------

    pygame.draw.line(
        screen,
        BLACK,
        to_screen((15, 246)),
        to_screen((48, 267)),
        max(1, int(3 * scale))
    )

    pygame.draw.polygon(
        screen,
        BLACK,
        [
            to_screen((48, 267)),
            to_screen((41, 257)),
            to_screen((39, 265))
        ]
    )

    # --------------------------------------------------------
    # TOOL 6
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        BLUE,
        tuple(map(int, to_screen((27, 303)))),
        max(2, int(12 * scale))
    )

    pygame.draw.circle(
        screen,
        GREEN,
        tuple(map(int, to_screen((39, 305)))),
        max(2, int(5 * scale))
    )

    # ========================================================
    # TOP CONTROLS
    # ========================================================

    # Alusta
    draw_button(
        scaled_rect(80, 8, 65, 30),
        "Alusta",
        GREEN
    )

    # Stop
    draw_button(
        scaled_rect(155, 8, 55, 30),
        "Stop",
        RED
    )

    # --------------------------------------------------------
    # Toolbar squares
    # --------------------------------------------------------

    for row in range(2):

        for col in range(4):

            rect = scaled_rect(
                230 + col * 22,
                10 + row * 20,
                17,
                17
            )

            pygame.draw.rect(
                screen,
                BLACK,
                rect
            )

            pygame.draw.rect(
                screen,
                WHITE,
                scaled_rect(
                    235 + col * 22,
                    15 + row * 20,
                    7,
                    7
                )
            )

    # ========================================================
    # TARGET
    # ========================================================

    target = pygame.Vector2(
        215,
        185
    )

    target_screen = to_screen(target)

    pygame.draw.circle(
        screen,
        WHITE,
        (int(target_screen.x), int(target_screen.y)),
        int(34 * scale)
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (int(target_screen.x), int(target_screen.y)),
        int(34 * scale),
        max(1, int(5 * scale))
    )

    # ========================================================
    # TRAJECTORY
    # ========================================================

    if len(trajectory) > 1:

        draw_dotted_line(
            trajectory,
            BLACK
        )

    # ========================================================
    # AIM PREVIEW
    # ========================================================

    if aiming:

        direction = (
            mouse_pos - launcher_pos
        )

        if direction.length() > 5:

            direction.normalize_ip()

            preview_velocity = (
                direction * (300 * POWER)
            )

            preview_points = []

            pos = launcher_pos.copy()
            vel = preview_velocity.copy()

            for _ in range(100):

                preview_points.append(
                    pos.copy()
                )

                vel.y += GRAVITY * 0.05

                pos += vel * 0.05

                if pos.y > BASE_HEIGHT - 10:
                    break

            draw_dotted_line(
                preview_points,
                GRAY
            )

            pygame.draw.line(
                screen,
                RED,
                to_screen(launcher_pos),
                to_screen(mouse_pos),
                max(1, int(3 * scale))
            )

    # ========================================================
    # LAUNCHER
    # ========================================================

    launcher_screen = to_screen(
        launcher_pos
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (
            int(launcher_screen.x),
            int(launcher_screen.y)
        ),
        max(2, int(12 * scale))
    )

    # Barrel
    if aiming:

        barrel_dir = (
            mouse_pos - launcher_pos
        )

        if barrel_dir.length() > 0:

            barrel_dir.scale_to_length(35)

            pygame.draw.line(
                screen,
                BLACK,
                launcher_screen,
                to_screen(
                    launcher_pos + barrel_dir
                ),
                max(2, int(8 * scale))
            )

    else:

        pygame.draw.line(
            screen,
            BLACK,
            launcher_screen,
            to_screen(
                launcher_pos +
                pygame.Vector2(30, -20)
            ),
            max(2, int(8 * scale))
        )

    # ========================================================
    # PROJECTILE
    # ========================================================

    if flying and projectile is not None:

        p = to_screen(projectile)

        pygame.draw.circle(
            screen,
            BLACK,
            (int(p.x), int(p.y)),
            max(2, int(7 * scale))
        )

    # ========================================================
    # UPDATE
    # ========================================================

    pygame.display.flip()


pygame.quit()
