# Space Mouse Flyer: Полный API для модификаций

## Возможности модов

Система модификаций Space Mouse Flyer позволяет модам:
- **Заменять любые функции** (отрисовка, обработка событий, спавн врагов, урон, фон, меню и т.д.)
- **Добавлять новые функции, обработчики, объекты и события**
- **Изменять или расширять поведение и логику любых объектов**
- **Заменять или добавлять спрайты, звуки, фон, эффекты**
- **Вмешиваться в игровой цикл через on_tick**
- **Добавлять новые переменные и методы к объектам**
- **Полностью переписывать или расширять игровой процесс**
- **Менять FPS, параметры сложности, структуру состояния, достижения, ресурсы и т.д.**

---

## Как работает система модов

- Каждый мод — это Python-файл с функцией `apply_mod(game)`.
- В функцию `apply_mod` передаётся объект `game` — это словарь со всеми основными объектами и функциями игры.
- Мод может изменять, заменять или расширять любые функции и объекты через этот API.
- Моды автоматически подгружаются из папки `mods/` при запуске игры.

---

## Структура объекта game

В функцию `apply_mod(game)` передаётся словарь со следующими ключами:

| Ключ                | Тип/Объект                | Описание                                                                                   |
|---------------------|--------------------------|--------------------------------------------------------------------------------------------|
| `player`            | Player                   | Игрок. Все его поля и методы можно изменять и расширять.                                   |
| `state`             | dict                     | Глобальное состояние игры: все списки объектов, таймеры, очки, события и т.д.              |
| `config`            | GameConfig               | Конфиг игры (размеры экрана, параметры, настройки).                                        |
| `camera`            | Camera                   | Камера (позиция, методы движения, тряска и т.д.).                                          |
| `sounds`            | dict                     | Словарь всех игровых звуков. Ключи: `"shoot"`, `"hit"`, `"bonus"`, `"player_hit"`, ...     |
| `achievements`      | Achievements             | Объект достижений, можно читать/менять статистику и вызывать методы.                       |
| `screen`            | pygame.Surface           | Главный экран для отрисовки.                                                               |
| `on_tick`           | list[callable]           | Список функций, вызываемых каждый кадр (можно добавлять свои обработчики).                 |
| `fps`               | list[int]                | FPS игры (изменяемый контейнер, например: `game["set_fps"](144)`).                         |
| `set_fps`           | function                 | Функция для изменения FPS: `game["set_fps"](144)`.                                         |
| `add_enemy`         | function                 | Функция для добавления врага: `add_enemy(enemy_obj)`                                       |
| `add_bonus`         | function                 | Функция для добавления бонуса: `add_bonus(bonus_obj)`                                      |
| `add_bullet`        | function                 | Функция для добавления пули игрока: `add_bullet(bullet_obj)`                               |
| `add_enemy_bullet`  | function                 | Функция для добавления пули врага: `add_enemy_bullet(bullet_obj)`                          |
| `remove_enemy`      | function                 | Удалить врага из state                                                                     |
| `remove_bullet`     | function                 | Удалить пулю игрока из state                                                               |
| `remove_enemy_bullet`| function                | Удалить пулю врага из state                                                                |
| `remove_bonus`      | function                 | Удалить бонус из state                                                                     |
| `spawn_enemy`       | function                 | Спавн врага: `spawn_enemy(pos, etype="default")`                                           |
| `spawn_bonus`       | function                 | Спавн бонуса: `spawn_bonus(pos, btype=None)`                                               |
| `spawn_explosion`   | function                 | Спавн взрыва: `spawn_explosion(pos, color, type)`                                          |
| `give_damage`       | function                 | Нанести урон игроку: `give_damage(amount=1, source=None)`                                  |
| `heal_player`       | function                 | Вылечить игрока                                                                            |
| `set_game_state`    | function                 | Сменить состояние игры (например, "menu", "game", "pause", "dead")                         |
| `get_game_state`    | function                 | Получить текущее состояние игры                                                            |
| `set_score`         | function                 | Установить счёт                                                                            |
| `get_score`         | function                 | Получить счёт                                                                              |
| `set_level`         | function                 | Установить уровень                                                                         |
| `get_level`         | function                 | Получить уровень                                                                           |
| **Функции ядра**    | function                 | Все функции ядра можно заменить: см. ниже                                                  |
| **Классы ядра**     | class                    | Все классы ядра можно заменить: см. ниже                                                   |

**Функции ядра (можно заменить своей):**
- `draw_game`
- `handle_events`
- `handle_player_shoot`
- `spawn_enemy_func`
- `handle_bullet_enemy_collisions`
- `handle_enemy_bullet_player_collisions`
- `handle_bonuses`
- `handle_explosions`
- `draw_background`
- `draw_enemy_indicators`
- `draw_lives`
- `draw_menu`
- `menu_loop`
- `select_difficulty`
- `draw_event_banner`
- `reset_game_state`

**Классы ядра (можно заменить своей реализацией):**
- `Player`
- `Enemy`
- `Bonus`
- `Explosion`
- `Meteor`
- `BlackHole`
- `Bullet`
- `Camera`

**Если вы хотите добавить новый ключ — просто добавьте его в объект game в своём моде или в ядре игры!**

---

## Структура state

В `game["state"]` доступны все игровые списки и переменные:

- `"player"`: объект игрока
- `"camera"`: объект камеры
- `"enemies"`: список врагов
- `"bullets"`: список пуль игрока
- `"enemy_bullets"`: список пуль врагов
- `"bonuses"`: список бонусов
- `"explosions"`: список взрывов
- `"meteors"`: список метеоров
- `"blackholes"`: список чёрных дыр
- `"score"`: текущий счёт
- `"level"`: текущий уровень
- `"game_time"`: время игры
- ...и любые другие переменные, которые вы добавите

---

## Как заменить любую функцию

**Пример: заменить фон на изображение**
```python
import pygame
import os

def my_bg(surface, camera_pos, config):
    bg_path = os.path.join(os.path.dirname(__file__), "my_bg.jpg")
    if not hasattr(my_bg, "img"):
        if os.path.exists(bg_path):
            my_bg.img = pygame.image.load(bg_path).convert()
            my_bg.img = pygame.transform.scale(my_bg.img, (config.width, config.height))
        else:
            my_bg.img = None
    if my_bg.img:
        surface.blit(my_bg.img, (0, 0))
    else:
        surface.fill((0, 0, 0))

def apply_mod(game):
    game["draw_background"] = my_bg
```

---

## Как заменить звук или спрайт

**Пример: заменить звук выстрела**
```python
import pygame
import os

def apply_mod(game):
    new_sound = os.path.join(os.path.dirname(__file__), "laser.wav")
    if os.path.exists(new_sound):
        game["sounds"]["shoot"] = pygame.mixer.Sound(new_sound)
```

**Пример: заменить спрайт игрока**
```python
import pygame
import os

def apply_mod(game):
    sprite_path = os.path.join(os.path.dirname(__file__), "new_player.png")
    if os.path.exists(sprite_path):
        game["player"].sprite = pygame.image.load(sprite_path).convert_alpha()
```

---

## Как добавить новую механику (например, прыжок)

```python
import pygame

def jump_event_handler(game):
    events = pygame.event.get(pygame.KEYDOWN)
    for event in events:
        if event.key == pygame.K_SPACE and not getattr(game["player"], "is_jumping", False):
            game["player"].is_jumping = True
            game["player"].jump_vel = -18

def jump_physics(game):
    player = game["player"]
    if getattr(player, "is_jumping", False):
        player.pos.y += player.jump_vel
        player.jump_vel += 1
        if player.pos.y >= player.config.height // 2:
            player.pos.y = player.config.height // 2
            player.is_jumping = False
            player.jump_vel = 0

def apply_mod(game):
    player = game["player"]
    player.is_jumping = False
    player.jump_vel = 0
    game["on_tick"].append(lambda: jump_event_handler(game))
    game["on_tick"].append(lambda: jump_physics(game))
```

---

## Как добавить нового врага

```python
from enemy import Enemy
import pygame

class RainbowEnemy(Enemy):
    def __init__(self, pos, config):
        super().__init__(pos, config, "default")
        self.color_phase = 0

    def update(self, player_pos, enemy_bullets, camera_pos):
        super().update(player_pos, enemy_bullets, camera_pos)
        self.color_phase += 0.1

    def draw(self, surface, camera_pos):
        import math
        draw_pos = self.pos - camera_pos + pygame.Vector2(self.config.width // 2, self.config.height // 2)
        color = (
            int(127 + 128 * math.sin(self.color_phase)),
            int(127 + 128 * math.sin(self.color_phase + 2)),
            int(127 + 128 * math.sin(self.color_phase + 4))
        )
        pygame.draw.circle(surface, color, (int(draw_pos.x), int(draw_pos.y)), self.radius)

def apply_mod(game):
    game["add_enemy"](RainbowEnemy(game["player"].pos + pygame.Vector2(300, 0), game["config"]))
```

---

## Как изменить игровую логику

**Пример: сделать игрока бессмертным**
```python
def immortal_damage(*args, **kwargs):
    print("Игрок бессмертен!")

def apply_mod(game):
    game["give_damage"] = immortal_damage
```

---

## Как добавить обработчик, вызываемый каждый кадр

```python
def my_tick(game):
    # Например, увеличить скорость игрока
    game["player"].vel *= 1.05

def apply_mod(game):
    game["on_tick"].append(lambda: my_tick(game))
```

---

## Как изменить FPS

```python
def apply_mod(game):
    game["set_fps"](144)  # Теперь игра будет работать на 144 FPS
```

---

## Как изменить достижения

**Добавить новое достижение:**
```python
def apply_mod(game):
    ach = game["achievements"]
    ach.achievements["snake_master"] = False
    def new_check(*args, **kwargs):
        Achievements.check(ach, *args, **kwargs)
        if ach.stats.get("snake_score", 0) >= 10 and not ach.achievements["snake_master"]:
            ach.achievements["snake_master"] = True
            ach.show_popup("Достижение: Змеиный мастер!")
    ach.check = new_check
```

**Полностью заменить систему достижений:**
```python
class MyAchievements:
    def __init__(self, config):
        self.achievements = {"mod_ach": False}
        self.stats = {}
    def check(self, *a, **kw):
        if not self.achievements["mod_ach"]:
            self.achievements["mod_ach"] = True
            print("Модовое достижение!")
    def show_popup(self, text):
        print("POPUP:", text)
    def draw_stats(self, screen): pass
    def draw_achievements(self, screen): pass
    def update_popups(self): pass
    def draw_popups(self, screen): pass

def apply_mod(game):
    game["achievements"] = MyAchievements(game["config"])
```

---

## Как получить доступ к любому объекту или функции

Всё, что есть в `game` и `state`, доступно для модификации.  
Вы можете:
- Добавлять новые переменные к объектам (например, `player.is_jumping = True`)
- Заменять методы объектов (например, `player.update = my_update`)
- Добавлять свои обработчики событий, физики, отрисовки и т.д.
- Заменять любые функции ядра (отрисовка, обработка событий, спавн, урон и т.д.)
- Заменять или расширять любые классы (Player, Enemy, Bonus, ...)

---

## Как добавить свои параметры или объекты

Вы можете добавить любые новые ключи в `game`, `state`, `config` или свои классы:

```python
def apply_mod(game):
    game["my_param"] = 42
    game["state"]["my_list"] = []
    game["config"].my_setting = True
```

---

## Итог

**Вы можете модифицировать абсолютно всё:**
- Заменять, расширять или удалять любые функции и объекты
- Добавлять новые механики, врагов, бонусы, эффекты, события
- Менять спрайты, звуки, фон, параметры игры
- Вмешиваться в игровой цикл через on_tick
- Делать игру совершенно другой — всё ограничено только вашей фантазией!

---

## Как подключить мод

1. Поместите свой мод в папку `mods/`.
2. В начале игры моды автоматически подгружаются и применяются.
3. Каждый мод должен содержать функцию `apply_mod(game)`.

---

**Пример минимального мода:**
```python
def apply_mod(game):
    print("Мой мод загружен!")
```

---

**Если вы не нашли нужный пример — спросите, и мы добавим его в документацию!**