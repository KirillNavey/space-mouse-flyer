import pygame
import random
import math
import os
from settings import *

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

class Meteor:
    def __init__(self, config, center_pos, **kwargs):
        self.config = config
        self.radius = kwargs.get("radius", random.randint(18, 32))
        x = center_pos.x + random.randint(-config.width // 2, config.width // 2)
        y = center_pos.y - config.height // 2 - self.radius
        self.pos = pygame.Vector2(x, y)
        self.speed = kwargs.get("speed", random.uniform(8, 16))
        self.angle = kwargs.get("angle", random.uniform(-0.2, 0.2))
        self.color = kwargs.get("color", (180, 180, 180))
        self.lifetime = kwargs.get("lifetime", 1200)
        self.age = 0
        self.sprite = kwargs.get("sprite", None)
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)
        if USE_SPRITES and self.sprite is None:
            try:
                self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, "meteor.png")).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (self.radius*2, self.radius*2))
            except Exception as e:
                # print("Не удалось загрузить спрайт метеорита:", e)
                self.sprite = None

    def update(self):
        self.pos.x += self.angle * self.speed
        self.pos.y += self.speed
        self.age += 1

    def is_alive(self):
        return self.age < self.lifetime and self.pos.y - self.radius < self.config.height + 1000

    def draw(self, surface, camera_pos, game_api=None):
        # Используем функцию ядра для кастомной отрисовки, если она есть
        if game_api and "draw_meteor" in game_api:
            return game_api["draw_meteor"](self, surface, camera_pos)
        draw_x = self.pos.x - camera_pos.x + self.config.width // 2
        draw_y = self.pos.y - camera_pos.y + self.config.height // 2
        if USE_SPRITES and self.sprite:
            rect = self.sprite.get_rect(center=(int(draw_x), int(draw_y)))
            surface.blit(self.sprite, rect)
        else:
            pygame.draw.circle(surface, self.color, (int(draw_x), int(draw_y)), self.radius)
            pygame.draw.circle(surface, (100, 100, 100), (int(draw_x), int(draw_y)), self.radius, 2)