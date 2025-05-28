import pygame
import math
import os
from settings import *

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

class Player:
    def __init__(self, config, **kwargs):
        self.config = config
        self.lives = kwargs.get("lives", PLAYER_LIVES)
        self.color = kwargs.get("color", (100, 100, 255))
        self.shape = kwargs.get("shape", "triangle")
        self.shapes_points = {
            "triangle": [(20, 0), (40, 40), (20, 30), (0, 40)],
        }
        self.image_orig = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image_orig, self.color, self.shapes_points[self.shape])
        self.image = self.image_orig.copy()
        self.pos = pygame.Vector2(kwargs.get("pos", (0, 0)))
        self.vel = pygame.Vector2(0, 0)
        self.max_speed = kwargs.get("max_speed", 9)
        self.max_accel = kwargs.get("max_accel", 1.2)
        self.radius = kwargs.get("radius", 20)
        self.sprite = kwargs.get("sprite", None)
        if USE_SPRITES and self.sprite is None:
            try:
                self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, "player.png")).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (40, 40))
            except Exception as e:
                # print("Не удалось загрузить спрайт игрока:", e)
                self.sprite = None
        self.effects = kwargs.get("effects", {})  # {"shield": ticks_left, ...}
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self):
        keys = pygame.key.get_pressed()
        accel = pygame.Vector2(0, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            accel.y -= self.max_accel
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            accel.y += self.max_accel
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            accel.x -= self.max_accel
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            accel.x += self.max_accel
        if accel.length() > 0:
            accel = accel.normalize() * self.max_accel
            self.vel += accel
            if self.vel.length() > self.max_speed:
                self.vel.scale_to_length(self.max_speed)
        else:
            self.vel *= 0.8
            if self.vel.length() < 0.5:
                self.vel = pygame.Vector2(0, 0)
        self.pos += self.vel

        # Update effects
        expired = []
        for eff in self.effects:
            self.effects[eff] -= 1
            if self.effects[eff] <= 0:
                expired.append(eff)
        for eff in expired:
            del self.effects[eff]

    def has_effect(self, effect):
        return self.effects.get(effect, 0) > 0

    def apply_effect(self, effect, duration=0, **kwargs):
        """Apply any effect: shield, heal, slow, etc."""
        if effect == "heal":
            self.heal(kwargs.get("amount", 1))
        elif effect == "shield":
            self.effects["shield"] = duration
        # Моды могут добавить свои эффекты

    def take_damage(self, amount=1, source=None):
        """Universal damage handler. Returns True if damage applied."""
        if self.has_effect("shield"):
            return False
        self.lives -= amount
        if self.lives < 0:
            self.lives = 0
        self.color = PLAYER_COLORS[min(PLAYER_LIVES - 1, PLAYER_LIVES - self.lives)]
        self.image_orig.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.image_orig, self.color, [(20, 0), (40, 40), (20, 30), (0, 40)])
        return True

    def heal(self, amount=1):
        self.lives = min(self.lives + amount, PLAYER_LIVES)
        self.color = PLAYER_COLORS[min(PLAYER_LIVES - 1, PLAYER_LIVES - self.lives)]
        self.image_orig.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.image_orig, self.color, [(20, 0), (40, 40), (20, 30), (0, 40)])

    def draw(self, surface, camera_pos, mouse_pos, game_api=None):
        # Используем функцию ядра для кастомной отрисовки, если она есть
        if game_api and "draw_player" in game_api:
            return game_api["draw_player"](self, surface, camera_pos, mouse_pos)
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        mouse_world = camera_pos + pygame.Vector2(mouse_pos) - pygame.Vector2(self.config.width // 2, self.config.height // 2)
        offset = mouse_world - self.pos
        angle = -math.degrees(math.atan2(offset.y, offset.x)) - 90

        # --- Визуализация щита ---
        if self.has_effect("shield"):
            shield_alpha = 120 + int(80 * math.sin(pygame.time.get_ticks() * 0.008))
            shield_radius = int(self.radius * 1.5 + 2 * math.sin(pygame.time.get_ticks() * 0.012))
            shield_surf = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 200, 255, shield_alpha), (shield_radius, shield_radius), shield_radius, 4)
            surface.blit(shield_surf, (draw_pos.x - shield_radius, draw_pos.y - shield_radius))

        if USE_SPRITES and self.sprite:
            rotated_image = pygame.transform.rotate(self.sprite, angle)
            rect = rotated_image.get_rect(center=draw_pos)
            surface.blit(rotated_image, rect)
        else:
            temp_image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(temp_image, self.color, self.shapes_points["triangle"])
            rotated_image = pygame.transform.rotate(temp_image, angle)
            rect = rotated_image.get_rect(center=draw_pos)
            surface.blit(rotated_image, rect)