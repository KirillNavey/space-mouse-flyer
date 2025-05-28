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
import utils
import settings
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

def load_sound(name, volume=0.5):
    s = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sounds", name))
    s.set_volume(volume)
    return s

sounds = {
    "shoot": load_sound("shoot.mp3"),
    "hit": load_sound("hit.mp3"),
    "player_hit": load_sound("player_hit.mp3"),
    "achievement": load_sound("achievement.mp3"),
    "levelup": load_sound("level_up.mp3"),
    "death": load_sound("death.mp3"),
    "bonus": load_sound("bonus.mp3"),
}

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
config = GameConfig(WIDTH, HEIGHT)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Mouse Flyer")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

def reset_game_state(difficulty=1, game_api=None):
    player_cls = Player if not game_api else game_api.get("Player", Player)
    camera_cls = Camera if not game_api else game_api.get("Camera", Camera)
    player = player_cls(config)
    camera = camera_cls(player.pos)
    return {
        "player": player,
        "camera": camera,
        "bullets": [],
        "enemy_bullets": [],
        "enemies": [],
        "bonuses": [],
        "explosions": [],
        "meteors": [],
        "blackholes": [],
        "score": 0,
        "level": 1,
        "kills_for_next_level": LEVEL_UP_KILLS,
        "enemy_spawn_timer": DIFFICULTY_LEVELS[difficulty - 1]["enemy_spawn"],
        "ENEMY_SPAWN_TIME": DIFFICULTY_LEVELS[difficulty - 1]["enemy_spawn"],
        "MAX_ENEMIES": DIFFICULTY_LEVELS[difficulty - 1]["max_enemies"],
        "ENEMY_SPEED": DIFFICULTY_LEVELS[difficulty - 1]["enemy_speed"],
        "game_time": 0,
        "shield_timer": 0,
        "event_timer": random.randint(1200, 2000),
        "event_active": None,
        "event_duration": 0,
        "blackhole_damage_timer": 0,
        "current_difficulty": difficulty,
    }

def main():
    achievements = Achievements(config)
    achievements.load()
    current_difficulty = 2  # по умолчанию "Средне"
    state = reset_game_state(current_difficulty)
    game_state = "menu"

    # --- API для модов ---
    fps = [60]  # изменяемый контейнер для FPS
    on_tick = []
    game_api = {
        "player": state["player"],
        "state": state,
        "config": config,
        "camera": state["camera"],
        "sounds": sounds,
        "achievements": achievements,
        "screen": screen,
        "on_tick": on_tick,
        "fps": fps,
        "set_fps": lambda val: fps.__setitem__(0, val),
        "settings": {k: getattr(settings, k) for k in dir(settings) if not k.startswith("__")},
        "add_enemy": lambda obj: state["enemies"].append(obj),
        "add_bonus": lambda obj: state["bonuses"].append(obj),
        "add_bullet": lambda obj: state["bullets"].append(obj),
        "add_enemy_bullet": lambda obj: state["enemy_bullets"].append(obj),
        "remove_enemy": lambda obj: state["enemies"].remove(obj) if obj in state["enemies"] else None,
        "remove_bullet": lambda obj: state["bullets"].remove(obj) if obj in state["bullets"] else None,
        "remove_enemy_bullet": lambda obj: state["enemy_bullets"].remove(obj) if obj in state["enemy_bullets"] else None,
        "remove_bonus": lambda obj: state["bonuses"].remove(obj) if obj in state["bonuses"] else None,
        "spawn_enemy": lambda pos, etype="default": state["enemies"].append(game_api["Enemy"](pos, config, etype)),
        "spawn_bonus": lambda pos, btype=None: state["bonuses"].append(game_api["Bonus"](pos, config)) if btype is None else state["bonuses"].append(game_api["Bonus"](pos, config, btype)),
        "spawn_explosion": lambda pos, color=(255,200,50), type="big": state["explosions"].append(game_api["Explosion"](pos, color, type)),
        "give_damage": lambda amount=1: state["player"].take_damage(amount=amount),
        "heal_player": lambda: state["player"].heal(),
        "set_game_state": lambda s: globals().__setitem__('game_state', s),
        "get_game_state": lambda: game_state,
        "set_score": lambda val: state.update({"score": val}),
        "get_score": lambda: state["score"],
        "set_level": lambda val: state.update({"level": val}),
        "get_level": lambda: state["level"],
        # Функции, которые могут быть заменены модами:
        "draw_game": utils.draw_game,
        "handle_events": utils.handle_events,
        "handle_player_shoot": utils.handle_player_shoot,
        "spawn_enemy_func": utils.spawn_enemy,
        "handle_bullet_enemy_collisions": utils.handle_bullet_enemy_collisions,
        "handle_enemy_bullet_player_collisions": utils.handle_enemy_bullet_player_collisions,
        "handle_bonuses": utils.handle_bonuses,
        "handle_explosions": utils.handle_explosions,
        "draw_background": utils.draw_background,
        "draw_enemy_indicators": utils.draw_enemy_indicators,
        "draw_lives": utils.draw_lives,
        "draw_menu": utils.draw_menu,
        "menu_loop": utils.menu_loop,
        "select_difficulty": utils.select_difficulty,
        "draw_event_banner": utils.draw_event_banner,
        "reset_game_state": reset_game_state,
        # Классы для гибкости:
        "Player": Player,
        "Enemy": Enemy,
        "Bonus": Bonus,
        "Explosion": Explosion,
        "Meteor": Meteor,
        "BlackHole": BlackHole,
        "Bullet": Bullet,
        "Camera": Camera,
    }

    # --- Применение модов ---
    for mod in loaded_mods:
        if hasattr(mod, "apply_mod"):
            try:
                mod.apply_mod(game_api)
            except Exception as e:
                print(f"Ошибка применения мода {mod}: {e}")

    def get_func(name):
        return game_api.get(name)

    state["current_event_name"] = ""
    state["current_event_timer"] = 0

    gameplay_time = 0.0
    gameplay_time_start = None

    while True:
        # --- Меню ---
        if game_state == "menu":
            menu_result = get_func("menu_loop")(screen, [
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
                current_difficulty = get_func("select_difficulty")(screen, config, current_difficulty)
                state = get_func("reset_game_state")(current_difficulty, game_api)
                game_api["state"] = state
                game_api["player"] = state["player"]
                game_api["camera"] = state["camera"]
                game_state = "game"
                gameplay_time_start = pygame.time.get_ticks()
                continue
            elif menu_result == "exit":
                pygame.quit()
                sys.exit()
            continue

        # --- Пауза ---
        if game_state == "pause":
            get_func("menu_loop")(screen, [
                "Пауза",
                f"Счет: {state['score']}",
                f"Уровень: {state['level']}",
                f"Врагов уничтожено: {achievements.stats['enemies_killed']}",
                f"Время: {int(state['game_time'])} сек",
                "",
                "Продолжить — ENTER/SPACE/ESC",
                "Выйти — M",
                "",
                "Навигация: стрелки/W/S  |  Выбор: ENTER/SPACE"
            ], config, achievements)
            game_state = "game"
            continue

        # --- После смерти ---
        if game_state == "dead":
            achievements.save()
            sounds["death"].play()
            get_func("menu_loop")(screen, [
                "Игра окончена",
                f"Ваш счет: {state['score']}",
                f"Врагов уничтожено: {achievements.stats['enemies_killed']}",
                f"Время: {int(state['game_time'])} сек",
                "",
                "В меню — ENTER/SPACE/ESC",
                "Выйти — M",
                "",
                "Навигация: стрелки/W/S  |  Выбор: ENTER/SPACE"
            ], config, achievements)
            game_state = "menu"
            continue

        # --- Обработка событий pygame (если мод не заменил handle_events полностью) ---
        if get_func("handle_events") == utils.handle_events:
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
                if event.type == pygame.MOUSEBUTTONDOWN and state["player"].lives > 0:
                    get_func("handle_player_shoot")(state, pygame.mouse.get_pos(), config, sounds)
                    achievements.stats["shots_fired"] += 1

        pygame.mouse.set_visible(True)

        # --- on_tick от модов ---
        for func in game_api["on_tick"]:
            func()

        # --- Стандартная логика (если не заменена модом) ---
        if get_func("handle_events") == utils.handle_events:
            if game_state == "game":
                if gameplay_time_start is None:
                    gameplay_time_start = pygame.time.get_ticks()
                state["player"].update()
                state["camera"].update(state["player"].pos)
                state["game_time"] = gameplay_time + (pygame.time.get_ticks() - gameplay_time_start) / 1000
                achievements.stats["time_survived"] = int(state["game_time"])
            else:
                if gameplay_time_start is not None:
                    gameplay_time += (pygame.time.get_ticks() - gameplay_time_start) / 1000
                    gameplay_time_start = None

            # Уровень и сложность
            if achievements.stats["enemies_killed"] >= state["kills_for_next_level"]:
                state["level"] += 1
                state["kills_for_next_level"] += LEVEL_UP_KILLS
                achievements.stats["levels_completed"] = state["level"]
                state["ENEMY_SPAWN_TIME"] = max(30, state["ENEMY_SPAWN_TIME"] - 10)
                state["MAX_ENEMIES"] += 2
                sounds["levelup"].play()
                achievements.show_popup(f"Уровень {state['level']}!")
                if not achievements.achievements.get("no_damage", False):
                    achievements.stats["damage_taken"] = 0

            # Спавн врагов
            state["enemy_spawn_timer"] -= 1
            if state["enemy_spawn_timer"] <= 0 and len(state["enemies"]) < state["MAX_ENEMIES"]:
                get_func("spawn_enemy_func")(state, config)
                state["enemy_spawn_timer"] = state["ENEMY_SPAWN_TIME"]

            if state["event_timer"] > 0:
                state["event_timer"] -= 1

            # Обновление врагов
            state["enemies"] = [enemy for enemy in state["enemies"] if enemy.pos.distance_to(state["player"].pos) < 2500]
            for enemy in state["enemies"]:
                enemy.update(state["player"].pos, state["enemy_bullets"], state["camera"].get())

            # Коллизии и обработка объектов
            get_func("handle_bullet_enemy_collisions")(state, achievements, config, sounds)
            result = get_func("handle_enemy_bullet_player_collisions")(state, achievements, sounds)
            if result == "dead":
                game_state = "dead"
                continue
            get_func("handle_bonuses")(state, achievements, sounds)
            get_func("handle_explosions")(state)
            result = get_func("handle_events")(state, achievements, game_api)
            if result == "dead":
                game_state = "dead"
                continue

            achievements.check(state["score"], state["game_time"], state["player"], screen, sounds["achievement"])

        else:
            # Если мод полностью заменил handle_events, просто вызываем её
            result = get_func("handle_events")(state, achievements, game_api)
            if result == "dead":
                game_state = "dead"
                continue

        # --- Рисование (может быть заменено модом) ---
        get_func("draw_game")(state, achievements, screen, config, game_api)
        clock.tick(game_api["fps"][0])

if __name__ == "__main__":
    main()