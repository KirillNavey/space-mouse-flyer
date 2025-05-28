import pygame
import random
import math
import os
from settings import *

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")
BONUS_TYPES = ["heal", "shield"]

class Bonus:
    def __init__(self, pos, config, bonus_type=None, game_api=None, **kwargs):
        self.pos = pygame.Vector2(pos)
        self.radius = kwargs.get("radius", 18)
        self.type = bonus_type if bonus_type else kwargs.get("type", random.choice(BONUS_TYPES))
        self.config = config
        self.lifetime = kwargs.get("lifetime", 600)
        self.sprite = kwargs.get("sprite", None)
        self.pulse_phase = 0
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)
        if USE_SPRITES and self.sprite is None:
            try:
                fname = f"bonus_{self.type}.png"
                path = os.path.join(ASSETS_PATH, fname)
                if not os.path.exists(path):
                    path = os.path.join(ASSETS_PATH, "bonus.png")
                self.sprite = pygame.image.load(path).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (self.radius*2, self.radius*2))
            except Exception as e:
                # print("Не удалось загрузить спрайт бонуса:", e)
                self.sprite = None

    def update(self, player=None, game_api=None):
        self.lifetime -= 1
        if player:
            dist = self.pos.distance_to(player.pos)
            attract_dist = player.radius * 2
            if dist < attract_dist * 2.2:
                direction = (player.pos - self.pos)
                if direction.length() > 0:
                    direction = direction.normalize()
                    strength = 0.8 + 2.5 * max(0, (attract_dist * 2.2 - dist) / (attract_dist * 2.2))
                    self.pos += direction * strength
        self.pulse_phase += 0.18

    def is_alive(self, game_api=None):
        return self.lifetime > 0

    def draw(self, surface, camera_pos, player=None, game_api=None):
        # Позволяет модам полностью заменить отрисовку бонуса
        if game_api and "draw_bonus" in game_api:
            return game_api["draw_bonus"](self, surface, camera_pos, player, game_api)
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        pulse = 1.0
        if player:
            dist = self.pos.distance_to(player.pos)
            attract_dist = player.radius * 2
            if dist < attract_dist * 2.2:
                pulse = 1.0 + 0.18 * math.sin(self.pulse_phase * 2)
        r = int(self.radius * pulse)
        if USE_SPRITES and self.sprite:
            image = pygame.transform.smoothscale(self.sprite, (r*2, r*2))
            rect = image.get_rect(center=draw_pos)
            surface.blit(image, rect)
        else:
            color = (100, 255, 100) if self.type == "heal" else (100, 200, 255)
            pygame.draw.circle(surface, color, (int(draw_pos.x), int(draw_pos.y)), r)
            if self.type == "heal":
                pygame.draw.line(surface, (255,255,255), (int(draw_pos.x)-8, int(draw_pos.y)), (int(draw_pos.x)+8, int(draw_pos.y)), 3)
                pygame.draw.line(surface, (255,255,255), (int(draw_pos.x), int(draw_pos.y)-8), (int(draw_pos.x), int(draw_pos.y)+8), 3)
            else:
                pygame.draw.circle(surface, (255,255,255), (int(draw_pos.x), int(draw_pos.y)), r-4, 2)