import pygame
import random
import math
import sys
from settings import *

def draw_background(surface, camera_pos, config, game_api=None):
    if game_api and "draw_background" in game_api and game_api["draw_background"] is not draw_background:
        return game_api["draw_background"](surface, camera_pos, config, game_api)
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

def draw_enemy_indicators(surface, camera_pos, enemies, config, game_api=None):
    if game_api and "draw_enemy_indicators" in game_api and game_api["draw_enemy_indicators"] is not draw_enemy_indicators:
        return game_api["draw_enemy_indicators"](surface, camera_pos, enemies, config, game_api)
    center = pygame.Vector2(config.width // 2, config.height // 2)
    radius = min(config.width, config.height) // 2 - 40
    for enemy in enemies:
        # Используем кастомный draw, если есть
        if hasattr(enemy, "draw") and hasattr(enemy.draw, "__call__") and hasattr(enemy, "config"):
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

def draw_lives(screen, lives, config, game_api=None):
    if game_api and "draw_lives" in game_api and game_api["draw_lives"] is not draw_lives:
        return game_api["draw_lives"](screen, lives, config, game_api)
    for i in range(PLAYER_LIVES):
        color = PLAYER_COLORS[i] if i < lives else (40, 40, 40)
        x = config.width - 40 - i * 40
        pygame.draw.circle(screen, color, (x, 40), 16)

def draw_menu(surface, text_lines, config, game_api=None):
    if game_api and "draw_menu" in game_api and game_api["draw_menu"] is not draw_menu:
        return game_api["draw_menu"](surface, text_lines, config, game_api)
    surface.fill((10, 10, 30))
    font = pygame.font.SysFont("consolas", 48)
    total_height = len(text_lines) * 60
    start_y = config.height // 2 - total_height // 2
    for i, line in enumerate(text_lines):
        surf = font.render(line, True, (255, 255, 0))
        rect = surf.get_rect(center=(config.width // 2, start_y + i * 60))
        surface.blit(surf, rect)
    pygame.display.flip()

def menu_loop(surface, lines, config, achievements, game_api=None):
    if game_api and "menu_loop" in game_api and game_api["menu_loop"] is not menu_loop:
        return game_api["menu_loop"](surface, lines, config, achievements, game_api)
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

def select_difficulty(surface, config, current_difficulty, game_api=None):
    if game_api and "select_difficulty" in game_api and game_api["select_difficulty"] is not select_difficulty:
        return game_api["select_difficulty"](surface, config, current_difficulty, game_api)
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

def draw_event_banner(surface, event_name, config, game_api=None):
    if game_api and "draw_event_banner" in game_api and game_api["draw_event_banner"] is not draw_event_banner:
        return game_api["draw_event_banner"](surface, event_name, config, game_api)
    if not event_name:
        return
    font = pygame.font.SysFont("arial", 36, bold=True)
    text = font.render(event_name, True, (255, 255, 80))
    rect = text.get_rect(center=(config.width // 2, 32))
    pygame.draw.rect(surface, (30, 30, 30), rect.inflate(40, 16), border_radius=12)
    pygame.draw.rect(surface, (255, 255, 80), rect.inflate(40, 16), 2, border_radius=12)
    surface.blit(text, rect)

def handle_player_shoot(state, mouse_pos, config, sounds, game_api=None):
    if game_api and "handle_player_shoot" in game_api and game_api["handle_player_shoot"] is not handle_player_shoot:
        return game_api["handle_player_shoot"](state, mouse_pos, config, sounds, game_api)
    from bullet import Bullet
    player = state["player"]
    screen_center = pygame.Vector2(config.width // 2, config.height // 2)
    mouse_offset = pygame.Vector2(mouse_pos) - screen_center
    mouse_world = player.pos + mouse_offset
    direction = mouse_world - player.pos
    if direction.length() > 0:
        bullet_color = player.color
        bullet_velocity = direction.normalize() * BULLET_SPEED - player.vel * 0.35
        state["bullets"].append(Bullet(player.pos, bullet_velocity, bullet_velocity.length(), bullet_color, BULLET_LIFETIME, config))
        player.vel -= direction.normalize() * 4
        sounds["shoot"].play()
    state["camera"].kickback(-direction.normalize() * 12)

def spawn_enemy(state, config, game_api=None):
    if game_api and "spawn_enemy_func" in game_api and game_api["spawn_enemy_func"] is not spawn_enemy:
        return game_api["spawn_enemy_func"](state, config, game_api)
    from enemy import Enemy
    player = state["player"]
    angle = random.uniform(0, 2 * math.pi)
    dist = random.randint(600, 1200)
    enemy_pos = player.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
    enemy_types = ["default", "fast", "tank", "zigzag"]
    enemy_type = random.choices(enemy_types, weights=[0.5, 0.2, 0.15, 0.15])[0]
    state["enemies"].append(Enemy(enemy_pos, config, enemy_type, game_api=game_api))

def handle_bullet_enemy_collisions(state, achievements, config, sounds, game_api=None):
    if game_api and "handle_bullet_enemy_collisions" in game_api and game_api["handle_bullet_enemy_collisions"] is not handle_bullet_enemy_collisions:
        return game_api["handle_bullet_enemy_collisions"](state, achievements, config, sounds, game_api)
    from explosion import Explosion
    from bonus import Bonus
    for bullet in state["bullets"][:]:
        # Используем кастомный update, если есть
        if hasattr(bullet, "update") and callable(bullet.update):
            bullet.update(game_api=game_api)
        if not bullet.is_alive(game_api=game_api):
            state["explosions"].append(Explosion(bullet.pos, color=(180, 180, 255), type="small"))
            state["bullets"].remove(bullet)
            continue
        for enemy in state["enemies"][:]:
            hit = enemy.pos.distance_to(bullet.pos) < (enemy.radius + 5)
            if hit:
                if bullet in state["bullets"]:
                    state["bullets"].remove(bullet)
                # Используем кастомный is_hit, если есть
                killed = enemy.is_hit(bullet, game_api=game_api) if hasattr(enemy, "is_hit") else False
                if killed:
                    exp_color = {
                        "fast": (100, 255, 255),
                        "tank": (180, 80, 80),
                        "zigzag": (180, 255, 100),
                        "default": (255, 180, 0)
                    }.get(getattr(enemy, "type", "default"), (255, 180, 0))
                    state["explosions"].append(Explosion(enemy.pos, color=exp_color, type="big"))
                    state["enemies"].remove(enemy)
                    state["score"] += 1
                    achievements.stats["enemies_killed"] += 1
                    if getattr(enemy, "type", "") == "tank":
                        achievements.stats["tank_kills"] += 1
                    elif getattr(enemy, "type", "") == "fast":
                        achievements.stats["fast_kills"] += 1
                    elif getattr(enemy, "type", "") == "zigzag":
                        achievements.stats["zigzag_kills"] += 1
                    now = pygame.time.get_ticks()
                    if now - achievements.stats["last_kill_time"] < 5000:
                        achievements.stats["combo_counter"] += 1
                    else:
                        achievements.stats["combo_counter"] = 1
                    achievements.stats["last_kill_time"] = now
                    achievements.stats["shots_hit"] += 1
                    sounds["hit"].play()
                    if random.random() < 0.2:
                        state["bonuses"].append(Bonus(enemy.pos, config))
                break

def handle_enemy_bullet_player_collisions(state, achievements, sounds, game_api=None):
    if game_api and "handle_enemy_bullet_player_collisions" in game_api and game_api["handle_enemy_bullet_player_collisions"] is not handle_enemy_bullet_player_collisions:
        return game_api["handle_enemy_bullet_player_collisions"](state, achievements, sounds, game_api)
    from explosion import Explosion
    player = state["player"]
    for bullet in state["enemy_bullets"][:]:
        if hasattr(bullet, "update") and callable(bullet.update):
            bullet.update(game_api=game_api)
        if not bullet.is_alive(game_api=game_api):
            state["explosions"].append(Explosion(bullet.pos, color=RED, type="small"))
            state["enemy_bullets"].remove(bullet)
        elif bullet.pos.distance_to(player.pos) < (player.radius + 5) and player.lives > 0:
            state["enemy_bullets"].remove(bullet)
            if not (hasattr(player, "has_effect") and player.has_effect("shield")):
                if hasattr(player, "take_damage") and player.take_damage():
                    state["camera"].shake(strength=24, duration=18)
                    achievements.stats["damage_taken"] += 1
                    state["explosions"].append(Explosion(player.pos, color=(255, 80, 80), type="hollow"))
                    sounds["player_hit"].play()
            if player.lives <= 0:
                return "dead"
    return None

def handle_bonuses(state, achievements, sounds, game_api=None):
    if game_api and "handle_bonuses" in game_api and game_api["handle_bonuses"] is not handle_bonuses:
        return game_api["handle_bonuses"](state, achievements, sounds, game_api)
    from explosion import Explosion
    player = state["player"]
    for bonus in state["bonuses"][:]:
        if hasattr(bonus, "update") and callable(bonus.update):
            bonus.update(player, game_api=game_api)
        if not (hasattr(bonus, "is_alive") and bonus.is_alive(game_api=game_api)):
            state["bonuses"].remove(bonus)
        elif player.pos.distance_to(bonus.pos) < (player.radius + bonus.radius):
            if bonus.type == "heal" and player.lives < PLAYER_LIVES:
                if hasattr(player, "apply_effect"):
                    player.apply_effect("heal", amount=1)
                achievements.stats["heal_collected"] += 1
            elif bonus.type == "shield":
                if hasattr(player, "apply_effect"):
                    player.apply_effect("shield", duration=300)
                achievements.stats["shield_collected"] += 1
            state["explosions"].append(Explosion(bonus.pos, color=(100, 200, 255) if bonus.type == "shield" else (100, 255, 100), type="hollow"))
            sounds["bonus"].play()
            achievements.stats["bonuses_collected"] += 1
            state["camera"].shake(strength=10, duration=10)
            state["bonuses"].remove(bonus)

def handle_explosions(state, game_api=None):
    if game_api and "handle_explosions" in game_api and game_api["handle_explosions"] is not handle_explosions:
        return game_api["handle_explosions"](state, game_api)
    for explosion in state["explosions"][:]:
        if hasattr(explosion, "update") and callable(explosion.update):
            explosion.update(game_api=game_api)
        if not (hasattr(explosion, "is_alive") and explosion.is_alive(game_api=game_api)):
            state["explosions"].remove(explosion)

def handle_events(state, achievements, game_api=None):
    if game_api and "handle_events" in game_api and game_api["handle_events"] is not handle_events:
        return game_api["handle_events"](state, achievements, game_api)
    cam_w, cam_h = state["player"].config.width, state["player"].config.height
    camera_pos = state["camera"].get()
    player = state["player"]
    Meteor = None
    BlackHole = None
    if game_api:
        Meteor = game_api.get("Meteor")
        BlackHole = game_api.get("BlackHole")
    if not Meteor:
        from meteor import Meteor
    if not BlackHole:
        from blackhole import BlackHole

    if state["event_timer"] <= 0:
        event_type = random.choice(["meteor_shower", "blackhole"])
        state["event_active"] = event_type
        state["event_duration"] = random.randint(180, 240)
        state["event_timer"] = random.randint(1200, 2000)
        if event_type == "meteor_shower":
            state["current_event_name"] = "Метеоритный дождь!"
        else:
            state["current_event_name"] = "Чёрная дыра!"
        state["current_event_timer"] = state["event_duration"]

    # Метеоритный дождь
    if state["event_active"] == "meteor_shower":
        if state["event_duration"] > 0:
            state["event_duration"] -= 1
            if random.random() < 0.25:
                attempts = 0
                while attempts < 10:
                    mx = camera_pos.x - cam_w // 2 + random.uniform(40, cam_w - 80)
                    my = camera_pos.y - cam_h // 2 + 10
                    meteor_pos = pygame.Vector2(mx, my)
                    if abs(meteor_pos.x - player.pos.x) > player.radius * 2:
                        meteor = Meteor(player.config, meteor_pos)
                        meteor.radius = random.randint(28, 48)
                        meteor.angle = 0
                        meteor.speed = random.uniform(6, 10)
                        state["meteors"].append(meteor)
                        break
                    attempts += 1
        else:
            state["event_active"] = None
            state["current_event_name"] = ""
            state["current_event_timer"] = 0
            achievements.stats["survived_meteor"] = True

    # Чёрные дыры
    if state["event_active"] == "blackhole":
        if state["event_duration"] > 0:
            state["event_duration"] -= 1
            if len(state["blackholes"]) < 2 and random.random() < 0.04:
                attempts = 0
                while attempts < 10:
                    bx = camera_pos.x - cam_w // 2 + random.uniform(100, cam_w - 200)
                    by = camera_pos.y - cam_h // 2 + random.uniform(100, cam_h - 200)
                    bh_pos = pygame.Vector2(bx, by)
                    if bh_pos.distance_to(player.pos) > 200:
                        bh = BlackHole(bh_pos, player.config)
                        bh.radius = random.randint(90, 140)
                        state["blackholes"].append(bh)
                        break
                    attempts += 1
        else:
            state["event_active"] = None
            state["current_event_name"] = ""
            state["current_event_timer"] = 0
            state["blackholes"].clear()
            achievements.stats["survived_blackhole"] = True

    # Обновление и удаление метеоров
    for meteor in state["meteors"][:]:
        if hasattr(meteor, "update") and callable(meteor.update):
            meteor.update(game_api=game_api)
        if meteor.pos.y - meteor.radius > camera_pos.y + cam_w // 2 + 100:
            state["meteors"].remove(meteor)
        elif player.pos.distance_to(meteor.pos) < (meteor.radius + player.radius):
            if not (hasattr(player, "has_effect") and player.has_effect("shield")):
                if hasattr(player, "take_damage") and player.take_damage(amount=1, source="meteor"):
                    from explosion import Explosion
                    state["explosions"].append(Explosion(meteor.pos, color=(180, 180, 180), type="big"))
                    achievements.stats["damage_taken"] += 1
                    state["camera"].shake(strength=18, duration=12)
                    if player.lives <= 0:
                        return "dead"
            state["meteors"].remove(meteor)

    # Обновление и удаление чёрных дыр
    for bh in state["blackholes"][:]:
        if hasattr(bh, "update") and callable(bh.update):
            bh.update(game_api=game_api)
        if hasattr(bh, "attract") and callable(bh.attract):
            bh.attract(player, game_api=game_api)
        cam_w, cam_h = player.config.width, player.config.height
        draw_x = bh.pos.x - camera_pos.x + cam_w // 2
        draw_y = bh.pos.y - camera_pos.y + cam_h // 2
        if not (0 <= draw_x < cam_w and 0 <= draw_y < cam_h):
            state["blackholes"].remove(bh)
            continue
        if not (hasattr(bh, "is_alive") and bh.is_alive(game_api=game_api)):
            state["blackholes"].remove(bh)
            continue
        player.vel += (bh.pos - player.pos).normalize() * 0.15
        if player.pos.distance_to(bh.pos) < 60:
            if state.get("blackhole_damage_timer", 0) <= 0:
                if not (hasattr(player, "has_effect") and player.has_effect("shield")):
                    if hasattr(player, "take_damage") and player.take_damage(amount=1, source="blackhole"):
                        from explosion import Explosion
                        state["camera"].shake(strength=24, duration=18)
                        achievements.stats["damage_taken"] += 1
                        state["explosions"].append(Explosion(player.pos, color=(80, 80, 255), type="hollow"))
                        if player.lives <= 0:
                            return "dead"
                state["blackhole_damage_timer"] = 60
        if state.get("blackhole_damage_timer", 0) > 0:
            state["blackhole_damage_timer"] -= 1

def draw_game(state, achievements, screen, config, game_api):
    game_api["draw_background"](screen, state["camera"].get(), config, game_api)
    for bonus in state["bonuses"]:
        if hasattr(bonus, "draw") and callable(bonus.draw):
            bonus.draw(screen, state["camera"].get(), state["player"], game_api)
    for explosion in state["explosions"]:
        if hasattr(explosion, "draw") and callable(explosion.draw):
            explosion.draw(screen, state["camera"].get(), config, game_api)
    if hasattr(state["player"], "draw") and callable(state["player"].draw):
        state["player"].draw(screen, state["camera"].get(), pygame.mouse.get_pos(), game_api)
    for enemy in state["enemies"]:
        if hasattr(enemy, "draw") and callable(enemy.draw):
            enemy.draw(screen, state["camera"].get(), game_api)
    for bullet in state["bullets"]:
        if hasattr(bullet, "draw") and callable(bullet.draw):
            bullet.draw(screen, state["camera"].get(), game_api)
    for bullet in state["enemy_bullets"]:
        if hasattr(bullet, "draw") and callable(bullet.draw):
            bullet.draw(screen, state["camera"].get(), game_api)
    for meteor in state["meteors"]:
        if hasattr(meteor, "draw") and callable(meteor.draw):
            meteor.draw(screen, state["camera"].get(), game_api)
    for bh in state["blackholes"]:
        if hasattr(bh, "draw") and callable(bh.draw):
            bh.draw(screen, state["camera"].get(), game_api)
    game_api["draw_enemy_indicators"](screen, state["camera"].get(), state["enemies"], config, game_api)
    game_api["draw_lives"](screen, state["player"].lives, config, game_api)
    achievements.draw_stats(screen)
    achievements.draw_achievements(screen)
    achievements.update_popups()
    achievements.draw_popups(screen)
    game_api["draw_event_banner"](screen, state.get("current_event_name", ""), config, game_api)
    pygame.display.flip()