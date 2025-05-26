import sys
import os

import pygame 
import random 
import math 
from player import Player 
from bullet import Bullet 
from enemy import Enemy 
from achievements import Achievements 
from bonus import Bonus 
from explosion import Explosion 
from meteor import Meteor 
from blackhole import BlackHole 
from camera import Camera 
from utils import draw_background, draw_enemy_indicators, draw_lives, draw_menu, menu_loop, select_difficulty 
from settings import * 

import importlib.util

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")
MODS_PATH = os.path.join(os.path.dirname(__file__), "..", "mods")
loaded_mods = []

def load_mods():
    if not os.path.exists(MODS_PATH):
        os.makedirs(MODS_PATH)
    for fname in os.listdir(MODS_PATH):
        if fname.endswith(".py"):
            mod_path = os.path.join(MODS_PATH, fname)
            mod_name = os.path.splitext(fname)[0]
            spec = importlib.util.spec_from_file_location(mod_name, mod_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                    loaded_mods.append(mod)
                    print(f"Мод '{mod_name}' загружен.")
                except Exception as e:
                    print(f"Ошибка загрузки мода '{mod_name}': {e}")

load_mods()

pygame.init() 
pygame.mixer.init() 

shoot_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "shoot.mp3"))
hit_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "hit.mp3"))
player_hit_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "player_hit.mp3"))
achievement_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "achievement.mp3"))
levelup_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "level_up.mp3"))
death_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "death.mp3"))
bonus_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", "bonus.mp3"))

shoot_sound.set_volume(0.5) 
hit_sound.set_volume(0.5) 
player_hit_sound.set_volume(0.5) 
achievement_sound.set_volume(0.5) 
levelup_sound.set_volume(0.5) 
death_sound.set_volume(0.5) 
bonus_sound.set_volume(0.5) 

info = pygame.display.Info() 
WIDTH, HEIGHT = info.current_w, info.current_h 
config = GameConfig(WIDTH, HEIGHT) 
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) 
pygame.display.set_caption("Space Mouse Flyer") 
clock = pygame.time.Clock() 
pygame.mouse.set_visible(False) 

enemy_types = ["default", "fast", "tank", "zigzag"] 
event_timer = random.randint(1200, 2000)  
event_active = None
meteors = []
blackholes = []
event_duration = 0
virtual_cursor = pygame.Vector2(WIDTH // 2, HEIGHT // 2) 
score = 0 
current_level = 1 
kills_for_next_level = LEVEL_UP_KILLS 
current_difficulty = 1 
game_state = "menu" 
player = Player(config) 
camera_pos = pygame.Vector2(0, 0) 
bullets = [] 
enemy_bullets = [] 
enemies = [] 
enemy_spawn_timer = ENEMY_SPAWN_TIME 
total_enemies = 0 
game_time = 0 
bonuses = [] 
shield_timer = 0 
explosions = [] 
blackhole_damage_timer = 0

achievements = Achievements(config) 
achievements.load() 

camera = Camera(player.pos)

game_api = {
    "player": player,
    "enemies": enemies,
    "bullets": bullets,
    "enemy_bullets": enemy_bullets,
    "bonuses": bonuses,
    "config": config,
    "score": lambda: score,
    "add_enemy": lambda obj: enemies.append(obj),
    "add_bonus": lambda obj: bonuses.append(obj),
    "add_bullet": lambda obj: bullets.append(obj),
    "add_enemy_bullet": lambda obj: enemy_bullets.append(obj),
    "remove_enemy": lambda obj: enemies.remove(obj) if obj in enemies else None,
    "remove_bullet": lambda obj: bullets.remove(obj) if obj in bullets else None,
    "remove_enemy_bullet": lambda obj: enemy_bullets.remove(obj) if obj in enemy_bullets else None,
    "remove_bonus": lambda obj: bonuses.remove(obj) if obj in bonuses else None,
    "spawn_enemy": lambda pos, etype="default": enemies.append(Enemy(pos, config, etype)),
    "spawn_bonus": lambda pos, btype=None: bonuses.append(Bonus(pos, config)) if btype is None else bonuses.append(Bonus(pos, config, btype)),
    "spawn_explosion": lambda pos, color=(255,200,50), type="big": explosions.append(Explosion(pos, color, type)),
    "give_damage": lambda amount=1: player.take_damage() if amount > 0 else None,
    "heal_player": lambda: player.heal(),
    "camera": camera,
    "sounds": {
        "shoot": shoot_sound,
        "hit": hit_sound,
        "player_hit": player_hit_sound,
        "achievement": achievement_sound,
        "levelup": levelup_sound,
        "death": death_sound,
        "bonus": bonus_sound,
    },
    "achievements": achievements,
    "events": [],
    "on_tick": [],
    "set_game_state": lambda state: globals().__setitem__('game_state', state),
    "get_game_state": lambda: game_state,
    "set_score": lambda val: globals().__setitem__('score', val),
    "get_score": lambda: score,
    "set_level": lambda val: globals().__setitem__('current_level', val),
    "get_level": lambda: current_level,
    
}

for mod in loaded_mods:
    if hasattr(mod, "apply_mod"):
        try:
            mod.apply_mod(game_api)
        except Exception as e:
            print(f"Ошибка применения мода {mod}: {e}")

while True:
    if game_state == "menu":
        menu_result = menu_loop(screen, [
            "Space Mouse Flyer",
            "",
            "Начать игру",
            "Пауза — ESC",
            "Выход — M",
            "Управление: стрелки/WASD, мышь, ЛКМ — выстрел",
            "",
            "Навигация: стрелки/W/S  |  Выбор: ENTER/SPACE"
        ], config, achievements)
        if menu_result == "start":
            current_difficulty = select_difficulty(screen, config, current_difficulty)
            player = Player(config)
            camera_pos = pygame.Vector2(0, 0)
            bullets = []
            enemy_bullets = []
            enemies = []
            ENEMY_SPAWN_TIME = DIFFICULTY_LEVELS[current_difficulty - 1]["enemy_spawn"]
            MAX_ENEMIES = DIFFICULTY_LEVELS[current_difficulty - 1]["max_enemies"]
            ENEMY_SPEED = DIFFICULTY_LEVELS[current_difficulty - 1]["enemy_speed"]
            enemy_spawn_timer = ENEMY_SPAWN_TIME
            score = 0
            total_enemies = 0
            game_time = 0
            game_state = "game"
            continue
        elif menu_result == "exit":
            pygame.quit()
            sys.exit()
        continue

    if game_state == "pause":
        menu_loop(screen, [
            "Пауза",
            f"Счет: {score}",
            f"Уровень: {current_level}",
            f"Врагов уничтожено: {achievements.stats['enemies_killed']}",
            f"Время: {int(game_time)} сек",
            "",
            "Продолжить — ENTER/SPACE/ESC",
            "Выйти — M",
            "",
            "Навигация: стрелки/W/S  |  Выбор: ENTER/SPACE"
        ], config, achievements)
        game_state = "game"
        continue

    if game_state == "dead":
        achievements.save()
        death_sound.play()
        menu_loop(screen, [
            "Игра окончена",
            f"Ваш счет: {score}",
            f"Врагов уничтожено: {total_enemies}",
            f"Время: {int(game_time)} сек",
            "",
            "В меню — ENTER/SPACE/ESC",
            "Выйти — M",
            "",
            "Навигация: стрелки/W/S  |  Выбор: ENTER/SPACE"
        ], config, achievements)
        game_state = "menu"
        continue

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            pygame.quit() 
            sys.exit() 
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE: 
                game_state = "pause" 
            if event.key == pygame.K_m: 
                pygame.quit() 
                sys.exit() 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.lives > 0:
            mouse_pos = pygame.mouse.get_pos()
            screen_center = pygame.Vector2(config.width // 2, config.height // 2)
            mouse_offset = pygame.Vector2(mouse_pos) - screen_center
            mouse_world = player.pos + mouse_offset
            direction = mouse_world - player.pos
            if direction.length() > 0:
                
                bullet_color = player.color
                bullet_velocity = direction.normalize() * BULLET_SPEED - player.vel * 0.35
                bullets.append(Bullet(player.pos, bullet_velocity, bullet_velocity.length(), bullet_color, BULLET_LIFETIME, config))
                player.vel -= direction.normalize() * 4
                shoot_sound.play()
            camera.kickback(-direction.normalize() * 12)
            achievements.stats["shots_fired"] += 1

    pygame.mouse.set_visible(True) 
    player.update() 
    camera.update(player.pos)
    camera_pos = camera.get()

    game_time += clock.get_time() / 1000 
    achievements.stats["time_survived"] = int(game_time) 

    if achievements.stats["enemies_killed"] >= kills_for_next_level:
        current_level += 1
        kills_for_next_level += LEVEL_UP_KILLS
        achievements.stats["levels_completed"] = current_level
        ENEMY_SPAWN_TIME = max(30, ENEMY_SPAWN_TIME - 10)
        MAX_ENEMIES += 2
        levelup_sound.play()  
        achievements.show_popup(f"Уровень {current_level}!")

    enemy_spawn_timer -= 1 
    if enemy_spawn_timer <= 0 and len(enemies) < MAX_ENEMIES: 
        angle = random.uniform(0, 2 * math.pi) 
        dist = random.randint(600, 1200) 
        enemy_pos = player.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * dist 
        enemy_type = random.choices(enemy_types, weights=[0.5, 0.2, 0.15, 0.15])[0]
        enemies.append(Enemy(enemy_pos, config, enemy_type))
        total_enemies += 1 
        enemy_spawn_timer = ENEMY_SPAWN_TIME 

    enemies = [enemy for enemy in enemies if enemy.pos.distance_to(player.pos) < 2500] 

    for enemy in enemies: 
        enemy.update(player.pos, enemy_bullets, camera_pos) 

    for bullet in bullets[:]:
        bullet.update()
        if not bullet.is_alive():
            explosions.append(Explosion(bullet.pos, color=(180, 180, 255), type="small"))
            bullets.remove(bullet)
        else:
            for enemy in enemies[:]:
                if enemy.is_hit(bullet):
                    
                    if enemy.type == "fast":
                        exp_color = (100, 255, 255)
                    elif enemy.type == "tank":
                        exp_color = (180, 80, 80)
                    elif enemy.type == "zigzag":
                        exp_color = (180, 255, 100)
                    else:
                        exp_color = (255, 180, 0)
                    explosions.append(Explosion(enemy.pos, color=exp_color, type="big"))
                    enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 1
                    
                    achievements.stats["enemies_killed"] += 1
                    if enemy.type == "tank":
                        achievements.stats["tank_kills"] += 1
                    elif enemy.type == "fast":
                        achievements.stats["fast_kills"] += 1
                    elif enemy.type == "zigzag":
                        achievements.stats["zigzag_kills"] += 1
                    
                    now = pygame.time.get_ticks()
                    if now - achievements.stats["last_kill_time"] < 5000:
                        achievements.stats["combo_counter"] += 1
                    else:
                        achievements.stats["combo_counter"] = 1
                    achievements.stats["last_kill_time"] = now
                    achievements.stats["enemies_killed"] += 1
                    achievements.stats["shots_hit"] += 1
                    hit_sound.play()  
                    if random.random() < 0.2:  
                        bonuses.append(Bonus(enemy.pos, config))
                    break

    for bullet in enemy_bullets[:]:
        bullet.update()
        if not bullet.is_alive():
            explosions.append(Explosion(bullet.pos, color=RED, type="small"))
            enemy_bullets.remove(bullet)  
        elif bullet.pos.distance_to(player.pos) < (player.radius + 5) and player.lives > 0:
            enemy_bullets.remove(bullet)
            if shield_timer > 0:
                
                pass
            else:
                player.take_damage()
                camera.shake(strength=24, duration=18)
                achievements.stats["damage_taken"] += 1
                explosions.append(Explosion(player.pos, color=(255, 80, 80), type="hollow"))
                player_hit_sound.play()
                if player.lives == 0:
                    game_state = "dead"
    
    for bonus in bonuses[:]:
        bonus.update()
        if not bonus.is_alive():
            bonuses.remove(bonus)
        elif player.pos.distance_to(bonus.pos) < (player.radius + bonus.radius):
            if bonus.type == "heal" and player.lives < PLAYER_LIVES:
                player.heal()
                achievements.stats["heal_collected"] += 1
            elif bonus.type == "shield":
                shield_timer = 300  
                achievements.stats["shield_collected"] += 1
            explosions.append(Explosion(bonus.pos, color=(100, 200, 255) if bonus.type == "shield" else (100, 255, 100), type="hollow"))
            bonus_sound.play()  
            achievements.stats["bonuses_collected"] += 1
            camera.shake(strength=10, duration=10)
            bonuses.remove(bonus)

    for explosion in explosions[:]:
        explosion.update()
        if not explosion.is_alive():
            explosions.remove(explosion)
        if (explosion.pos - player.pos).length() < 120:
            camera.shake(strength=14, duration=10)

    achievements.check(score, game_time, player, screen, achievement_sound) 

    draw_background(screen, camera_pos, config) 
    for bonus in bonuses:
        bonus.draw(screen, camera_pos)
    for explosion in explosions:
        explosion.draw(screen, camera_pos, config)
    player.draw(screen, camera_pos, pygame.mouse.get_pos()) 
    if shield_timer > 0:
        draw_pos = player.pos - camera_pos + pygame.Vector2(config.width // 2, config.height // 2)
        pygame.draw.circle(screen, (100, 200, 255), (int(draw_pos.x), int(draw_pos.y)), player.radius + 12, 4)
    for enemy in enemies: 
        enemy.draw(screen, camera_pos) 
    for bullet in bullets: 
        bullet.draw(screen, camera_pos) 
    for bullet in enemy_bullets: 
        bullet.draw(screen, camera_pos) 
    draw_enemy_indicators(screen, camera_pos, enemies, config) 
    draw_lives(screen, player.lives, config) 
    achievements.draw_stats(screen) 
    achievements.draw_achievements(screen) 
    if event_active == "meteor":
        font = pygame.font.SysFont("consolas", 36)
        surf = font.render("МЕТЕОРИТНЫЙ ДОЖДЬ!", True, (200, 200, 200))
        screen.blit(surf, (config.width // 2 - surf.get_width() // 2, 80))
    elif event_active == "blackhole":
        font = pygame.font.SysFont("consolas", 36)
        surf = font.render("ЧЕРНАЯ ДЫРА!", True, (80, 80, 255))
        screen.blit(surf, (config.width // 2 - surf.get_width() // 2, 80))

    font = pygame.font.SysFont("consolas", 36) 
    total_surf = font.render(f"Enemies: {len(enemies)}", True, (255, 180, 0)) 
    total_surf.set_alpha(200) 
    screen.blit(total_surf, (30, 30)) 

    if shield_timer > 0:
        draw_pos = player.pos - camera_pos + pygame.Vector2(config.width // 2, config.height // 2)
        
        pygame.draw.circle(screen, (100, 200, 255), (int(draw_pos.x), int(draw_pos.y)), player.radius + 12, 4)
        
        shield_max = 300  
        shield_angle = (shield_timer / shield_max) * 360
        dark_color = (40, 80, 120)
        rect = pygame.Rect(0, 0, (player.radius + 16) * 2, (player.radius + 16) * 2)
        rect.center = (int(draw_pos.x), int(draw_pos.y))
        
        pygame.draw.arc(
            screen,
            dark_color,
            rect,
            math.radians(-90),
            math.radians(-90 + shield_angle),
            8
        )
        shield_timer -= 1

    if not event_active:
        event_timer -= 1
        if event_timer <= 0:
            event_active = random.choice(["meteor", "blackhole", "speedwave"])
            if event_active == "meteor":
                event_duration = 240  
                meteors.clear()
            elif event_active == "blackhole":
                event_duration = 600  
                blackholes.append(BlackHole(
                    player.pos + pygame.Vector2(random.randint(-600, 600), random.randint(-400, 400)), config))
            elif event_active == "speedwave":
                event_duration = 300  
                for enemy in enemies:
                    enemy.max_speed *= 1.8
    else:
        event_duration -= 1
        
        if event_active == "meteor" and event_duration <= 0 and player.lives > 0:
            achievements.stats["survived_meteor"] = True
        if event_active == "meteor":
            if random.random() < 0.18:
                meteors.append(Meteor(config, player.pos))
            for meteor in meteors[:]:
                meteor.update()
                meteor.draw(screen, camera_pos)
                
                if player.pos.distance_to(pygame.Vector2(meteor.x, meteor.y)) < (player.radius + meteor.radius):
                    player.take_damage()
                    explosions.append(Explosion(player.pos, color=(200, 200, 200), type="hollow"))
                    meteors.remove(meteor)
                elif not meteor.is_alive():
                    meteors.remove(meteor)
        
        if event_active == "blackhole" and event_duration <= 0 and player.lives > 0:
            achievements.stats["survived_blackhole"] = True
        if event_active == "blackhole":
            for bh in blackholes[:]:
                bh.update()
                bh.draw(screen, camera_pos)
                bh.attract(player.pos, player.vel)
                for enemy in enemies:
                    bh.attract(enemy.pos, enemy.vel)
                
                for bullet in bullets[:]:
                    bh.attract(bullet.pos, bullet.dir)
                    if bullet.pos.distance_to(bh.pos) < bh.radius * 0.5:
                        explosions.append(Explosion(bullet.pos, color=(80, 80, 255), type="small"))
                        bullets.remove(bullet)
                for bullet in enemy_bullets[:]:
                    bh.attract(bullet.pos, bullet.dir)
                    if bullet.pos.distance_to(bh.pos) < bh.radius * 0.5:
                        explosions.append(Explosion(bullet.pos, color=(80, 80, 255), type="small"))
                        enemy_bullets.remove(bullet)
                
                if player.pos.distance_to(bh.pos) < bh.radius * 0.7:
                    if blackhole_damage_timer <= 0 and player.lives > 0:
                        player.take_damage()
                        explosions.append(Explosion(player.pos, color=(80, 80, 255), type="hollow"))
                        player_hit_sound.play()
                        blackhole_damage_timer = 30  
            blackholes = [bh for bh in blackholes if bh.is_alive()]
        
        elif event_active == "speedwave":
            font = pygame.font.SysFont("consolas", 36)
            surf = font.render("ВНИМАНИЕ: ВРАГИ УСКОРЕНЫ!", True, (255, 80, 80))
            screen.blit(surf, (config.width // 2 - surf.get_width() // 2, 120))
        
        if event_duration <= 0:
            if event_active == "speedwave":
                for enemy in enemies:
                    enemy.max_speed /= 1.8
            event_active = None
            event_timer = random.randint(1200, 2000)
            meteors.clear()
            blackholes.clear()
        if blackhole_damage_timer > 0:
            blackhole_damage_timer -= 1

    achievements.update_popups()
    achievements.draw_popups(screen)

    pygame.display.flip() 
    clock.tick(60) 