import math

import pygame

pygame.init()

BASE_WIDTH = 600
BASE_HEIGHT = 400
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Two-Body Gravity Simulation")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (190, 235, 80)
RED = (235, 100, 100)
BLUE = (50, 150, 255)
GRAY = (100, 100, 100)

GRAVITATIONAL_CONSTANT = 1000.0
SOFTENING_DISTANCE = 12.0
MAX_TRAIL_POINTS = 1800

bodies = [
    {
        "name": "A",
        "pos": pygame.Vector2(210, 245),
        "vel": pygame.Vector2(),
        "mass_text": "100",
        "speed_text": "14",
        "color": BLUE,
        "trail": [],
    },
    {
        "name": "B",
        "pos": pygame.Vector2(460, 245),
        "vel": pygame.Vector2(),
        "mass_text": "100",
        "speed_text": "14",
        "color": RED,
        "trail": [],
    },
]

focused_field = None
dragging_body = None
simulation_running = False
status_message = ""
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
    image = font(11).render(value, True, BLACK)
    screen.blit(
        image,
        (rect.x + round(4 * get_scale()), rect.centery - image.get_height() // 2),
    )


def draw_dotted_line(points, color):
    if len(points) < 2:
        return

    scale = get_scale()
    spacing = 16 * scale
    radius = max(1, round(2 * scale))
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


def body_radius(body):
    try:
        mass = float(body["mass_text"])
    except ValueError:
        mass = 100.0
    return max(8, min(22, round(10 + math.log10(max(mass, 0.01)) * 2)))


def move_with_collisions(step):
    first, second = bodies
    inverse_first = 0.0 if dragging_body == 0 else 1 / float(first["mass_text"])
    inverse_second = 0.0 if dragging_body == 1 else 1 / float(second["mass_text"])
    inverse_total = inverse_first + inverse_second
    radius = body_radius(first) + body_radius(second)
    separation = second["pos"] - first["pos"]
    distance = separation.length()

    # Separate overlapping planets, keeping a dragged planet under the cursor.
    if distance < radius:
        normal = separation / distance if distance else pygame.Vector2(1, 0)
        correction = normal * (radius - distance) / inverse_total
        first["pos"] -= correction * inverse_first
        second["pos"] += correction * inverse_second

    velocity_first = first["vel"] if inverse_first else pygame.Vector2()
    velocity_second = second["vel"] if inverse_second else pygame.Vector2()
    relative_velocity = velocity_second - velocity_first
    separation = second["pos"] - first["pos"]
    speed_squared = relative_velocity.length_squared()
    approach = separation.dot(relative_velocity)
    gap = separation.length_squared() - radius**2
    contact_time = None

    # Sweep the circles through the step so fast planets cannot pass through.
    if approach < 0 and speed_squared > 0:
        discriminant = approach**2 - speed_squared * gap
        if gap <= 1e-8:
            contact_time = 0.0
        elif discriminant >= 0:
            candidate = gap / (-approach + math.sqrt(discriminant))
            if 0 <= candidate <= step:
                contact_time = candidate

    travel_time = step if contact_time is None else contact_time
    first["pos"] += velocity_first * travel_time
    second["pos"] += velocity_second * travel_time
    if contact_time is None:
        return

    normal = (second["pos"] - first["pos"]).normalize()
    closing_speed = relative_velocity.dot(normal)
    impulse = -2 * closing_speed / inverse_total
    first["vel"] -= normal * impulse * inverse_first
    second["vel"] += normal * impulse * inverse_second
    remaining = step - contact_time
    if inverse_first:
        first["pos"] += first["vel"] * remaining
    if inverse_second:
        second["pos"] += second["vel"] * remaining


def start_simulation():
    global simulation_running, status_message

    try:
        for body in bodies:
            mass = float(body["mass_text"])
            speed = float(body["speed_text"])
            if not math.isfinite(mass) or not 0 < mass <= 1_000_000:
                raise ValueError("Mass must be greater than 0 and at most 1,000,000.")
            if not math.isfinite(speed) or not 0 <= speed <= 500:
                raise ValueError("Speed must be between 0 and 500.")
    except ValueError as error:
        message = str(error)
        if not message.startswith(("Mass must", "Speed must")):
            message = "Enter valid numbers for both bodies."
        status_message = message
        return

    separation = bodies[1]["pos"] - bodies[0]["pos"]
    if separation.length_squared() < 1:
        status_message = "Move the bodies apart before starting."
        return

    tangent = pygame.Vector2(-separation.y, separation.x).normalize()
    bodies[0]["vel"] = -tangent * float(bodies[0]["speed_text"])
    bodies[1]["vel"] = tangent * float(bodies[1]["speed_text"])
    for body in bodies:
        body["trail"] = [body["pos"].copy()]

    simulation_running = True
    status_message = ""


def stop_simulation():
    global simulation_running, status_message
    simulation_running = False
    status_message = "Simulation paused."


def reset_simulation():
    global simulation_running, dragging_body, focused_field, status_message

    defaults = (
        (210, 245, "100", "14"),
        (460, 245, "100", "14"),
    )
    for body, (x, y, mass, speed) in zip(bodies, defaults):
        body["pos"] = pygame.Vector2(x, y)
        body["vel"] = pygame.Vector2()
        body["mass_text"] = mass
        body["speed_text"] = speed
        body["trail"] = []

    simulation_running = False
    dragging_body = None
    focused_field = None
    status_message = "Simulation reset."


def field_at(position, fields):
    for name, rect in fields.items():
        if rect.collidepoint(position):
            return name
    return None


while running:
    dt = min(clock.tick(60) / 1000.0, 1 / 30)

    start_rect = scaled_rect(80, 7, 52, 27)
    stop_rect = scaled_rect(138, 7, 48, 27)
    reset_rect = scaled_rect(190, 7, 54, 27)
    fields = {
        "mass_a": scaled_rect(126, 38, 57, 24),
        "speed_a": scaled_rect(222, 38, 52, 24),
        "mass_b": scaled_rect(363, 38, 57, 24),
        "speed_b": scaled_rect(459, 38, 52, 24),
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            focused_field = field_at(event.pos, fields)
            if focused_field is not None:
                if simulation_running:
                    simulation_running = False
                    status_message = "Paused while editing settings."
                continue

            if start_rect.collidepoint(event.pos):
                start_simulation()
                continue
            if stop_rect.collidepoint(event.pos):
                stop_simulation()
                continue
            if reset_rect.collidepoint(event.pos):
                reset_simulation()
                continue

            mouse_pos = from_screen(event.pos)
            for body_index in range(len(bodies) - 1, -1, -1):
                body = bodies[body_index]
                if mouse_pos.distance_to(body["pos"]) <= body_radius(body) + 5:
                    dragging_body = body_index
                    body["vel"] = pygame.Vector2()
                    body["trail"] = []
                    break

        elif event.type == pygame.MOUSEMOTION and dragging_body is not None:
            body = bodies[dragging_body]
            body["pos"] = from_screen(event.pos)
            body["pos"].x = max(12, min(BASE_WIDTH - 12, body["pos"].x))
            body["pos"].y = max(82, min(BASE_HEIGHT - 12, body["pos"].y))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging_body = None

        elif event.type == pygame.KEYDOWN and focused_field is not None:
            body_index = 0 if focused_field.endswith("_a") else 1
            value_type = "mass_text" if focused_field.startswith("mass") else "speed_text"
            value = bodies[body_index][value_type]
            if event.key == pygame.K_BACKSPACE:
                value = value[:-1]
            elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                value = ""
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                focused_field = None
            elif event.key == pygame.K_DELETE:
                value = ""
            elif event.unicode and event.unicode in "0123456789.":
                if event.unicode != "." or "." not in value:
                    value += event.unicode
            bodies[body_index][value_type] = value

    if simulation_running:
        substeps = 2
        step = dt / substeps
        for _ in range(substeps):
            first, second = bodies
            separation = second["pos"] - first["pos"]
            distance_squared = max(
                separation.length_squared(),
                SOFTENING_DISTANCE**2,
            )
            direction = separation.normalize() if separation.length_squared() else pygame.Vector2()
            acceleration_first = (
                direction
                * GRAVITATIONAL_CONSTANT
                * float(second["mass_text"])
                / distance_squared
            )
            acceleration_second = (
                -direction
                * GRAVITATIONAL_CONSTANT
                * float(first["mass_text"])
                / distance_squared
            )

            if dragging_body != 0:
                first["vel"] += acceleration_first * step
            if dragging_body != 1:
                second["vel"] += acceleration_second * step
            move_with_collisions(step)

        for body in bodies:
            if dragging_body is None:
                body["trail"].append(body["pos"].copy())
                if len(body["trail"]) > MAX_TRAIL_POINTS:
                    del body["trail"][:-MAX_TRAIL_POINTS]

    screen.fill(WHITE)
    scale = get_scale()

    # Start/stop in the top row; mass and speed fields are grouped by body below.
    draw_button(start_rect, "Start", GREEN)
    draw_button(stop_rect, "Stop", RED)
    draw_button(reset_rect, "Reset", WHITE)
    draw_text("Two-body gravity", (252, 14), 14, bold=True)
    draw_text("A mass", (80, 44), 10, bold=True)
    draw_input(fields["mass_a"], bodies[0]["mass_text"], focused_field == "mass_a")
    draw_text("Speed", (185, 44), 10, bold=True)
    draw_input(fields["speed_a"], bodies[0]["speed_text"], focused_field == "speed_a")
    draw_text("B mass", (291, 44), 10, bold=True)
    draw_input(fields["mass_b"], bodies[1]["mass_text"], focused_field == "mass_b")
    draw_text("Speed", (422, 44), 10, bold=True)
    draw_input(fields["speed_b"], bodies[1]["speed_text"], focused_field == "speed_b")
    draw_text("units", (518, 44), 9, color=GRAY)

    previous_clip = screen.get_clip()
    screen.set_clip(scaled_rect(3, 71, 597, 329))

    for body in bodies:
        if len(body["trail"]) > 1:
            draw_dotted_line(body["trail"], body["color"])

    for body in bodies:
        center = to_screen(body["pos"])
        radius = max(2, round(body_radius(body) * scale))
        pygame.draw.circle(screen, body["color"], tuple(map(round, center)), radius)
        pygame.draw.circle(
            screen,
            BLACK,
            tuple(map(round, center)),
            radius,
            max(1, round(2 * scale)),
        )
        label_pos = body["pos"] + pygame.Vector2(-4, -radius / scale - 17)
        draw_text(body["name"], label_pos, 12, bold=True)

    screen.set_clip(previous_clip)

    if status_message:
        draw_text(status_message, (11, 74), 10, RED)

    pygame.display.flip()

pygame.quit()
