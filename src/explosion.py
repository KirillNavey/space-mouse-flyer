import pygame
import random

class Explosion:
    def __init__(self, pos, color=(255, 200, 50), type="big", game_api=None, **kwargs):
        self.pos = pygame.Vector2(pos)
        self.type = type
        self.color = color
        self.age = 0
        # Моды могут задать свои параметры через kwargs
        if type == "big":
            self.frames = kwargs.get("frames", 22)
            self.radius = kwargs.get("radius", 18 + random.randint(0, 8))
            self.max_radius = kwargs.get("max_radius", self.radius + 38 + random.randint(0, 12))
        elif type == "small":
            self.frames = kwargs.get("frames", 10)
            self.radius = kwargs.get("radius", 7 + random.randint(0, 3))
            self.max_radius = kwargs.get("max_radius", self.radius + 12 + random.randint(0, 4))
        elif type == "hollow":
            self.frames = kwargs.get("frames", 18)
            self.radius = kwargs.get("radius", 32)
            self.min_radius = kwargs.get("min_radius", 8)
        else:
            self.frames = kwargs.get("frames", 16)
            self.radius = kwargs.get("radius", 12)
            self.max_radius = kwargs.get("max_radius", self.radius + 20)
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, game_api=None):
        self.age += 1

    def is_alive(self, game_api=None):
        return self.age < self.frames

    def draw(self, surface, camera_pos, config, game_api=None):
        # Позволяет модам полностью заменить отрисовку взрыва
        if game_api and "draw_explosion" in game_api:
            return game_api["draw_explosion"](self, surface, camera_pos, config)
        draw_pos = self.pos - camera_pos + pygame.Vector2(config.width // 2, config.height // 2)
        if self.type == "hollow":
            progress = self.age / self.frames
            radius = int(self.radius - (self.radius - self.min_radius) * progress)
            alpha = max(0, 180 - int(180 * progress))
            surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.radius, self.radius), radius, 5)
            surface.blit(surf, (draw_pos.x - self.radius, draw_pos.y - self.radius))
        else:
            progress = self.age / self.frames
            radius = int(self.radius + (self.max_radius - self.radius) * progress)
            alpha = max(0, 255 - int(255 * progress))
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (radius, radius), radius)
            surface.blit(surf, (draw_pos.x - radius, draw_pos.y - radius))