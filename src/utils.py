import pygame 
import random 
import math 
import sys 
from settings import * 
from achievements import Achievements 

def draw_background(surface, camera_pos, config):
    surface.fill((10, 10, 30)) 
    parallax_layers = [ 
        (0.2, 80), 
        (0.4, 60), 
        (0.6, 40), 
        (0.8, 30), 
        (0.95, 20) 
    ]
    for layer, num_stars in parallax_layers: 
        rng = random.Random(int(layer * 10000)) 
        for i in range(num_stars): 
            star_seed = int(layer * 10000) + i 
            star_rng = random.Random(star_seed) 
            star_x = star_rng.uniform(0, config.width) 
            star_y = star_rng.uniform(0, config.height) 
            scolor = star_rng.choice(STAR_COLORS) 
            sradius = star_rng.randint(1, 2 if layer < 0.7 else 3) 
            offset_x = (camera_pos.x * (1 - layer)) % config.width 
            offset_y = (camera_pos.y * (1 - layer)) % config.height 
            screen_x = (star_x - offset_x) % config.width 
            screen_y = (star_y - offset_y) % config.height 
            pygame.draw.circle(surface, scolor, (int(screen_x), int(screen_y)), sradius) 

def draw_enemy_indicators(surface, camera_pos, enemies, config):
    center = pygame.Vector2(config.width // 2, config.height // 2) 
    radius = min(config.width, config.height) // 2 - 40 
    
    for enemy in enemies: 
        enemy_screen = enemy.pos - camera_pos + center 
        if not (0 <= enemy_screen.x < config.width and 0 <= enemy_screen.y < config.height): 
            direction = (enemy.pos - camera_pos) 
            dist = direction.length() 
            if dist > 0: 
                direction = direction.normalize() 
                min_r, max_r = 8, 24 
                indicator_radius = max(min_r, max_r - int(dist // 300)) 
                indicator_pos = center + direction * radius 
                
                triangle_points = [ 
                    (indicator_pos.x + indicator_radius * direction.x, indicator_pos.y + indicator_radius * direction.y), 
                    (indicator_pos.x - indicator_radius * direction.y, indicator_pos.y + indicator_radius * direction.x), 
                    (indicator_pos.x + indicator_radius * direction.y, indicator_pos.y - indicator_radius * direction.x)  
                ]
                pygame.draw.polygon(surface, (255, 100, 0), triangle_points) 

def draw_lives(screen, lives, config):
    for i in range(PLAYER_LIVES): 
        color = PLAYER_COLORS[i] if i < lives else (40, 40, 40) 
        pygame.draw.circle(screen, color, (config.width - 40 - i * 40, 40), 16) 

def draw_menu(surface, text_lines, config):
    surface.fill((10, 10, 30))
    font = pygame.font.SysFont("consolas", 48)
    total_height = len(text_lines) * 60
    start_y = config.height // 2 - total_height // 2
    for i, line in enumerate(text_lines):
        surf = font.render(line, True, (255, 255, 0))
        rect = surf.get_rect(center=(config.width // 2, start_y + i * 60))
        surface.blit(surf, rect)
    pygame.display.flip()

def menu_loop(surface, lines, config, achievements):
    menu_items = []
    for line in lines:
        if "начать" in line.lower():
            menu_items.append("Начать игру")
        else:
            menu_items.append(line)
    menu_items += ["Сбросить прогресс", "Выйти"]
    selected = 0
    font = pygame.font.SysFont("consolas", 48)
    total_height = len(menu_items) * 60
    start_y = config.height // 2 - total_height // 2
    while True:
        surface.fill((10, 10, 30))
        for i, line in enumerate(menu_items):
            color = (255, 255, 0) if i == selected else (180, 180, 180)
            surf = font.render(line, True, color)
            rect = surf.get_rect(center=(config.width // 2, start_y + i * 60))
            surface.blit(surf, rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(menu_items)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(menu_items)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if menu_items[selected] == "Начать игру":
                        return "start"
                    elif menu_items[selected] == "Сбросить прогресс":
                        achievements.reset()
                        font2 = pygame.font.SysFont("consolas", 36)
                        surf2 = font2.render("Прогресс сброшен!", True, (255, 255, 0))
                        rect2 = surf2.get_rect(center=(config.width // 2, config.height // 2 + 200))
                        surface.blit(surf2, rect2)
                        pygame.display.flip()
                        pygame.time.delay(1200)
                    elif menu_items[selected] == "Выйти":
                        return "exit"
                    else:
                        return
                if event.key in (pygame.K_ESCAPE,):
                    return

def select_difficulty(surface, config, current_difficulty):
    options = [
        "Легко",
        "Средне",
        "Сложно"
    ]
    selected = current_difficulty - 1 if 0 <= current_difficulty - 1 < len(options) else 0
    font = pygame.font.SysFont("consolas", 48)
    title_font = pygame.font.SysFont("consolas", 56, bold=True)
    while True:
        surface.fill((10, 10, 30))
        title = title_font.render("Выберите сложность", True, (255, 255, 0))
        surface.blit(title, (config.width // 2 - title.get_width() // 2, config.height // 2 - 160))
        total_height = len(options) * 60
        start_y = config.height // 2 - total_height // 2
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (180, 180, 180)
            surf = font.render(opt, True, color)
            rect = surf.get_rect(center=(config.width // 2, start_y + i * 60))
            surface.blit(surf, rect)
        hint_font = pygame.font.SysFont("consolas", 28)
        hint = hint_font.render("Навигация: стрелки/W/S  |  Выбор: ENTER/SPACE", True, (180, 180, 180))
        surface.blit(hint, (config.width // 2 - hint.get_width() // 2, config.height // 2 + 120))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected + 1
                if event.key == pygame.K_ESCAPE:
                    return current_difficulty