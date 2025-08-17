import pygame
WIDTH, HEIGHT = 800, 650
def create():
    # Создание окна
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    return screen, clock