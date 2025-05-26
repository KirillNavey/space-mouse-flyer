import pygame
import math
from settings import *

class Player:
    def __init__(self, config):
        self.config = config
        self.lives = PLAYER_LIVES
        self.color = (100, 100, 255)
        self.shape = "triangle"
        self.shapes_points = {
            "triangle": [(20, 0), (40, 40), (20, 30), (0, 40)],
        }
        self.image_orig = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image_orig, self.color, self.shapes_points[self.shape])
        self.image = self.image_orig.copy()
        self.pos = pygame.Vector2(0, 0)
        self.vel = pygame.Vector2(0, 0)
        self.max_speed = 9
        self.max_accel = 1.2
        self.radius = 20

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

    def take_damage(self):
        if self.lives > 0: 
            self.lives -= 1 
        if self.lives < 1: 
            self.lives = 0 
        self.color = PLAYER_COLORS[min(PLAYER_LIVES - 1, PLAYER_LIVES - self.lives)] 
        self.image_orig.fill((0, 0, 0, 0)) 
        pygame.draw.polygon(self.image_orig, self.color, [(20, 0), (40, 40), (20, 30), (0, 40)]) 

    def draw(self, surface, camera_pos, mouse_pos):
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        
        mouse_world = camera_pos + pygame.Vector2(mouse_pos) - pygame.Vector2(self.config.width // 2, self.config.height // 2)
        offset = mouse_world - self.pos
        angle = -math.degrees(math.atan2(offset.y, offset.x)) - 90
        rotated_image = pygame.transform.rotate(self.image_orig, angle)
        rect = rotated_image.get_rect(center=draw_pos)
        surface.blit(rotated_image, rect)
    
    def heal(self):
        if self.lives < PLAYER_LIVES:
            self.lives += 1
            self.color = PLAYER_COLORS[min(PLAYER_LIVES - 1, PLAYER_LIVES - self.lives)]
            self.image_orig.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image_orig, self.color, [(20, 0), (40, 40), (20, 30), (0, 40)])