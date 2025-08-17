import pygame
import sys
from storage import *
from create_window import create
from db import DatabaseManager
from ball import Ball
from paddle import Paddle
# Инициализация Pygame
pygame.init()

# Шрифты
big_font = pygame.font.Font(None, 74)
medium_font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 26)
tiny_font = pygame.font.Font(None, 24)

def draw_middle_line(screen):
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 10))

def show_scores(screen,player_name, left_score, right_score, misses_left):
    name_text = small_font.render(player_name, True, WHITE)
    screen.blit(name_text, (20, 20))
    
    left_text = big_font.render(str(left_score), True, WHITE)
    right_text = big_font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH // 4, 20))
    screen.blit(right_text, (3 * WIDTH // 4 - right_text.get_width(), 20))
    
    misses_text = small_font.render(f"Попытки: {MAX_MISSES - misses_left}/{MAX_MISSES}", True, RED)
    screen.blit(misses_text, (20, HEIGHT - 30))

def show_game_over(screen, db_manager, player_name, score):

    # Получаем актуальную таблицу лидеров
    leaderboard = db_manager.get_leaderboard()
    
    # Определяем позицию игрока
    player_position = None
    for i, entry in enumerate(leaderboard):
        if entry[0] == player_name and entry[1] == score:
            player_position = i + 1
            break
    
    screen.fill(BLACK)
    
    # Заголовок
    game_over_text = big_font.render("ИГРА ОКОНЧЕНА", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 30))
    
    # Результат игрока
    result_text = medium_font.render(f"{player_name}: {score} очков", True, WHITE)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 100))
    
    # Позиция в таблице
    if player_position is not None:
        position_text = medium_font.render(f"Ваше место: {player_position}", True, 
                                         GOLD if player_position == 1 
                                         else SILVER if player_position == 2 
                                         else BRONZE if player_position == 3 
                                         else WHITE)
        screen.blit(position_text, (WIDTH // 2 - position_text.get_width() // 2, 150))
    
    # Таблица лидеров
    lb_title = medium_font.render("Топ-5 игроков:", True, WHITE)
    screen.blit(lb_title, (WIDTH // 2 - lb_title.get_width() // 2, 220))
    
    # Выводим топ-5 игроков
    for i, entry in enumerate(leaderboard):
        color = GOLD if i == 0 else SILVER if i == 1 else BRONZE if i == 2 else WHITE
        name, score, date = entry
        
        # Основная строка
        lb_entry = small_font.render(f"{i+1}. {name}: {score}", True, color)
        screen.blit(lb_entry, (WIDTH // 2 - lb_entry.get_width() // 2, 280 + i * 60))
        
        # Дата под основным текстом
        date_text = tiny_font.render(f"({date.split()[0]})", True, GRAY)
        screen.blit(date_text, (WIDTH // 2 - date_text.get_width() // 2, 310 + i * 60))
    
    # Инструкция
    restart_text = small_font.render("Нажмите R для рестарта", True, GRAY)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()
    

def get_player_name(screen, clock):
    name = ""
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name:
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode
        
        screen.fill(BLACK)
        title_text = medium_font.render("Введите ваше имя:", True, WHITE)
        name_text = medium_font.render(name, True, WHITE)
        prompt_text = small_font.render("Нажмите Enter для продолжения", True, GRAY)
        
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 50))
        
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = WIDTH // 2 + name_text.get_width() // 2 + 5
            pygame.draw.line(screen, WHITE, (cursor_x, HEIGHT // 2), 
                           (cursor_x, HEIGHT // 2 + name_text.get_height()), 2)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return name

def show_instruction(screen, clock):
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                        input_active = False
        screen.fill(BLACK)
        title_text = medium_font.render("Цель игры - набрать как можно больше очков", True, WHITE)
        title_text_2 = medium_font.render("Для управления волспользуйся стрелочками", True, WHITE)
        title_text_3 = medium_font.render("Обрати внимание: если пропустишь пять мячей", True, WHITE)
        title_text_4 = medium_font.render("игра закончится поражением", True, WHITE)
        prompt_text = small_font.render("Нажмите Enter для продолжения", True, GRAY)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 200))
        screen.blit(title_text_2,(WIDTH // 2 - title_text_2.get_width() // 2, HEIGHT // 2 -100))
        screen.blit(title_text_3, (WIDTH // 2 - title_text_3.get_width() // 2, HEIGHT // 2))
        screen.blit(title_text_4, (WIDTH // 2 - title_text_3.get_width() // 2, HEIGHT // 2 + 100))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 150))
        pygame.display.flip()
        clock.tick(FPS)

    return

def main():
    screen, clock = create()
    db_manager = DatabaseManager()
    print(db_manager.all())
    player_name = get_player_name(screen, clock)
    show_instruction(screen, clock)
    player = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    opponent = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()
    
    running = True
    game_active = True
    misses = 0
    db_updated = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player.score = 0
                    opponent.score = 0
                    misses = 0
                    ball.reset()
                    game_active = True
        
        if game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player.rect.top > 0:
                player.move(-PADDLE_SPEED)
            if keys[pygame.K_DOWN] and player.rect.bottom < HEIGHT:
                player.move(PADDLE_SPEED)
            
            if opponent.rect.centery < ball.rect.centery:
                opponent.move(min(PADDLE_SPEED - 5, ball.rect.centery - opponent.rect.centery))
            elif opponent.rect.centery > ball.rect.centery:
                opponent.move(-min(PADDLE_SPEED - 5, opponent.rect.centery - ball.rect.centery))
            
            result = ball.move()
            if result == "left":
                player.score += 1
                ball.reset()
            elif result == "right":
                opponent.score += 1
                misses += 1
                ball.reset()
                
                if misses >= MAX_MISSES:
                    game_active = False
            
            ball.collide(player)
            ball.collide(opponent)
            
            screen.fill(BLACK)
            draw_middle_line(screen)
            player.draw(screen)
            opponent.draw(screen)
            ball.draw(screen)
            show_scores(screen, player_name, player.score, opponent.score, misses)
        else:
            if db_updated == False:
                db_manager.update_leaderboard(player_name, player.score)
                db_updated = True
            if db_updated == True:
                show_game_over(screen, db_manager, player_name, player.score)
        pygame.display.flip()
        clock.tick(FPS)
    #db_manager.update_leaderboard(player_name, player.score)
    db_manager.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()