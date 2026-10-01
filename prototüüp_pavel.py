import pygame
import sys

pygame.init()

WIDTH = 600
HEIGHT = 365

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Session")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 25)
clock = pygame.time.Clock()


def draw_window():
    screen.fill(WHITE)

  
    # Left vertical divider
   
    pygame.draw.line(
        screen,
        BLACK,
        (73, 0),
        (73, HEIGHT),
        6
    )

 
    # Empty boxes on the left

    box_x = 7
    box_width = 61
    box_height = 49

  
    box_positions = [51, 105, 160, 215, 270, 320]

    for y in box_positions:
        pygame.draw.rect(
            screen,
            WHITE,
            (box_x, y, box_width, box_height)
        )

        pygame.draw.rect(
            screen,
            BLACK,
            (box_x, y, box_width, box_height),
            5
        )

    
    # Top-right empty box

    pygame.draw.rect(
        screen,
        WHITE,
        (502, 5, 88, 34)
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (502, 5, 88, 34),
        5
    )

  
    # Main button 1
   
    button1 = pygame.Rect(
        202, 102, 301, 75
    )

    pygame.draw.rect(
        screen,
        WHITE,
        button1
    )

    pygame.draw.rect(
        screen,
        BLACK,
        button1,
        6
    )

    text1 = font.render(
        "Taasta eelmine sessioon",
        True,
        BLACK
    )

    screen.blit(
        text1,
        text1.get_rect(center=button1.center)
    )


    button2 = pygame.Rect(
        202, 186, 301, 76
    )

    pygame.draw.rect(
        screen,
        WHITE,
        button2
    )

    pygame.draw.rect(
        screen,
        BLACK,
        button2,
        6
    )

    text2 = font.render(
        "Laadi fail",
        True,
        BLACK
    )

    screen.blit(
        text2,
        text2.get_rect(center=button2.center)
    )



# Main loop

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_window()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
