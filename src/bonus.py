import pygame
import random
from settings import *

BONUS_TYPES = ["heal", "shield"]

class Bonus:
    def __init__(self, pos, config):
        self.pos = pygame.Vector2(pos)
        self.radius = 18
        self.type = random.choice(BONUS_TYPES)
        self.config = config
        self.lifetime = 600  

    def update(self):
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0

    def draw(self, surface, camera_pos):
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        color = (100, 255, 100) if self.type == "heal" else (100, 200, 255)
        pygame.draw.circle(surface, color, (int(draw_pos.x), int(draw_pos.y)), self.radius)
        if self.type == "heal":
            pygame.draw.line(surface, (255,255,255), (int(draw_pos.x)-8, int(draw_pos.y)), (int(draw_pos.x)+8, int(draw_pos.y)), 3)
            pygame.draw.line(surface, (255,255,255), (int(draw_pos.x), int(draw_pos.y)-8), (int(draw_pos.x), int(draw_pos.y)+8), 3)
        else:
            pygame.draw.circle(surface, (255,255,255), (int(draw_pos.x), int(draw_pos.y)), self.radius-4, 2)