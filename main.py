import pygame
import sys
import random
import sqlite3
from datetime import datetime

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 650
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
PADDLE_SPEED = 7
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
MAX_MISSES = 5

# Список случайных имён
RANDOM_NAMES = ["Alex", "Sam", "Taylor", "Jordan", "Casey", 
               "Riley", "Jamie", "Morgan", "Dylan", "Cameron",
               "Jessie", "Robin", "Avery", "Peyton", "Quinn"]

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Шрифты
big_font = pygame.font.Font(None, 74)
medium_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('pong_leaderboard.db')
        self._init_db()
    
    def _init_db(self):
        c = self.conn.cursor()
        
        # Создаем таблицу лидеров
        c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      score INTEGER NOT NULL,
                      date TEXT NOT NULL)''')
        
        # Создаем таблицу настроек
        c.execute('''CREATE TABLE IF NOT EXISTS settings
                     (id INTEGER PRIMARY KEY,
                      initialized INTEGER DEFAULT 0)''')
        
        # Проверяем, инициализирована ли база
        c.execute("SELECT initialized FROM settings WHERE id = 1")
        result = c.fetchone()
        
        if not result or result[0] == 0:
            # Заполняем таблицу лидеров случайными именами один раз
            scores = [50, 40, 30, 20, 10]
            for i, score in enumerate(scores):
                name = random.choice(RANDOM_NAMES)
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO leaderboard (name, score, date) VALUES (?, ?, ?)",
                         (name, score, date))
            
            # Помечаем базу как инициализированную
            c.execute("INSERT OR REPLACE INTO settings (id, initialized) VALUES (1, 1)")
            self.conn.commit()
    
    def update_leaderboard(self, player_name, player_score):
        c = self.conn.cursor()
        
        # Получаем текущие результаты
        c.execute("SELECT name, score FROM leaderboard ORDER BY score DESC")
        current_leaders = c.fetchall()
        
        # Проверяем, побил ли игрок чей-то результат
        new_leaders = []
        added = False
        
        for name, score in current_leaders:
            if not added and player_score >= score:
                new_leaders.append((player_name, player_score))
                added = True
            if len(new_leaders) < 5 and (name != player_name or added):
                new_leaders.append((name, score))
        
        # Если не добавили и есть место
        if not added and len(new_leaders) < 5:
            new_leaders.append((player_name, player_score))
        
        # Обрезаем до 5 записей
        new_leaders = new_leaders[:5]
        
        # Очищаем и перезаписываем таблицу
        c.execute("DELETE FROM leaderboard")
        
        for name, score in new_leaders:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO leaderboard (name, score, date) VALUES (?, ?, ?)",
                     (name, score, date))
        
        self.conn.commit()
    
    def get_leaderboard(self):
        c = self.conn.cursor()
        c.execute("SELECT name, score, date FROM leaderboard ORDER BY score DESC")
        return c.fetchall()
    
    def close(self):
        self.conn.close()

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
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

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
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

def draw_middle_line():
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, y, 4, 10))

def show_scores(player_name, left_score, right_score, misses_left):
    name_text = small_font.render(player_name, True, WHITE)
    screen.blit(name_text, (20, 20))
    
    left_text = big_font.render(str(left_score), True, WHITE)
    right_text = big_font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH // 4, 20))
    screen.blit(right_text, (3 * WIDTH // 4 - right_text.get_width(), 20))
    
    misses_text = small_font.render(f"Попытки: {MAX_MISSES - misses_left}/{MAX_MISSES}", True, RED)
    screen.blit(misses_text, (20, HEIGHT - 30))

def show_game_over(db_manager, player_name, score):
    # Обновляем таблицу лидеров
    db_manager.update_leaderboard(player_name, score)
    
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

def get_player_name():
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

def show_instruction():
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
    db_manager = DatabaseManager()
    player_name = get_player_name()
    show_instruction()
    player = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    opponent = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()
    
    running = True
    game_active = True
    misses = 0
    
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
                opponent.move(min(PADDLE_SPEED - 1, ball.rect.centery - opponent.rect.centery))
            elif opponent.rect.centery > ball.rect.centery:
                opponent.move(-min(PADDLE_SPEED - 1, opponent.rect.centery - ball.rect.centery))
            
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
            draw_middle_line()
            player.draw()
            opponent.draw()
            ball.draw()
            show_scores(player_name, player.score, opponent.score, misses)
        else:
            show_game_over(db_manager, player_name, player.score)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    db_manager.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()