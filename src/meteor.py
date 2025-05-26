import pygame
import random

class Meteor:
    def __init__(self, config, center_pos):
        self.radius = random.randint(18, 32)
        self.x = center_pos.x + random.randint(-config.width // 2, config.width // 2)
        self.y = center_pos.y - config.height // 2 - self.radius  
        self.speed = random.uniform(8, 16)
        self.angle = random.uniform(-0.2, 0.2)
        self.color = (180, 180, 180)
        self.config = config

    def update(self):
        self.x += self.angle * self.speed
        self.y += self.speed

    def is_alive(self):
        return self.y - self.radius < self.config.height + 1000

    def draw(self, surface, camera_pos):
        draw_x = self.x - camera_pos.x + self.config.width // 2
        draw_y = self.y - camera_pos.y + self.config.height // 2
        pygame.draw.circle(surface, self.color, (int(draw_x), int(draw_y)), self.radius)
        pygame.draw.circle(surface, (100, 100, 100), (int(draw_x), int(draw_y)), self.radius, 2)