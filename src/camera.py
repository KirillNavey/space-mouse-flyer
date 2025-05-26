import pygame
import random
import math

class Camera:
    def __init__(self, start_pos):
        self.pos = pygame.Vector2(start_pos)
        self.target = pygame.Vector2(start_pos)
        self.shake_timer = 0
        self.shake_strength = 0
        self.shake_offset = pygame.Vector2(0, 0)
        self.kick = pygame.Vector2(0, 0)
        self.kick_decay = 0.85

    def update(self, player_pos):
        self.target = pygame.Vector2(player_pos)
        self.pos += (self.target - self.pos) * 0.12 + self.kick
        self.kick *= self.kick_decay
        if self.shake_timer > 0:
            angle = random.uniform(0, 2 * math.pi)
            strength = self.shake_strength * (self.shake_timer / 20)
            self.shake_offset = pygame.Vector2(math.cos(angle), math.sin(angle)) * strength
            self.shake_timer -= 1
        else:
            self.shake_offset = pygame.Vector2(0, 0)

    def get(self):
        return self.pos + self.shake_offset

    def shake(self, strength=16, duration=12):
        self.shake_strength = strength
        self.shake_timer = duration

    def kickback(self, vec):
        self.kick += vec * 0.7