import pygame
import random
import math

class Camera:
    def __init__(self, start_pos, game_api=None, **kwargs):
        self.pos = pygame.Vector2(start_pos)
        self.target = pygame.Vector2(start_pos)
        self.shake_timer = 0
        self.shake_strength = 0
        self.shake_offset = pygame.Vector2(0, 0)
        self.kick = pygame.Vector2(0, 0)
        self.kick_decay = kwargs.get("kick_decay", 0.85)
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, player_pos, game_api=None):
        # Позволяет модам полностью заменить поведение камеры
        if game_api and "update_camera" in game_api:
            return game_api["update_camera"](self, player_pos, game_api)
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

    def get(self, game_api=None):
        return self.pos + self.shake_offset

    def shake(self, strength=16, duration=12, game_api=None):
        self.shake_strength = strength
        self.shake_timer = duration

    def kickback(self, vec, game_api=None):
        self.kick += vec * 0.7