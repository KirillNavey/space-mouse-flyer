import pygame
import random
import math

class BlackHole:
    def __init__(self, pos, config):
        self.pos = pygame.Vector2(pos)
        self.radius = random.randint(60, 90)
        self.strength = random.uniform(0.7, 1.2)
        self.age = 0
        self.max_age = 900  
        self.config = config

    def update(self):
        self.age += 1

    def is_alive(self):
        return self.age < self.max_age

    def attract(self, obj_pos, obj_vel):
        direction = self.pos - obj_pos
        dist = direction.length()
        if dist < self.radius * 6:
            force = self.strength * min(1, self.radius * 2 / max(dist, 1))
            obj_vel += direction.normalize() * force

    def draw(self, surface, camera_pos):
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        for i in range(3):
            pygame.draw.circle(surface, (40, 40, 80), (int(draw_pos.x), int(draw_pos.y)), int(self.radius * (1 - i * 0.2)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(draw_pos.x), int(draw_pos.y)), int(self.radius * 0.6))