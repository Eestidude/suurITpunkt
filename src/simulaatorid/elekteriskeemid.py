import pygame
import math
import copy


# =========================================================
# AKEN
# =========================================================

WIDTH = 1200
HEIGHT = 760

SIDEBAR_WIDTH = 310
CANVAS_WIDTH = WIDTH - SIDEBAR_WIDTH

# =========================================================
# VÄRVID
# =========================================================

WHITE = (255, 255, 255)
BLACK = (26, 39, 48)

GRAY = (238, 243, 245)
LIGHT_GRAY = (248, 250, 251)

GREEN = (20, 166, 112)
LIGHT_GREEN = (220, 246, 235)

RED = (205, 75, 72)
LIGHT_RED = (255, 232, 229)

YELLOW = (255, 220, 0)
LIGHT_YELLOW = (255, 245, 80)

BLUE = (50, 126, 171)
DARK_PANEL = (26, 40, 49)
PANEL_TEXT = (224, 235, 238)
PANEL_MUTED = (150, 171, 179)
GRID_COLOR = (229, 236, 239)


# =========================================================
# FONDID
# =========================================================

# =========================================================
# SEADISTUSED
# =========================================================

TOOLBAR_HEIGHT = 72

COMPONENT_WIDTH = 60
COMPONENT_HEIGHT = 40

WIRE_LENGTH = 90

SNAP_DISTANCE = 25
TERMINAL_HIT_RADIUS = 14

CONNECTION_TOLERANCE = 4.0
SOURCE_INTERNAL_RESISTANCE = 0.5
BULB_MIN_POWER = 0.025
BULB_BURNOUT_FACTOR = 1.5


# =========================================================
# ABIFUNKTSIOONID
# =========================================================

def distance(a, b):

    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )


def rotate_point(x, y, cx, cy, angle):

    rad = math.radians(angle)

    dx = x - cx
    dy = y - cy

    new_x = (
        dx * math.cos(rad)
        -
        dy * math.sin(rad)
    )

    new_y = (
        dx * math.sin(rad)
        +
        dy * math.cos(rad)
    )

    return (
        cx + new_x,
        cy + new_y
    )


def point_segment_distance(
    px,
    py,
    x1,
    y1,
    x2,
    y2
):

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:

        return math.hypot(
            px - x1,
            py - y1
        )

    t = (
        (px - x1) * dx
        +
        (py - y1) * dy
    ) / (
        dx * dx
        +
        dy * dy
    )

    t = max(
        0,
        min(1, t)
    )

    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy

    return math.hypot(
        px - nearest_x,
        py - nearest_y
    )


# =========================================================
# DETAIL
# =========================================================

class Component:

    def __init__(
        self,
        kind,
        x,
        y
    ):

        self.kind = kind

        self.x = x
        self.y = y

        self.angle = 0
        self.resistance = 100.0
        self.voltage = 9.0
        self.rated_power = 5.0
        self.burned_out = False

        if kind == 'bulb':
            self.resistance = 20.0


        # -------------------------------------------------
        # JUHE
        # -------------------------------------------------

        if kind == 'wire':

            self.start_x = x - WIRE_LENGTH / 2
            self.start_y = y

            self.end_x = x + WIRE_LENGTH / 2
            self.end_y = y


    # =====================================================
    # JUHTME KESKPUNKT
    # =====================================================

    def update_midpoint(self):

        if self.kind != 'wire':
            return

        self.x = (
            self.start_x +
            self.end_x
        ) / 2

        self.y = (
            self.start_y +
            self.end_y
        ) / 2


    # =====================================================
    # DETAILI KONTAKTID
    # =====================================================

    def terminals(self):

        # JUHE

        if self.kind == 'wire':

            return [
                (
                    self.start_x,
                    self.start_y
                ),
                (
                    self.end_x,
                    self.end_y
                )
            ]


        # MUU DETAIL

        terminal_offset = COMPONENT_WIDTH / 2 + 8

        rad = math.radians(
            self.angle
        )

        dx = math.cos(rad) * terminal_offset
        dy = math.sin(rad) * terminal_offset

        return [
            (
                self.x - dx,
                self.y - dy
            ),
            (
                self.x + dx,
                self.y + dy
            )
        ]


    # =====================================================
    # RECT
    # =====================================================

    def rect(self):

        if self.kind == 'wire':

            min_x = min(
                self.start_x,
                self.end_x
            )

            max_x = max(
                self.start_x,
                self.end_x
            )

            min_y = min(
                self.start_y,
                self.end_y
            )

            max_y = max(
                self.start_y,
                self.end_y
            )

            return pygame.Rect(
                min_x - 10,
                min_y - 10,
                max_x - min_x + 20,
                max_y - min_y + 20
            )

        return pygame.Rect(
            self.x - 35,
            self.y - 35,
            70,
            70
        )


    # =====================================================
    # KAS HIIR ON DETAILIL
    # =====================================================

    def contains(self, pos):

        mx, my = pos


        # JUHE

        if self.kind == 'wire':

            return (
                point_segment_distance(
                    mx,
                    my,
                    self.start_x,
                    self.start_y,
                    self.end_x,
                    self.end_y
                )
                <= 10
            )


        # LAMP

        if self.kind == 'bulb':

            return (
                math.hypot(
                    mx - self.x,
                    my - self.y
                )
                <= 24
            )


        # MUU DETAIL

        return self.rect().collidepoint(
            pos
        )


    # =====================================================
    # JOONISTAMINE
    # =====================================================

    def draw(
        self,
        surface,
        selected=False,
        bulb_lit=False,
        bulb_burned_out=False
    ):

        terminals = self.terminals()


        # =================================================
        # JUHE
        # =================================================

        if self.kind == 'wire':

            pygame.draw.line(
                surface,
                BLACK,
                terminals[0],
                terminals[1],
                5
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (
                    int(terminals[0][0]),
                    int(terminals[0][1])
                ),
                3
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (
                    int(terminals[1][0]),
                    int(terminals[1][1])
                ),
                3
            )


            if selected:

                pygame.draw.circle(
                    surface,
                    GREEN,
                    (
                        int(terminals[0][0]),
                        int(terminals[0][1])
                    ),
                    9,
                    2
                )

                pygame.draw.circle(
                    surface,
                    GREEN,
                    (
                        int(terminals[1][0]),
                        int(terminals[1][1])
                    ),
                    9,
                    2
                )

            return


        # =================================================
        # DETAILI JUHTMED
        # =================================================

        body_left = rotate_point(
            self.x - COMPONENT_WIDTH / 2,
            self.y,
            self.x,
            self.y,
            self.angle
        )

        body_right = rotate_point(
            self.x + COMPONENT_WIDTH / 2,
            self.y,
            self.x,
            self.y,
            self.angle
        )


        pygame.draw.line(
            surface,
            BLACK,
            terminals[0],
            body_left,
            3
        )

        pygame.draw.line(
            surface,
            BLACK,
            body_right,
            terminals[1],
            3
        )


        # =================================================
        # TAKISTI
        # =================================================

        if self.kind == 'resistor':

            points = []

            for px, py in [
                (-30, -18),
                (30, -18),
                (30, 18),
                (-30, 18)
            ]:

                points.append(
                    rotate_point(
                        self.x + px,
                        self.y + py,
                        self.x,
                        self.y,
                        self.angle
                    )
                )


            pygame.draw.polygon(
                surface,
                WHITE,
                points
            )

            pygame.draw.polygon(
                surface,
                BLACK,
                points,
                2
            )


            text = font.render(
                "R",
                True,
                BLACK
            )

            text = pygame.transform.rotate(
                text,
                -self.angle
            )


            surface.blit(
                text,
                (
                    self.x -
                    text.get_width() / 2,

                    self.y -
                    text.get_height() / 2
                )
            )

            value_text = small_font.render(
                f"{self.resistance:g} Ω",
                True,
                BLACK
            )

            surface.blit(
                value_text,
                (
                    self.x - value_text.get_width() / 2,
                    self.y + 23
                )
            )


        # =================================================
        # LAMP
        # =================================================

        elif self.kind == 'bulb':

            if bulb_burned_out:

                color = (188, 193, 194)

            elif bulb_lit:

                color = LIGHT_YELLOW

            else:

                color = WHITE


            pygame.draw.circle(
                surface,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                18
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (
                    int(self.x),
                    int(self.y)
                ),
                18,
                2
            )


            if bulb_burned_out:

                pygame.draw.line(
                    surface,
                    RED,
                    (self.x - 10, self.y - 10),
                    (self.x + 10, self.y + 10),
                    3
                )

                pygame.draw.line(
                    surface,
                    RED,
                    (self.x + 10, self.y - 10),
                    (self.x - 10, self.y + 10),
                    3
                )


            rad = math.radians(
                self.angle
            )

            dx = math.cos(rad) * 11
            dy = math.sin(rad) * 11

            px = -math.sin(rad) * 11
            py = math.cos(rad) * 11


            pygame.draw.line(
                surface,
                BLACK,
                (
                    self.x - dx,
                    self.y - dy
                ),
                (
                    self.x + dx,
                    self.y + dy
                ),
                2
            )

            value_text = small_font.render(
                f"{self.resistance:g} Ω",
                True,
                BLACK
            )

            surface.blit(
                value_text,
                (
                    self.x - value_text.get_width() / 2,
                    self.y + 23
                )
            )

            pygame.draw.line(
                surface,
                BLACK,
                (
                    self.x - px,
                    self.y - py
                ),
                (
                    self.x + px,
                    self.y + py
                ),
                2
            )


        # =================================================
        # VOOLUALLIKAS
        # =================================================

        elif self.kind == 'battery':

            points = []

            for px, py in [
                (-30, -20),
                (30, -20),
                (30, 20),
                (-30, 20)
            ]:

                points.append(
                    rotate_point(
                        self.x + px,
                        self.y + py,
                        self.x,
                        self.y,
                        self.angle
                    )
                )


            pygame.draw.polygon(
                surface,
                WHITE,
                points
            )

            pygame.draw.polygon(
                surface,
                BLACK,
                points,
                2
            )


            # MIINUS

            p1 = rotate_point(
                self.x - 18,
                self.y,
                self.x,
                self.y,
                self.angle
            )

            p2 = rotate_point(
                self.x - 7,
                self.y,
                self.x,
                self.y,
                self.angle
            )


            pygame.draw.line(
                surface,
                BLACK,
                p1,
                p2,
                3
            )

            value_text = small_font.render(
                f"{self.voltage:g} V",
                True,
                BLACK
            )

            surface.blit(
                value_text,
                (
                    self.x - value_text.get_width() / 2,
                    self.y + 22
                )
            )


            # PLUSS

            p1 = rotate_point(
                self.x + 7,
                self.y,
                self.x,
                self.y,
                self.angle
            )

            p2 = rotate_point(
                self.x + 18,
                self.y,
                self.x,
                self.y,
                self.angle
            )


            pygame.draw.line(
                surface,
                BLACK,
                p1,
                p2,
                3
            )


            p1 = rotate_point(
                self.x + 12,
                self.y - 5,
                self.x,
                self.y,
                self.angle
            )

            p2 = rotate_point(
                self.x + 12,
                self.y + 5,
                self.x,
                self.y,
                self.angle
            )


            pygame.draw.line(
                surface,
                BLACK,
                p1,
                p2,
                3
            )


        # =================================================
        # VALIK
        # =================================================

        if selected:

            if self.kind == 'bulb':

                pygame.draw.circle(
                    surface,
                    GREEN,
                    (
                        int(self.x),
                        int(self.y)
                    ),
                    26,
                    2
                )

            else:

                pygame.draw.rect(
                    surface,
                    GREEN,
                    self.rect().inflate(
                        8,
                        8
                    ),
                    2
                )


# =========================================================
# DETAILI OTSIMINE
# =========================================================

def find_component(pos):

    for component in reversed(components):

        if component.contains(pos):

            return component

    return None


# =========================================================
# LÄHIMA KONTAKTI OTSIMINE
# =========================================================

def closest_point_on_segment(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return start
    fraction = max(0.0, min(1.0, ((point[0] - start[0]) * dx
                                  + (point[1] - start[1]) * dy) / length_squared))
    return start[0] + fraction * dx, start[1] + fraction * dy


def find_nearest_terminal(point, excluded=None):
    best = None
    best_distance = SNAP_DISTANCE
    for component in components:
        if component is excluded:
            continue
        targets = list(component.terminals())
        if component.kind == 'wire':
            targets.append(closest_point_on_segment(point, *component.terminals()))
        for target in targets:
            candidate_distance = distance(point, target)
            if candidate_distance < best_distance:
                best_distance = candidate_distance
                best = target
    return best


# =========================================================
# DETAILI ÜHENDAMINE
# =========================================================

def snap_component(component):

    if component not in components:
        return


    best_offset = None
    smallest_distance = SNAP_DISTANCE


    for terminal in component.terminals():

        target = find_nearest_terminal(
            terminal,
            component
        )


        if target is None:
            continue


        d = distance(
            terminal,
            target
        )


        if d < smallest_distance:

            smallest_distance = d

            best_offset = (
                target[0] - terminal[0],
                target[1] - terminal[1]
            )


    if best_offset is None:
        return


    dx, dy = best_offset


    # JUHE

    if component.kind == 'wire':

        component.start_x += dx
        component.start_y += dy

        component.end_x += dx
        component.end_y += dy

        component.update_midpoint()


    # MUU DETAIL

    else:

        component.x += dx
        component.y += dy


# =========================================================
# JUHTME ÜHE OTSA ÜHENDAMINE
# =========================================================

def snap_wire_endpoint(
    component,
    endpoint
):

    if component.kind != 'wire':
        return


    if endpoint == 'start':

        point = (
            component.start_x,
            component.start_y
        )

    else:

        point = (
            component.end_x,
            component.end_y
        )


    target = find_nearest_terminal(
        point,
        component
    )


    if target is None:
        return


    if distance(
        point,
        target
    ) > SNAP_DISTANCE:

        return


    if endpoint == 'start':

        component.start_x = target[0]
        component.start_y = target[1]

    else:

        component.end_x = target[0]
        component.end_y = target[1]


    component.update_midpoint()


# =========================================================
# AHELA ARVUTAMINE
# =========================================================

def solve_linear_system(matrix, results):

    size = len(results)

    for column in range(size):

        pivot = max(
            range(column, size),
            key=lambda row: abs(matrix[row][column])
        )

        if abs(matrix[pivot][column]) < 1e-12:
            return None

        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        results[column], results[pivot] = results[pivot], results[column]

        divisor = matrix[column][column]

        for entry in range(column, size):
            matrix[column][entry] /= divisor

        results[column] /= divisor

        for row in range(column + 1, size):

            multiplier = matrix[row][column]

            if multiplier == 0:
                continue

            for entry in range(column, size):
                matrix[row][entry] -= multiplier * matrix[column][entry]

            results[row] -= multiplier * results[column]

    solution = [0.0] * size

    for row in range(size - 1, -1, -1):

        solution[row] = results[row] - sum(
            matrix[row][column] * solution[column]
            for column in range(row + 1, size)
        )

    return solution


def build_circuit_nodes():
    """Merge touching terminals and wire junctions into electrical nodes.

    An endpoint on a wire creates a junction. Two wire interiors crossing
    without an endpoint remain independent, as in a circuit diagram.
    """
    terminal_points = [point for component in components
                       for point in component.terminals()]
    parent = list(range(len(terminal_points)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first, second):
        parent[find(second)] = find(first)

    for first, point in enumerate(terminal_points):
        for second in range(first + 1, len(terminal_points)):
            if distance(point, terminal_points[second]) <= CONNECTION_TOLERANCE:
                union(first, second)

    for index, component in enumerate(components):
        if component.kind != 'wire':
            continue
        start, end = component.terminals()
        union(index * 2, index * 2 + 1)
        for terminal_index, point in enumerate(terminal_points):
            if distance(point, closest_point_on_segment(point, start, end)) <= CONNECTION_TOLERANCE:
                union(index * 2, terminal_index)

    return {component: (find(index * 2), find(index * 2 + 1))
            for index, component in enumerate(components)}


def solve_circuit():
    """Solve every connected island, including all battery polarities.

    Each battery is an ideal voltage source with SOURCE_INTERNAL_RESISTANCE
    in series. Its Norton equivalent stamps a conductance and a signed
    current injection, so series and parallel sources use the same solver.
    """
    nodes = build_circuit_nodes()
    branches = []
    sources = []
    for component, (negative, positive) in nodes.items():
        if component.kind == 'battery':
            sources.append(component)
            branches.append((negative, positive, SOURCE_INTERNAL_RESISTANCE,
                             component.voltage, component))
        elif component.kind in ('resistor', 'bulb') and not component.burned_out:
            if component.resistance > 0:
                branches.append((negative, positive, component.resistance,
                                 0.0, component))

    connections = {}
    for first, second, _, _, component in branches:
        connections.setdefault(first, []).append((second, component))
        connections.setdefault(second, []).append((first, component))

    # Each disconnected island needs its own arbitrary zero-voltage reference.
    grounds = set()
    visited = set()
    for node in connections:
        if node in visited:
            continue
        grounds.add(node)
        queue = [node]
        visited.add(node)
        while queue:
            for neighbor, _ in connections[queue.pop()]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    unknowns = sorted(visited - grounds)
    indices = {node: index for index, node in enumerate(unknowns)}
    matrix = [[0.0] * len(unknowns) for _ in unknowns]
    results = [0.0] * len(unknowns)
    for first, second, resistance, voltage, _ in branches:
        if first == second:
            continue
        conductance = 1.0 / resistance
        first_index = indices.get(first)
        second_index = indices.get(second)
        if first_index is not None:
            matrix[first_index][first_index] += conductance
            results[first_index] -= voltage * conductance
        if second_index is not None:
            matrix[second_index][second_index] += conductance
            results[second_index] += voltage * conductance
        if first_index is not None and second_index is not None:
            matrix[first_index][second_index] -= conductance
            matrix[second_index][first_index] -= conductance

    voltages = solve_linear_system(matrix, results)
    result = {
        'closed': False,
        'short_circuit': any(nodes[source][0] == nodes[source][1] for source in sources),
        'voltage': 0.0,
        'resistance': math.inf,
        'current': 0.0,
        'bulb_powers': {},
        'component_voltages': {},
        'component_currents': {},
        'source_currents': {},
        'circuit_measurements': ('Kogu ahel', math.nan, math.nan, math.nan, math.nan),
        'junctions': junction_points(),
        'solver_error': voltages is None,
    }
    if voltages is None:
        return result

    node_voltages = {node: 0.0 for node in grounds}
    node_voltages.update((node, voltages[index]) for node, index in indices.items())
    for component, (first, second) in nodes.items():
        voltage = node_voltages.get(second, 0.0) - node_voltages.get(first, 0.0)
        result['component_voltages'][component] = voltage
        result['component_currents'][component] = 0.0
        if component.kind == 'bulb':
            result['bulb_powers'][component] = 0.0

    for first, second, resistance, voltage, component in branches:
        terminal_voltage = result['component_voltages'][component]
        if component.kind == 'battery':
            # Positive means supplying power; negative means absorbing current.
            current = (voltage - terminal_voltage) / resistance
            result['source_currents'][component] = current
        else:
            current = -terminal_voltage / resistance
        result['component_currents'][component] = current
        if component.kind == 'bulb':
            result['bulb_powers'][component] = current * current * resistance

    # A closed loop can carry zero current when opposing sources cancel.
    for source in sources:
        negative, positive = nodes[source]
        visited = {negative}
        queue = [negative]
        while queue:
            for neighbor, component in connections.get(queue.pop(), ()):
                if component is not source and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        if positive in visited:
            result['closed'] = True

    if sources:
        reference_source = max(sources, key=lambda source: abs(result['source_currents'][source]))
        result['voltage'] = result['component_voltages'][reference_source]
        result['current'] = result['source_currents'][reference_source]
        # Multiple active sources do not define a single load resistance V/I.
        if len(sources) == 1 and abs(result['current']) > 1e-12:
            result['resistance'] = abs(result['voltage'] / result['current'])
        elif len(sources) > 1:
            result['resistance'] = math.nan
    result['circuit_measurements'] = whole_circuit_measurements(result, nodes, node_voltages)
    return result


def whole_circuit_measurements(result, nodes, node_voltages):
    """Measure the load across the battery bank, excluding internal losses.

    Separate supplies or a bank with intermediate load taps have no single
    supply voltage/current. Keep total load power, but mark those values N/A.
    """
    sources = list(result['source_currents'])
    loads = [component for component in components
             if component.kind in ('bulb', 'resistor')]
    power = sum(abs(result['component_voltages'][component]
                    * result['component_currents'][component]) for component in loads)
    if not sources:
        return 'Kogu ahel', 0.0, 0.0, math.inf, power

    source_connections = {}
    for source in sources:
        first, second = nodes[source]
        source_connections.setdefault(first, set()).add(second)
        source_connections.setdefault(second, set()).add(first)
    visited = set()
    queue = [next(iter(source_connections))]
    while queue:
        node = queue.pop()
        if node not in visited:
            visited.add(node)
            queue.extend(source_connections[node] - visited)
    if len(visited) != len(source_connections):
        return 'Kogu ahel', math.nan, math.nan, math.nan, power

    if len(visited) == 1:
        current = sum(abs(result['source_currents'][source]) for source in sources)
        return 'Kogu ahel', 0.0, current, 0.0, power

    load_nodes = {node for component in loads for node in nodes[component]}
    terminals = visited & load_nodes
    if len(terminals) < 2:
        # An open load may touch only one bank terminal, or none at all.
        terminals |= {node for node, neighbors in source_connections.items()
                      if len(neighbors) == 1}
    if len(terminals) != 2:
        return 'Kogu ahel', math.nan, math.nan, math.nan, power

    first, second = sorted(terminals)
    voltage = abs(node_voltages[second] - node_voltages[first])
    # Net current at the bank boundary sums parallel sources, while counting
    # a series string only once. Charging currents retain their sign.
    current = abs(sum(result['source_currents'][source]
                      * ((nodes[source][1] == first) - (nodes[source][0] == first))
                      for source in sources))
    if current < 1e-12:
        current = 0.0
    resistance = voltage / current if current else math.inf
    return 'Kogu ahel', voltage, current, resistance, power


def junction_points():
    """Return branch junctions for the canvas, using the solver's tolerance."""
    points = []
    for component in components:
        for point in component.terminals():
            incident_count = 0
            for other in components:
                start, end = other.terminals()
                if other.kind == 'wire':
                    if distance(point, closest_point_on_segment(point, start, end)) <= CONNECTION_TOLERANCE:
                        incident_count += (1 if min(distance(point, start), distance(point, end))
                                           <= CONNECTION_TOLERANCE else 2)
                else:
                    incident_count += sum(distance(point, terminal) <= CONNECTION_TOLERANCE
                                          for terminal in (start, end))
            if incident_count >= 3 and not any(distance(point, old) <= CONNECTION_TOLERANCE for old in points):
                points.append(point)
    return points


def simulate_circuit():
    bulbs = [component for component in components if component.kind == 'bulb']
    while True:
        result = solve_circuit()
        overloaded_bulbs = [bulb for bulb in bulbs if (
            not bulb.burned_out
            and result['bulb_powers'].get(bulb, 0.0) > bulb.rated_power * BULB_BURNOUT_FACTOR
        )]
        if not overloaded_bulbs:
            break
        for bulb in overloaded_bulbs:
            bulb.burned_out = True

    result['bulb_power'] = max(result['bulb_powers'].values(), default=0.0)
    result['bulbs_burned_out'] = any(bulb.burned_out for bulb in bulbs)
    result['bulbs_lit'] = {bulb: not bulb.burned_out
                         and result['bulb_powers'].get(bulb, 0.0) >= BULB_MIN_POWER
                         for bulb in bulbs}
    result['bulb_lit'] = any(result['bulbs_lit'].values())
    return result


def measurement_values(result):
    """Measure the selected component, or the whole circuit by default."""
    measured = selected_component
    if measured is None or measured.kind == 'wire':
        return result['circuit_measurements']
    voltage = abs(result['component_voltages'].get(measured, 0.0))
    current = result['component_currents'].get(measured, 0.0)
    if measured.kind == 'battery':
        return 'Allikas: sisetakistus', voltage, current, SOURCE_INTERNAL_RESISTANCE, voltage * current
    resistance = math.inf if measured.burned_out else measured.resistance
    name = 'Lamp' if measured.kind == 'bulb' else 'Takisti'
    return name, voltage, abs(current), resistance, voltage * abs(current)


def format_measurement(value, unit):
    if math.isnan(value):
        return f'— {unit}'
    if math.isinf(value):
        return f'∞ {unit}'
    return f'{value:.3g} {unit}'


# =========================================================
# AJALUGU
# =========================================================

history = []


def save_history():

    history.append(
        copy.deepcopy(
            components
        )
    )


    if len(history) > 50:

        history.pop(0)


def undo():

    global components
    global selected_component

    if not history:
        return


    components = history.pop()

    selected_component = None


# =========================================================
# NUPUD
# =========================================================

buttons = [

    (
        'resistor',
        pygame.Rect(
            14,
            14,
            108,
            44
        ),
        "Takisti"
    ),

    (
        'bulb',
        pygame.Rect(
            130,
            14,
            96,
            44
        ),
        "Lamp"
    ),

    (
        'battery',
        pygame.Rect(
            234,
            14,
            146,
            44
        ),
        "Vooluallikas"
    ),

    (
        'wire',
        pygame.Rect(
            388,
            14,
            92,
            44
        ),
        "Juhe"
    )
]


delete_button = pygame.Rect(
    488,
    14,
    98,
    44
)

undo_button = pygame.Rect(
    594,
    14,
    94,
    44
)

property_field = pygame.Rect(
    CANVAS_WIDTH + 22,
    468,
    SIDEBAR_WIDTH - 44,
    46
)


# =========================================================
# MUUTUJAD
# =========================================================

components = []

selected_kind = None

selected_component = None

# Detail, mis on hetkel hiirega kaasas.

held_component = None

# Juba laual oleva detaili liigutamine.

dragged_component = None

drag_mode = None

offset_x = 0
offset_y = 0

edited_field = None
field_text = ""
input_error = False
replace_field = False
simulation_dirty = True
simulation_result = None


# =========================================================
# PEAMINE TSÜKKEL
# =========================================================

running = True


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Elektriskeemi koostaja")
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 22)
    small_font = pygame.font.SysFont("segoeui", 16)
    title_font = pygame.font.SysFont("segoeui", 25, bold=True)
    number_font = pygame.font.SysFont("segoeui", 29, bold=True)

    while running:

        # =====================================================
        # SÜNDMUSED
        # =====================================================

        for event in pygame.event.get():

            if event.type in (
                pygame.KEYDOWN,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION
            ):

                simulation_dirty = True

            # =================================================
            # SULGEMINE
            # =================================================

            if event.type == pygame.QUIT:

                running = False


            # =================================================
            # KLAVIATUUR
            # =================================================

            elif event.type == pygame.KEYDOWN:

                if edited_field is not None:

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):

                        try:

                            new_value = float(
                                field_text.replace(",", ".")
                            )

                        except ValueError:

                            new_value = 0


                        if (
                            math.isfinite(new_value)
                            and new_value > 0
                            and selected_component is not None
                        ):

                            save_history()

                            if edited_field == 'resistance':

                                selected_component.resistance = new_value

                            else:

                                selected_component.voltage = new_value


                            edited_field = None
                            input_error = False

                        else:

                            input_error = True
                            replace_field = True


                    elif event.key == pygame.K_BACKSPACE:

                        if replace_field:

                            field_text = ""

                        else:

                            field_text = field_text[:-1]

                        replace_field = False
                        input_error = False


                    elif event.key == pygame.K_ESCAPE:

                        edited_field = None
                        input_error = False


                    elif event.unicode in "0123456789.," and len(field_text) < 14:

                        if replace_field:

                            field_text = event.unicode

                        else:

                            field_text += event.unicode

                        replace_field = False
                        input_error = False


                elif (
                    event.key == pygame.K_z
                    and
                    event.mod & pygame.KMOD_CTRL
                ):

                    undo()


            # =================================================
            # HIIRE NUPP ALLA
            # =================================================

            elif event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = pygame.mouse.get_pos()


                # =================================================
                # VASAK HIIRE NUPP
                # =================================================

                if event.button == 1:

                    button_clicked = False
                    edited_field = None


                    if mx >= CANVAS_WIDTH:

                        button_clicked = True

                        if (
                            property_field.collidepoint(mx, my)
                            and selected_component is not None
                            and selected_component.kind in ('resistor', 'bulb', 'battery')
                        ):

                            if selected_component.kind in ('resistor', 'bulb'):

                                edited_field = 'resistance'
                                field_text = f"{selected_component.resistance:g}"

                            else:

                                edited_field = 'voltage'
                                field_text = f"{selected_component.voltage:g}"

                            replace_field = True
                            input_error = False


                    # =================================================
                    # DETAILI NUPUD
                    # =================================================

                    for kind, rect, name in buttons:

                        if rect.collidepoint(
                            mx,
                            my
                        ):

                            button_clicked = True


                            # Sama nupp = tühista valik.

                            if selected_kind == kind:

                                selected_kind = None
                                held_component = None

                            else:

                                selected_kind = kind

                                held_component = Component(
                                    kind,
                                    mx,
                                    my
                                )


                            selected_component = None

                            break


                    # =================================================
                    # KUSTUTA
                    # =================================================

                    if delete_button.collidepoint(
                        mx,
                        my
                    ):

                        button_clicked = True


                        if selected_component is not None:

                            save_history()


                            if selected_component in components:

                                components.remove(
                                    selected_component
                                )


                            selected_component = None


                    if undo_button.collidepoint(mx, my):

                        button_clicked = True
                        undo()


                    # =================================================
                    # TÖÖALA
                    # =================================================

                    if not button_clicked:

                        # =============================================
                        # DETAIL ON KÄES
                        # =============================================

                        if held_component is not None:

                            if my > TOOLBAR_HEIGHT and mx < CANVAS_WIDTH:

                                save_history()


                                new_component = copy.deepcopy(
                                    held_component
                                )


                                components.append(
                                    new_component
                                )


                                snap_component(
                                    new_component
                                )


                                selected_component = new_component


                                # -------------------------------------
                                # Uus sama tüüpi detail jääb kätte.
                                # -------------------------------------

                                held_component = Component(
                                    selected_kind,
                                    mx,
                                    my
                                )


                        # =============================================
                        # MIDAGI EI OLE KÄES
                        # =============================================

                        else:

                            component = find_component(
                                (
                                    mx,
                                    my
                                )
                            )


                            selected_component = component


                            if component is not None:

                                dragged_component = component


                                # =====================================
                                # JUHE
                                # =====================================

                                if component.kind == 'wire':

                                    start_distance = distance(
                                        (
                                            mx,
                                            my
                                        ),
                                        (
                                            component.start_x,
                                            component.start_y
                                        )
                                    )


                                    end_distance = distance(
                                        (
                                            mx,
                                            my
                                        ),
                                        (
                                            component.end_x,
                                            component.end_y
                                        )
                                    )


                                    if (
                                        start_distance
                                        <=
                                        TERMINAL_HIT_RADIUS
                                    ):

                                        drag_mode = (
                                            'start'
                                        )


                                    elif (
                                        end_distance
                                        <=
                                        TERMINAL_HIT_RADIUS
                                    ):

                                        drag_mode = (
                                            'end'
                                        )


                                    else:

                                        drag_mode = (
                                            'whole'
                                        )


                                        offset_x = (
                                            component.x
                                            -
                                            mx
                                        )


                                        offset_y = (
                                            component.y
                                            -
                                            my
                                        )


                                # =====================================
                                # MUU DETAIL
                                # =====================================

                                else:

                                    drag_mode = (
                                        'whole'
                                    )


                                    offset_x = (
                                        component.x
                                        -
                                        mx
                                    )


                                    offset_y = (
                                        component.y
                                        -
                                        my
                                    )


                # =================================================
                # PAREM HIIRE NUPP
                # =================================================

                elif event.button == 3:

                    # =============================================
                    # JUHE / DETAIL ON KÄES
                    # =============================================

                    if held_component is not None:

                        # -----------------------------------------
                        # JUHTME PÖÖRAMINE
                        # -----------------------------------------

                        if held_component.kind == 'wire':

                            cx = held_component.x
                            cy = held_component.y


                            new_start = rotate_point(
                                held_component.start_x,
                                held_component.start_y,
                                cx,
                                cy,
                                90
                            )


                            new_end = rotate_point(
                                held_component.end_x,
                                held_component.end_y,
                                cx,
                                cy,
                                90
                            )


                            held_component.start_x = (
                                new_start[0]
                            )

                            held_component.start_y = (
                                new_start[1]
                            )


                            held_component.end_x = (
                                new_end[0]
                            )

                            held_component.end_y = (
                                new_end[1]
                            )


                            held_component.update_midpoint()


                        # -----------------------------------------
                        # MUU DETAIL
                        # -----------------------------------------

                        else:

                            held_component.angle += 90

                            if held_component.angle >= 360:

                                held_component.angle = 0


                    # =============================================
                    # LAUAL OLEV DETAIL
                    # =============================================

                    elif selected_component is not None:

                        save_history()


                        component = selected_component


                        # -----------------------------------------
                        # JUHE
                        # -----------------------------------------

                        if component.kind == 'wire':

                            cx = component.x
                            cy = component.y


                            new_start = rotate_point(
                                component.start_x,
                                component.start_y,
                                cx,
                                cy,
                                90
                            )


                            new_end = rotate_point(
                                component.end_x,
                                component.end_y,
                                cx,
                                cy,
                                90
                            )


                            component.start_x = (
                                new_start[0]
                            )

                            component.start_y = (
                                new_start[1]
                            )


                            component.end_x = (
                                new_end[0]
                            )

                            component.end_y = (
                                new_end[1]
                            )


                            component.update_midpoint()


                        # -----------------------------------------
                        # MUU DETAIL
                        # -----------------------------------------

                        else:

                            component.angle += 90

                            if component.angle >= 360:

                                component.angle = 0


                        snap_component(
                            component
                        )


            # =====================================================
            # HIIRE LIIKUMINE
            # =====================================================

            elif event.type == pygame.MOUSEMOTION:

                mx, my = pygame.mouse.get_pos()


                # =================================================
                # DETAIL ON KÄES
                # =================================================

                if held_component is not None:

                    # ---------------------------------------------
                    # JUHE
                    # ---------------------------------------------

                    if held_component.kind == 'wire':

                        # Väga oluline:
                        # liigume mõlemat juhet korraga.
                        #
                        # See parandab vea, kus ainult x/y
                        # muutus, aga juhtme otsad jäid vanale
                        # kohale.

                        dx = (
                            mx
                            -
                            held_component.x
                        )

                        dy = (
                            my
                            -
                            held_component.y
                        )


                        held_component.start_x += dx
                        held_component.start_y += dy

                        held_component.end_x += dx
                        held_component.end_y += dy


                        held_component.update_midpoint()


                    # ---------------------------------------------
                    # MUU DETAIL
                    # ---------------------------------------------

                    else:

                        held_component.x = mx
                        held_component.y = my


                    # =================================================
                    # MAGNEETILINE ÜHENDAMINE
                    # =================================================

                    nearest_terminal = None
                    nearest_target = None

                    smallest_distance = (
                        SNAP_DISTANCE
                    )


                    for terminal in held_component.terminals():

                        target = find_nearest_terminal(
                            terminal,
                            held_component
                        )


                        if target is None:
                            continue


                        d = distance(
                            terminal,
                            target
                        )


                        if d < smallest_distance:

                            smallest_distance = d

                            nearest_terminal = terminal

                            nearest_target = target


                    if (
                        nearest_terminal is not None
                        and
                        nearest_target is not None
                    ):

                        dx = (
                            nearest_target[0]
                            -
                            nearest_terminal[0]
                        )

                        dy = (
                            nearest_target[1]
                            -
                            nearest_terminal[1]
                        )


                        # -----------------------------------------
                        # Nihutame kogu detaili.
                        # -----------------------------------------

                        if held_component.kind == 'wire':

                            held_component.start_x += dx
                            held_component.start_y += dy

                            held_component.end_x += dx
                            held_component.end_y += dy

                            held_component.update_midpoint()


                        else:

                            held_component.x += dx
                            held_component.y += dy


                # =================================================
                # LAUAL OLEV DETAIL
                # =================================================

                if dragged_component is not None:

                    component = dragged_component


                    # =============================================
                    # JUHE
                    # =============================================

                    if component.kind == 'wire':

                        # -----------------------------------------
                        # KOGU JUHE
                        # -----------------------------------------

                        if drag_mode == 'whole':

                            new_center_x = (
                                mx
                                +
                                offset_x
                            )

                            new_center_y = (
                                my
                                +
                                offset_y
                            )


                            dx = (
                                new_center_x
                                -
                                component.x
                            )

                            dy = (
                                new_center_y
                                -
                                component.y
                            )


                            component.start_x += dx
                            component.start_y += dy

                            component.end_x += dx
                            component.end_y += dy


                            component.update_midpoint()


                        # -----------------------------------------
                        # ALGUS
                        # -----------------------------------------

                        elif drag_mode == 'start':

                            component.start_x = mx
                            component.start_y = my

                            component.update_midpoint()


                        # -----------------------------------------
                        # LÕPP
                        # -----------------------------------------

                        elif drag_mode == 'end':

                            component.end_x = mx
                            component.end_y = my

                            component.update_midpoint()


                    # =============================================
                    # MUU DETAIL
                    # =============================================

                    else:

                        component.x = (
                            mx
                            +
                            offset_x
                        )

                        component.y = (
                            my
                            +
                            offset_y
                        )


            # =====================================================
            # HIIRE NUPP ÜLES
            # =====================================================

            elif event.type == pygame.MOUSEBUTTONUP:

                if event.button == 1:

                    # =============================================
                    # LAUALT LIIGUTATUD DETAIL
                    # =============================================

                    if dragged_component is not None:

                        component = dragged_component


                        if component.kind == 'wire':

                            if (
                                drag_mode
                                ==
                                'start'
                            ):

                                snap_wire_endpoint(
                                    component,
                                    'start'
                                )


                            elif (
                                drag_mode
                                ==
                                'end'
                            ):

                                snap_wire_endpoint(
                                    component,
                                    'end'
                                )


                            else:

                                snap_component(
                                    component
                                )


                        else:

                            snap_component(
                                component
                            )


                    dragged_component = None
                    drag_mode = None


        # =========================================================
        # AHELA SIMULATSIOON
        # =========================================================

        if simulation_dirty:

            simulation_result = simulate_circuit()
            simulation_dirty = False


        bulb_lit = simulation_result['bulb_lit']
        bulb_burned_out = simulation_result['bulbs_burned_out']


        # =========================================================
        # TAUST
        # =========================================================

        screen.fill(
            LIGHT_GRAY
        )


        pygame.draw.rect(
            screen,
            WHITE,
            (0, TOOLBAR_HEIGHT, CANVAS_WIDTH, HEIGHT - TOOLBAR_HEIGHT)
        )


        for grid_x in range(12, CANVAS_WIDTH, 24):

            pygame.draw.line(
                screen,
                GRID_COLOR,
                (grid_x, TOOLBAR_HEIGHT),
                (grid_x, HEIGHT),
                1
            )


        for grid_y in range(TOOLBAR_HEIGHT + 12, HEIGHT, 24):

            pygame.draw.line(
                screen,
                GRID_COLOR,
                (0, grid_y),
                (CANVAS_WIDTH, grid_y),
                1
            )


        # =========================================================
        # ÜLEMINE RIBA
        # =========================================================

        pygame.draw.rect(
            screen,
            GRAY,
            (
                0,
                0,
                CANVAS_WIDTH,
                TOOLBAR_HEIGHT
            )
        )


        pygame.draw.line(
            screen,
            (216, 226, 230),
            (0, TOOLBAR_HEIGHT - 1),
            (CANVAS_WIDTH, TOOLBAR_HEIGHT - 1),
            1
        )


        # =========================================================
        # DETAILI NUPUD
        # =========================================================

        for kind, rect, name in buttons:

            hovered = rect.collidepoint(pygame.mouse.get_pos())

            if selected_kind == kind:

                background_color = LIGHT_GREEN
                border_color = GREEN

            else:

                background_color = WHITE if not hovered else (232, 241, 244)
                border_color = (194, 208, 214)


            pygame.draw.rect(
                screen,
                background_color,
                rect,
                border_radius=8
            )


            pygame.draw.rect(
                screen,
                border_color,
                rect,
                1,
                border_radius=8
            )


            text = font.render(
                name,
                True,
                BLACK
            )


            screen.blit(
                text,
                (
                    rect.centerx -
                    text.get_width() / 2,

                    rect.centery -
                    text.get_height() / 2
                )
            )


        # =========================================================
        # KUSTUTA
        # =========================================================

        if selected_component is not None:

            delete_color = LIGHT_RED

        else:

            delete_color = WHITE


        pygame.draw.rect(
            screen,
            delete_color,
            delete_button,
            border_radius=8
        )


        pygame.draw.rect(
            screen,
            RED if selected_component is not None else (194, 208, 214),
            delete_button,
            1,
            border_radius=8
        )


        text = font.render(
            "Kustuta",
            True,
            BLACK
        )


        screen.blit(
            text,
            (
                delete_button.centerx -
                text.get_width() / 2,

                delete_button.centery -
                text.get_height() / 2
            )
        )


        pygame.draw.rect(
            screen,
            WHITE,
            undo_button,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (194, 208, 214),
            undo_button,
            1,
            border_radius=8
        )

        text = font.render("Undo", True, BLACK)
        screen.blit(
            text,
            (
                undo_button.centerx - text.get_width() / 2,
                undo_button.centery - text.get_height() / 2
            )
        )


        measurement_name, voltage, current, resistance, bulb_power = measurement_values(simulation_result)

        pygame.draw.rect(
            screen,
            DARK_PANEL,
            (CANVAS_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
        )

        pygame.draw.line(
            screen,
            (52, 72, 81),
            (CANVAS_WIDTH, 0),
            (CANVAS_WIDTH, HEIGHT),
            1
        )

        panel_x = CANVAS_WIDTH + 24

        text = small_font.render("ELEKTRISKEEM", True, PANEL_MUTED)
        screen.blit(text, (panel_x, 20))

        text = title_font.render(measurement_name, True, PANEL_TEXT)
        screen.blit(text, (panel_x, 39))

        status_bar = pygame.Rect(panel_x, 86, SIDEBAR_WIDTH - 48, 38)
        if simulation_result['solver_error']:

            status = 'ARVUTUSVIGA'
            status_color = (111, 58, 57)

        elif simulation_result['short_circuit']:

            status = 'LÜHIS'
            status_color = (111, 58, 57)

        elif bulb_burned_out:

            status = "PIRN LÄBI PÕLENUD"
            status_color = (111, 58, 57)

        elif bulb_lit:

            status = "PIRN PÕLEB"
            status_color = (31, 111, 82)

        elif simulation_result['closed']:

            status = "VOOL LIIGA VÄIKE"
            status_color = (119, 91, 42)

        else:

            status = "AHEL AVATUD"
            status_color = (111, 58, 57)


        pygame.draw.rect(screen, status_color, status_bar, border_radius=7)

        status_text = font.render(status, True, WHITE)
        screen.blit(
            status_text,
            (
                status_bar.centerx - status_text.get_width() / 2,
                status_bar.centery - status_text.get_height() / 2
            )
        )

        whole_circuit = selected_component is None or selected_component.kind == 'wire'
        meters = [
            ("KOGUPINGE" if whole_circuit else "KLEMMIPINGE", format_measurement(voltage, 'V')),
            ("EKVIVALENTTAKISTUS" if whole_circuit else "TAKISTUS", format_measurement(resistance, 'Ω')),
            ("KOGUVOOL" if whole_circuit else "VOOL", format_measurement(current, 'A')),
            ("KOGUVÕIMSUS" if whole_circuit else "VÕIMSUS", format_measurement(bulb_power, 'W'))
        ]

        for index, (label, value) in enumerate(meters):

            y = 143 + index * 58
            screen.blit(
                small_font.render(label, True, PANEL_MUTED),
                (panel_x, y)
            )
            screen.blit(
                number_font.render(value, True, PANEL_TEXT),
                (panel_x, y + 17)
            )

            if index < len(meters) - 1:

                pygame.draw.line(
                    screen,
                    (52, 72, 81),
                    (panel_x, y + 51),
                    (WIDTH - 24, y + 51),
                    1
                )


        pygame.draw.line(
            screen,
            (52, 72, 81),
            (panel_x, 386),
            (WIDTH - 24, 386),
            1
        )

        screen.blit(
            title_font.render("Detaili väärtus", True, PANEL_TEXT),
            (panel_x, 398)
        )

        if selected_component is not None and selected_component.kind == 'resistor':

            field_label = "TAKISTUS"
            field_value = f"{selected_component.resistance:g}"
            unit = "Ω"

        elif selected_component is not None and selected_component.kind == 'bulb':

            field_label = "LAMBI TAKISTUS"
            field_value = f"{selected_component.resistance:g}"
            unit = "Ω"

        elif selected_component is not None and selected_component.kind == 'battery':

            field_label = "ALLIKA PINGE"
            field_value = f"{selected_component.voltage:g}"
            unit = "V"

        else:

            field_label = "VALI TAKISTI, LAMP VÕI ALLIKAS"
            field_value = ""
            unit = ""

        screen.blit(
            small_font.render(field_label, True, PANEL_MUTED),
            (panel_x, 435)
        )

        field_border = RED if input_error else GREEN if edited_field else (74, 96, 104)
        field_background = (35, 53, 62) if field_value else (31, 45, 53)
        pygame.draw.rect(screen, field_background, property_field, border_radius=7)
        pygame.draw.rect(screen, field_border, property_field, 2 if edited_field else 1, border_radius=7)

        displayed_value = field_text if edited_field else field_value
        value_text = font.render(displayed_value, True, PANEL_TEXT)
        screen.blit(
            value_text,
            (property_field.x + 13, property_field.centery - value_text.get_height() / 2)
        )

        unit_text = font.render(unit, True, PANEL_MUTED)
        screen.blit(
            unit_text,
            (property_field.right - unit_text.get_width() - 13,
             property_field.centery - unit_text.get_height() / 2)
        )

        hint_text = "Vajuta Enter, et rakendada" if edited_field else "Klõpsa väärtusel muutmiseks"
        screen.blit(
            small_font.render(hint_text, True, PANEL_MUTED),
            (panel_x, 520)
        )

        if input_error:

            screen.blit(
                small_font.render("Sisesta arv, mis on suurem kui 0", True, (255, 145, 135)),
                (panel_x, 542)
            )

        pygame.draw.line(
            screen,
            (52, 72, 81),
            (panel_x, HEIGHT - 82),
            (WIDTH - 24, HEIGHT - 82),
            1
        )

        screen.blit(
            small_font.render("Ctrl+Z  Samm tagasi", True, PANEL_MUTED),
            (panel_x, HEIGHT - 62)
        )

        screen.blit(
            small_font.render("Parema klahviga pööra detaili", True, PANEL_MUTED),
            (panel_x, HEIGHT - 38)
        )


        # =========================================================
        # LAUAL OLEVAD DETAILID
        # =========================================================

        screen.set_clip(
            pygame.Rect(
                0,
                TOOLBAR_HEIGHT,
                CANVAS_WIDTH,
                HEIGHT - TOOLBAR_HEIGHT
            )
        )

        for component in components:

            component.draw(
                screen,
                component == selected_component,
                simulation_result['bulbs_lit'].get(component, False),
                component.burned_out
            )


        for point in simulation_result['junctions']:
            pygame.draw.circle(screen, BLACK, (round(point[0]), round(point[1])), 6)

        # =========================================================
        # KÄES OLEV DETAIL
        # =========================================================

        if held_component is not None:

            held_component.draw(
                screen,
                True,
                False,
                False
            )


        screen.set_clip(None)


        # =========================================================
        # EKRAANI UUENDAMINE
        # =========================================================

        pygame.display.flip()

        clock.tick(60)


    pygame.quit()


