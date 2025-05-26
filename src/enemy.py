import pygame
import random
import math
from bullet import Bullet
from settings import *

class Enemy:
    def __init__(self, pos, config, enemy_type="default"):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.config = config
        self.type = enemy_type
        
        self.radius = 24
        self.speed = ENEMY_SPEED
        self.cooldown = random.randint(30, 90)
        self.max_speed = self.speed + random.uniform(0, 1.2)
        self.hp = 1
        
        if self.type == "fast":
            self.radius = 16
            self.speed = ENEMY_SPEED + 2
            self.max_speed = self.speed + 2
            self.cooldown = random.randint(20, 50)
        elif self.type == "tank":
            self.radius = 36
            self.speed = ENEMY_SPEED * 0.6
            self.max_speed = self.speed + 0.5
            self.cooldown = random.randint(90, 160)
            self.hp = 3
        elif self.type == "zigzag":
            self.radius = 20
            self.speed = ENEMY_SPEED + 0.5
            self.max_speed = self.speed + 1
            self.zigzag_phase = random.uniform(0, 2 * math.pi)
            self.zigzag_ampl = random.randint(40, 80)
        
        self.wobble_angle = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.03, 0.07)
        self.orbit_phase = random.uniform(0, 2 * math.pi)
        self.orbit_radius = random.randint(0, 40)
        self.accel = 0.15 + random.uniform(0, 0.1)

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
                enemy_bullets.append(Bullet(self.pos, direction, ENEMY_BULLET_SPEED, RED, ENEMY_BULLET_LIFETIME, self.config))
                if self.type == "tank":
                    self.cooldown = random.randint(120, 200)
                elif self.type == "fast":
                    self.cooldown = random.randint(15, 40)
                else:
                    self.cooldown = random.randint(60, 120)

    def is_hit(self, bullet):
        if self.type == "tank":
            self.hp -= 1
            return self.hp <= 0 and self.pos.distance_to(bullet.pos) < (self.radius + 5)
        return self.pos.distance_to(bullet.pos) < (self.radius + 5)

    def draw(self, surface, camera_pos):
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        
        if self.type == "fast":
            color = (100, 255, 255)
        elif self.type == "tank":
            color = (180, 80, 80)
        elif self.type == "zigzag":
            color = (180, 255, 100)
        else:
            color = (255, 180, 0)
        pygame.draw.circle(surface, color, (int(draw_pos.x), int(draw_pos.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(draw_pos.x), int(draw_pos.y)), self.radius, 2)