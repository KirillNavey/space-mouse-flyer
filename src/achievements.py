import pygame
import os
import json
from settings import *

class Achievements:
    def __init__(self, config, game_api=None, **kwargs):
        self.config = config
        # Моды могут расширять/заменять список достижений через kwargs
        self.achievements = kwargs.get("achievements", {
            "first_blood": False,
            "survivor": False,
            "sharpshooter": False,
            "unstoppable": False,
            "long_run": False,
            "meteor_survivor": False,
            "blackhole_escape": False,
            "no_damage": False,
            "bonus_collector": False,
            "tank_slayer": False,
            "fast_hunter": False,
            "zigzag_master": False,
            "combo_killer": False,
            "shield_master": False,
            "heal_master": False,
        })
        self.stats = kwargs.get("stats", {
            "enemies_killed": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "time_survived": 0,
            "levels_completed": 1,
            "bonuses_collected": 0,
            "tank_kills": 0,
            "fast_kills": 0,
            "zigzag_kills": 0,
            "shield_collected": 0,
            "heal_collected": 0,
            "damage_taken": 0,
            "combo_counter": 0,
            "combo_timer": 0,
            "last_kill_time": 0,
            "survived_meteor": False,
            "survived_blackhole": False,
        })
        self.load()
        self.popup_queue = []
        self.active_popups = []
        self.POPUP_TIME = 90

        # Моды могут добавить любые новые поля через kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Позволяет модам заменить методы через game_api
        if game_api:
            game_api["draw_achievements"] = self.draw_achievements
            game_api["draw_stats"] = self.draw_stats
            game_api["draw_popups"] = self.draw_popups
            game_api["update_popups"] = self.update_popups
            game_api["show_popup"] = self.show_popup
            game_api["check_achievements"] = self.check

    def check(self, score, game_time, player, surface, achievement_sound=None, game_api=None):
        # Моды могут заменить этот метод или расширить его через наследование
        if game_api and "check_achievements" in game_api and game_api["check_achievements"] is not self.check:
            return game_api["check_achievements"](score, game_time, player, surface, achievement_sound, game_api)
        if score >= 1 and not self.achievements.get("first_blood", False):
            self.achievements["first_blood"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Первый фраг!")
        if game_time >= 60 and not self.achievements.get("survivor", False):
            self.achievements["survivor"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Выживший!")
        if self.stats.get("shots_hit", 0) >= 10 and not self.achievements.get("sharpshooter", False):
            self.achievements["sharpshooter"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Меткий стрелок!")
        if self.stats.get("enemies_killed", 0) >= 20 and not self.achievements.get("unstoppable", False):
            self.achievements["unstoppable"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Неостановим!")
        if game_time >= 180 and not self.achievements.get("long_run", False):
            self.achievements["long_run"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Марафонец!")
        if self.stats.get("survived_meteor", False) and not self.achievements.get("meteor_survivor", False):
            self.achievements["meteor_survivor"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Пережить метеоритный дождь!")
        if self.stats.get("survived_blackhole", False) and not self.achievements.get("blackhole_escape", False):
            self.achievements["blackhole_escape"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Выбраться из черной дыры!")
        if self.stats.get("damage_taken", 0) == 0 and self.stats.get("levels_completed", 1) > 1 and not self.achievements.get("no_damage", False):
            self.achievements["no_damage"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Без единой царапины!")
        if self.stats.get("bonuses_collected", 0) >= 10 and not self.achievements.get("bonus_collector", False):
            self.achievements["bonus_collector"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Коллекционер бонусов!")
        if self.stats.get("tank_kills", 0) >= 5 and not self.achievements.get("tank_slayer", False):
            self.achievements["tank_slayer"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Убийца танков!")
        if self.stats.get("fast_kills", 0) >= 10 and not self.achievements.get("fast_hunter", False):
            self.achievements["fast_hunter"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Охотник на быстрых!")
        if self.stats.get("zigzag_kills", 0) >= 10 and not self.achievements.get("zigzag_master", False):
            self.achievements["zigzag_master"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Мастер зигзага!")
        if self.stats.get("combo_counter", 0) >= 3 and not self.achievements.get("combo_killer", False):
            self.achievements["combo_killer"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Комбо-киллер!")
        if self.stats.get("shield_collected", 0) >= 5 and not self.achievements.get("shield_master", False):
            self.achievements["shield_master"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Мастер щита!")
        if self.stats.get("heal_collected", 0) >= 5 and not self.achievements.get("heal_master", False):
            self.achievements["heal_master"] = True
            if achievement_sound: achievement_sound.play()
            self.show_popup("Достижение: Мастер лечения!")
        # Моды могут добавить свои условия

    def show_popup(self, text, surface=None, game_api=None):
        # Моды могут заменить этот метод для кастомных popup'ов
        if game_api and "show_popup" in game_api and game_api["show_popup"] is not self.show_popup:
            return game_api["show_popup"](text, surface, game_api)
        self.popup_queue.append(text)

    def update_popups(self, game_api=None):
        if game_api and "update_popups" in game_api and game_api["update_popups"] is not self.update_popups:
            return game_api["update_popups"](game_api)
        while self.popup_queue and len(self.active_popups) < 3:
            text = self.popup_queue.pop(0)
            self.active_popups.append([text, self.POPUP_TIME])
        for popup in self.active_popups:
            popup[1] -= 1
        self.active_popups = [p for p in self.active_popups if p[1] > 0]

    def draw_popups(self, surface, game_api=None):
        if game_api and "draw_popups" in game_api and game_api["draw_popups"] is not self.draw_popups:
            return game_api["draw_popups"](surface, game_api)
        font = pygame.font.SysFont("consolas", 36)
        base_y = self.config.height // 2 - 200
        for i, (text, timer) in enumerate(self.active_popups):
            alpha = min(255, int(255 * min(1, timer / 15))) if timer < 20 else 255
            surf = font.render(text, True, (255, 255, 0))
            surf.set_alpha(alpha)
            rect = surf.get_rect(center=(self.config.width // 2, base_y + i * 60))
            surface.blit(surf, rect)

    def draw_achievements(self, surface, game_api=None):
        if game_api and "draw_achievements" in game_api and game_api["draw_achievements"] is not self.draw_achievements:
            return game_api["draw_achievements"](surface, game_api)
        font = pygame.font.SysFont("consolas", 24)
        achv_names = {
            "first_blood": "Первый фраг",
            "survivor": "Выживший (60с)",
            "sharpshooter": "Меткий стрелок (10 попаданий)",
            "unstoppable": "Неостановим (20 врагов)",
            "long_run": "Марафонец (3 мин)",
            "meteor_survivor": "Пережить метеоритный дождь",
            "blackhole_escape": "Выбраться из черной дыры",
            "no_damage": "Без единой царапины",
            "bonus_collector": "Коллекционер бонусов",
            "tank_slayer": "Убийца танков",
            "fast_hunter": "Охотник на быстрых",
            "zigzag_master": "Мастер зигзага",
            "combo_killer": "Комбо-киллер",
            "shield_master": "Мастер щита",
            "heal_master": "Мастер лечения",
        }
        x = self.config.width - 320
        y = 220
        header = font.render("Достижения:", True, (255, 255, 0))
        surface.blit(header, (x, y))
        y += 30
        for key in self.achievements:
            unlocked = self.achievements[key]
            color = (100, 255, 100) if unlocked else (100, 100, 100)
            surf = font.render(achv_names.get(key, key), True, color)
            surface.blit(surf, (x, y))
            y += 28

    def draw_stats(self, surface, game_api=None):
        if game_api and "draw_stats" in game_api and game_api["draw_stats"] is not self.draw_stats:
            return game_api["draw_stats"](surface, game_api)
        font = pygame.font.SysFont("consolas", 24)
        stats = [
            f"Врагов убито: {self.stats.get('enemies_killed', 0)}",
            f"Выстрелов: {self.stats.get('shots_fired', 0)}",
            f"Попаданий: {self.stats.get('shots_hit', 0)}",
            f"Время: {self.stats.get('time_survived', 0)} c",
            f"Уровень: {self.stats.get('levels_completed', 1)}",
            f"Точность: {self.stats['shots_hit'] / self.stats['shots_fired'] * 100:.1f}%" if self.stats.get('shots_fired', 0) > 0 else "Точность: 0.0%"
        ]
        x = self.config.width - 320
        y = 30
        header = font.render("Статистика:", True, (180, 180, 255))
        surface.blit(header, (x, y))
        y += 30
        for line in stats:
            surf = font.render(line, True, (180, 180, 255))
            surface.blit(surf, (x, y))
            y += 28

    def save(self):
        data = {
            "achievements": self.achievements,
            "stats": self.stats,
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Progress saved to {SAVE_FILE}")
            pygame.time.delay(500)
        except IOError as e:
            print(f"Failed to save progress to {SAVE_FILE}: {e}")

    def load(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    loaded_achievements = data.get("achievements", {})
                    loaded_stats = data.get("stats", {})
                    for key in self.achievements:
                        if key in loaded_achievements:
                            self.achievements[key] = loaded_achievements[key]
                    for key in self.stats:
                        if key in loaded_stats:
                            self.stats[key] = loaded_stats[key]
                    print(f"Progress loaded from {SAVE_FILE}: {self.achievements}, {self.stats}")
            else:
                print(f"No save file found at {SAVE_FILE}, using default progress")
        except json.JSONDecodeError as e:
            print(f"Failed to parse save file {SAVE_FILE}: {e}, using default progress")
        except Exception as e:
            print(f"Failed to load progress: {e}, using default progress")

    def reset(self):
        print("Resetting progress...")
        self.achievements = {k: False for k in self.achievements}
        self.stats = {
            "enemies_killed": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "time_survived": 0,
            "levels_completed": 1,
            "bonuses_collected": 0,
            "tank_kills": 0,
            "fast_kills": 0,
            "zigzag_kills": 0,
            "shield_collected": 0,
            "heal_collected": 0,
            "damage_taken": 0,
            "combo_counter": 0,
            "combo_timer": 0,
            "last_kill_time": 0,
            "survived_meteor": False,
            "survived_blackhole": False,
        }
        self.save()
        print("Progress reset and saved")