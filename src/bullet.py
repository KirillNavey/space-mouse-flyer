import pygame
import os
from settings import *

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

class Bullet:
    def __init__(self, pos, velocity, speed, color, lifetime, config, is_enemy=False, game_api=None, **kwargs):
        self.pos = pygame.Vector2(pos)
        self.dir = velocity.normalize()
        self.speed = speed
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.config = config
        self.is_enemy = is_enemy
        self.radius = kwargs.get("radius", 5)
        self.sprite = kwargs.get("sprite", None)
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)
        if USE_SPRITES and self.sprite is None:
            try:
                fname = "enemy_bullet.png" if self.is_enemy else "bullet.png"
                self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, fname)).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (18, 18))
            except Exception as e:
                # print("Не удалось загрузить спрайт пули:", e)
                self.sprite = None

    def update(self, game_api=None):
        self.pos += self.dir * self.speed
        self.age += 1

    def draw(self, surface, camera_pos, game_api=None):
        # Позволяет модам полностью заменить отрисовку пули
        if game_api and "draw_bullet" in game_api:
            return game_api["draw_bullet"](self, surface, camera_pos, game_api)
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        if USE_SPRITES and self.sprite:
            angle = -self.dir.angle_to(pygame.Vector2(0, -1))
            rotated = pygame.transform.rotate(self.sprite, angle)
            rect = rotated.get_rect(center=(int(draw_pos.x), int(draw_pos.y)))
            surface.blit(rotated, rect)
        else:
            pygame.draw.circle(surface, self.color, (int(draw_pos.x), int(draw_pos.y)), self.radius)

    def is_alive(self, game_api=None):
        return self.age < self.lifetime