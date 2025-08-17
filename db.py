import sqlite3
import random
from datetime import datetime

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
        
        self.conn.commit()

    def update_leaderboard(self, player_name, player_score):
        c = self.conn.cursor()
        c.execute("INSERT into leaderboard (name, score, date) VALUES(?,?,?)",(player_name, player_score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
    
    def all(self):
        c = self.conn.cursor()
        c.execute("SELECT name, score, date FROM leaderboard ORDER BY score DESC")
        return c.fetchall()

    def get_leaderboard(self):
        c = self.conn.cursor()
        c.execute("SELECT name, score, date FROM leaderboard ORDER BY score DESC")
        return c.fetchall()
    
    def close(self):
        self.conn.close()
