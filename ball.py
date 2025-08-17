import pygame
import random

WIDTH, HEIGHT = 800, 650
BALL_SIZE = 15
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
WHITE = (255, 255, 255)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, 
                               HEIGHT // 2 - BALL_SIZE // 2, 
                               BALL_SIZE, BALL_SIZE)
        self.dx = BALL_SPEED_X * random.choice((1, -1))
        self.dy = BALL_SPEED_Y * random.choice((1, -1))
    
    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
        
        if self.rect.left <= 0:
            return "right"
        if self.rect.right >= WIDTH:
            return "left"
        return None
    
    def collide(self, paddle):
        if self.rect.colliderect(paddle.rect):
            self.dx *= -1.1
            self.dy = random.uniform(-1, 1) * BALL_SPEED_Y
            return True
        return False
    
    def draw(self,screen):
        pygame.draw.rect(screen, WHITE, self.rect)
