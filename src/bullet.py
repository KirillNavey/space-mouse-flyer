import pygame 
from settings import * 

class Bullet:
    def __init__(self, pos, velocity, speed, color, lifetime, config):
        self.pos = pygame.Vector2(pos)
        self.dir = velocity.normalize() 
        self.speed = speed 
        self.color = color 
        self.lifetime = lifetime 
        self.age = 0 
        self.config = config 

    def update(self): 
        self.pos += self.dir * self.speed 
        self.age += 1 

    def draw(self, surface, camera_pos): 
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)  
        pygame.draw.circle(surface, self.color, (int(draw_pos.x), int(draw_pos.y)), 5) 

    def is_alive(self): 
        return self.age < self.lifetime 