import pygame
import math
import os
from settings import *

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

class BlackHole:
    def __init__(self, pos, config, game_api=None, **kwargs):
        self.pos = pygame.Vector2(pos)
        self.config = config
        self.radius = kwargs.get("radius", 100)
        self.strength = kwargs.get("strength", 1.2)
        self.age = 0
        self.max_age = kwargs.get("max_age", 900)
        self.sprite = kwargs.get("sprite", None)
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)
        if USE_SPRITES and self.sprite is None:
            try:
                self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, "blackhole.png")).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (self.radius*2, self.radius*2))
            except Exception as e:
                # print("Не удалось загрузить спрайт черной дыры:", e)
                self.sprite = None

    def update(self, game_api=None):
        self.age += 1

    def is_alive(self, game_api=None):
        return self.age < self.max_age

    def attract(self, obj, game_api=None):
        # Позволяет модам полностью заменить поведение притяжения
        if game_api and "blackhole_attract" in game_api:
            return game_api["blackhole_attract"](self, obj, game_api)
        direction = self.pos - obj.pos
        dist = direction.length()
        if dist < self.radius * 6:
            force = self.strength * min(1, self.radius * 2 / max(dist, 1))
            obj.vel += direction.normalize() * force

    def draw(self, surface, camera_pos, game_api=None):
        # Позволяет модам полностью заменить отрисовку чёрной дыры
        if game_api and "draw_blackhole" in game_api:
            return game_api["draw_blackhole"](self, surface, camera_pos, game_api)
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        if USE_SPRITES and self.sprite:
            rect = self.sprite.get_rect(center=draw_pos)
            surface.blit(self.sprite, rect)
        else:
            t = pygame.time.get_ticks() * 0.002
            accretion_radius = int(self.radius * 0.95 + 6 * math.sin(t*2))
            accretion_surf = pygame.Surface((accretion_radius*2, accretion_radius*2), pygame.SRCALPHA)
            for j in range(8):
                color = (80+20*j, 80+10*j, 255, 30+j*18)
                pygame.draw.circle(accretion_surf, color, (accretion_radius, accretion_radius), accretion_radius-j, width=2)
            surface.blit(accretion_surf, (draw_pos.x-accretion_radius, draw_pos.y-accretion_radius), special_flags=pygame.BLEND_ADD)
            pygame.draw.circle(surface, (0, 0, 0), (int(draw_pos.x), int(draw_pos.y)), int(self.radius * 0.6))
            for i in range(8):
                angle = t + i * (math.pi / 4)
                x = int(draw_pos.x + math.cos(angle) * self.radius * 0.8)
                y = int(draw_pos.y + math.sin(angle) * self.radius * 0.8)
                pygame.draw.line(surface, (120, 120, 255, 80), (int(draw_pos.x), int(draw_pos.y)), (x, y), 2)