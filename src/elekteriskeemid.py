import pygame

pygame.init()

WIDTH = 640
HEIGHT = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 170, 255)
GRAY = (120, 120, 120)
YELLOW = (255, 220, 0)
RED = (230, 80, 80)
GREEN = (60, 180, 60)

font = pygame.font.SysFont(None, 28)

run = True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill(WHITE)

    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 40), 2)

    # 3 komponentide ruutu
    pygame.draw.rect(screen, BLACK, (10, 5, 70, 30), 2)
    pygame.draw.rect(screen, BLACK, (90, 5, 70, 30), 2)
    pygame.draw.rect(screen, BLACK, (170, 5, 70, 30), 2)
    pygame.draw.rect(screen, BLACK, (250, 5, 70, 30), 2)

    # TAKISTI
    pygame.draw.rect(screen, BLACK, (30, 10, 30, 20), 2)

    resistor_text = font.render("R", True, BLACK)
    screen.blit(resistor_text, (40, 11))

    # PATAREI
    pygame.draw.rect(screen, BLACK, (100, 10, 50, 20), 2)

    pygame.draw.line(screen, BLACK, (105, 20), (113, 20), 2)
    pygame.draw.line(screen, BLACK, (109, 16), (109, 24), 2)

    pygame.draw.line(screen, BLACK, (137, 20), (145, 20), 2)

    # LAMP
    pygame.draw.circle(screen, BLACK, (205, 20), 10, 2)

    pygame.draw.line(screen, BLACK, (198, 13), (212, 27), 2)
    pygame.draw.line(screen, BLACK, (212, 13), (198, 27), 2)

    # JUHE

    pygame.draw.line(screen, BLACK, (268, 13), (292, 13), 2)

    # Parempoolne kast
    pygame.draw.rect(screen, BLACK, (550, 8, 70, 24), 2)

    # Vasakpoolne menüü
    pygame.draw.rect(screen, BLACK, (10, 40, 70, 350), 3)

    y = 50

    for i in range(6):

        pygame.draw.rect(screen, BLACK, (15, y, 60, 45), 2)

        if i == 0:
            pygame.draw.line(screen, BLACK, (28, y + 22), (48, y + 22), 2)
            pygame.draw.polygon(screen, BLACK,
                                [(25, y + 22), (31, y + 18), (31, y + 26)])

            pygame.draw.line(screen, BLACK, (48, y + 22), (48, y + 10), 2)
            pygame.draw.polygon(screen, BLACK,
                                [(44, y + 13), (48, y + 7), (52, y + 13)])

            pygame.draw.circle(screen, BLACK, (48, y + 22), 4)

        elif i == 1:
            pygame.draw.line(screen, BLACK, (40, y + 10), (40, y + 34), 2)

            pygame.draw.polygon(screen, BLACK,
                                [(40, y + 7), (36, y + 13), (44, y + 13)])
            pygame.draw.polygon(screen, BLACK,
                                [(40, y + 37), (36, y + 31), (44, y + 31)])

            pygame.draw.circle(screen, BLUE, (40, y + 22), 3)

        elif i == 2:
            pygame.draw.rect(screen, BLACK, (24, y + 10, 32, 22), 2)
            pygame.draw.line(screen, BLACK, (40, y + 32), (40, y + 38), 2)
            pygame.draw.line(screen, BLACK, (34, y + 35), (46, y + 35), 2)

        elif i == 3:
            for xx in range(24, 56, 6):
                for yy in range(y + 12, y + 34, 6):
                    pygame.draw.circle(screen, BLUE, (xx, yy), 1)

            for xx in range(27, 53, 6):
                for yy in range(y + 15, y + 31, 6):
                    pygame.draw.circle(screen, RED, (xx, yy), 1)

        elif i == 4:
            pygame.draw.circle(screen, BLACK, (25, y + 11), 3)
            pygame.draw.circle(screen, BLACK, (55, y + 31), 3)

        elif i == 5:
            pygame.draw.circle(screen, BLUE, (28, y + 32), 6)
            pygame.draw.circle(screen, YELLOW, (54, y + 36), 5)
            pygame.draw.circle(screen, GRAY, (42, y + 18), 2)

        y += 55

    pygame.display.flip()

pygame.quit()
