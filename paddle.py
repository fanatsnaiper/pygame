import pygame

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
HEIGHT = 650
WHITE = (255, 255, 255)
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0
    
    def move(self, dy):
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
    
    def draw(self,screen):
        pygame.draw.rect(screen, WHITE, self.rect)