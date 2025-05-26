import os

WHITE = (255, 255, 255) 
BLUE = (50, 50, 255) 
RED = (255, 50, 50) 
STAR_COLORS = [ 
    (255, 255, 255), 
    (200, 200, 255), 
    (255, 220, 180), 
    (255, 200, 200), 
    (180, 255, 220), 
]

MAX_ENEMIES = 10 
PLAYER_LIVES = 4 
LEVEL_UP_KILLS = 15 
PLAYER_COLORS = [ 
    (50, 50, 255), 
    (100, 100, 180), 
    (180, 100, 100), 
    (40, 40, 40), 
]
SAVE_FILE = os.path.join(os.path.dirname(__file__), "..", "savegame.json")

ENEMY_SPAWN_TIME = 120 
BULLET_SPEED = 18 
BULLET_LIFETIME = 60 
ENEMY_BULLET_SPEED = 16 
ENEMY_BULLET_LIFETIME = 90 
ENEMY_SPEED = 3 

DIFFICULTY_LEVELS = [ 
    {
        "name": "Легко", 
        "enemy_speed": 2, 
        "enemy_spawn": 180, 
        "max_enemies": 6 
    },
    {
        "name": "Средне", 
        "enemy_speed": 3, 
        "enemy_spawn": 120, 
        "max_enemies": 10 
    },
    {
        "name": "Сложно", 
        "enemy_speed": 4, 
        "enemy_spawn": 70, 
        "max_enemies": 16 
    }
]

class GameConfig: 
    def __init__(self, width, height):
        self.width = width 
        self.height = height 