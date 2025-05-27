import pygame
import random
import math
import os
from bullet import Bullet
from settings import *

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")

ENEMY_TYPES = {
    "default": {"radius": 24, "speed": ENEMY_SPEED, "hp": 1, "cooldown": (60, 120)},
    "fast":    {"radius": 16, "speed": ENEMY_SPEED + 2, "hp": 1, "cooldown": (15, 40)},
    "tank":    {"radius": 36, "speed": ENEMY_SPEED * 0.6, "hp": 3, "cooldown": (120, 200)},
    "zigzag":  {"radius": 20, "speed": ENEMY_SPEED + 0.5, "hp": 1, "cooldown": (60, 120)},
}

class Enemy:
    def __init__(self, pos, config, enemy_type="default", **kwargs):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.config = config
        self.type = enemy_type
        params = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["default"])
        self.radius = kwargs.get("radius", params["radius"])
        self.speed = kwargs.get("speed", params["speed"])
        self.max_speed = kwargs.get("max_speed", self.speed + (2 if enemy_type == "fast" else 1))
        self.hp = kwargs.get("hp", params["hp"])
        self.cooldown = random.randint(*params["cooldown"])
        self.invuln_timer = 0
        self.sprite = kwargs.get("sprite", None)
        if USE_SPRITES and self.sprite is None:
            try:
                fname = f"enemy_{self.type}.png" if os.path.exists(os.path.join(ASSETS_PATH, f"enemy_{self.type}.png")) else "enemy.png"
                self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, fname)).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (self.radius*2, self.radius*2))
            except Exception as e:
                print("Не удалось загрузить спрайт врага:", e)
                self.sprite = None
        # Спец. параметры
        if self.type == "zigzag":
            self.zigzag_phase = random.uniform(0, 2 * math.pi)
            self.zigzag_ampl = random.randint(40, 80)
        self.wobble_angle = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.03, 0.07)
        self.orbit_phase = random.uniform(0, 2 * math.pi)
        self.orbit_radius = random.randint(0, 40)
        self.accel = kwargs.get("accel", 0.15 + random.uniform(0, 0.1))
        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, player_pos, enemy_bullets, camera_pos):
        to_player = player_pos - self.pos
        distance = to_player.length()
        if distance > 1:
            if self.type == "zigzag":
                self.zigzag_phase += 0.15
                perp = pygame.Vector2(-to_player.y, to_player.x).normalize()
                zigzag_offset = perp * math.sin(self.zigzag_phase) * self.zigzag_ampl
                target = player_pos + zigzag_offset
            else:
                orbit_offset = pygame.Vector2(-to_player.y, to_player.x).normalize() * math.sin(pygame.time.get_ticks() / 400 + self.orbit_phase) * self.orbit_radius
                wobble = pygame.Vector2(math.cos(self.wobble_angle), math.sin(self.wobble_angle)) * 2
                target = player_pos + orbit_offset + wobble
            desired = (target - self.pos).normalize() * self.max_speed
            steer = desired - self.vel
            if steer.length() > self.accel:
                steer.scale_to_length(self.accel)
            self.vel += steer
            if self.vel.length() > self.max_speed:
                self.vel.scale_to_length(self.max_speed)
            self.pos += self.vel
        else:
            self.vel *= 0.8

        self.cooldown -= 1
        if self.cooldown <= 0:
            direction = (player_pos - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()
                enemy_bullets.append(Bullet(self.pos, direction, ENEMY_BULLET_SPEED, RED, ENEMY_BULLET_LIFETIME, self.config, is_enemy=True))
                self.cooldown = random.randint(*ENEMY_TYPES[self.type]["cooldown"])
        if self.invuln_timer > 0:
            self.invuln_timer -= 1

    def is_hit(self, bullet):
        hit = self.pos.distance_to(bullet.pos) < (self.radius + 5)
        if not hit:
            return False
        if self.type == "tank":
            if self.invuln_timer == 0:
                self.hp -= 1
                self.invuln_timer = 15
                return self.hp <= 0
            return False
        else:
            self.hp -= 1
            return self.hp <= 0

    def draw(self, surface, camera_pos):
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        alpha = 255
        if self.invuln_timer > 0:
            alpha = int(255 * (self.invuln_timer / 15))
            alpha = max(0, min(255, alpha))
        if USE_SPRITES and self.sprite:
            image = self.sprite.copy()
            if self.invuln_timer > 0:
                image.set_alpha(alpha)
            rect = image.get_rect(center=draw_pos)
            surface.blit(image, rect)
        else:
            color = {
                "fast": (100, 255, 255),
                "tank": (180, 80, 80),
                "zigzag": (180, 255, 100),
                "default": (255, 180, 0)
            }.get(self.type, (255, 180, 0))
            pygame.draw.circle(surface, color, (int(draw_pos.x), int(draw_pos.y)), self.radius)
            pygame.draw.circle(surface, (0, 0, 0), (int(draw_pos.x), int(draw_pos.y)), self.radius, 2)
            if self.invuln_timer > 0:
                fade_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(fade_surf, (255,255,255,alpha), (self.radius, self.radius), self.radius)
                surface.blit(fade_surf, (draw_pos.x-self.radius, draw_pos.y-self.radius))