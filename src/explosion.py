import pygame
import random

class Explosion:
    def __init__(self, pos, color=(255, 200, 50), type="big"):
        self.pos = pygame.Vector2(pos)
        self.type = type
        self.color = color
        self.age = 0
        if type == "big":
            self.frames = 22
            self.radius = 18 + random.randint(0, 8)
            self.max_radius = self.radius + 38 + random.randint(0, 12)
        elif type == "small":
            self.frames = 10
            self.radius = 7 + random.randint(0, 3)
            self.max_radius = self.radius + 12 + random.randint(0, 4)
        elif type == "hollow":
            self.frames = 18
            self.radius = 32
            self.min_radius = 8
        else:
            self.frames = 16
            self.radius = 12
            self.max_radius = self.radius + 20

    def update(self):
        self.age += 1

    def is_alive(self):
        return self.age < self.frames

    def draw(self, surface, camera_pos, config):
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