# Space Mouse Flyer: Руководство по созданию модов

## Как работает система модов

- Каждый мод — это отдельный Python-файл в папке `mods/`.
- В каждом моде обязательно должна быть функция `apply_mod(game)`.
- В функцию `apply_mod` передаётся объект `game` — это словарь со всеми основными объектами, функциями и классами игры.
- Моды могут заменять, расширять или добавлять любые функции, классы, обработчики и параметры через этот объект.
- Все функции ядра должны вызываться только через `game`, чтобы моды могли их переопределять.

---

## Структура объекта game

В функцию `apply_mod(game)` передаётся словарь с такими ключами:

| Ключ                | Описание                                                                                   |
|---------------------|--------------------------------------------------------------------------------------------|
| `player`            | Игрок (объект класса Player)                                                               |
| `state`             | Глобальное состояние игры (словарь с объектами, списками, таймерами и т.д.)                |
| `config`            | Конфиг игры (размеры экрана, параметры, настройки)                                         |
| `camera`            | Камера (позиция, методы движения, тряска и т.д.)                                           |
| `sounds`            | Словарь всех игровых звуков                                                                |
| `achievements`      | Объект достижений                                                                          |
| `screen`            | Главный экран для отрисовки                                                                |
| `on_tick`           | Список функций, вызываемых каждый кадр (можно добавлять свои обработчики)                  |
| `fps`               | FPS игры (изменяемый контейнер, например: `game["set_fps"](120)`)                          |
| `set_fps`           | Функция для изменения FPS                                                                  |
| ...                 | Все функции и классы ядра, которые можно заменить (см. ниже)                               |

**Функции ядра (можно заменить своей):**
- `draw_game`
- `handle_events`
- `draw_lives`
- `draw_background`
- `menu_loop`
- и другие (см. исходный код)

**Классы ядра (можно заменить своей реализацией):**
- `Player`
- `Enemy`
- `Bonus`
- и другие

---

## Примеры: как писать моды

### 1. Минимальный мод

```python
def apply_mod(game):
    print("Мой мод успешно загружен!")
```

---

### 2. Как заменить функцию ядра (например, отрисовку жизней)

```python
import pygame

def draw_hearts(screen, lives, config, game_api=None):
    n = game_api["settings"]["PLAYER_LIVES"]
    for i in range(n):
        x = config.width - 24 - 42*i
        y = 40
        color = (255,80,120) if i < lives else (80,80,80)
        heart = pygame.Surface((32,32), pygame.SRCALPHA)
        pygame.draw.circle(heart, color, (11,12), 9)
        pygame.draw.circle(heart, color, (21,12), 9)
        pygame.draw.polygon(heart, color, [(6,18),(16,29),(26,18)])
        pygame.draw.circle(heart, (255,255,255,120), (16,16), 15, 2)
        screen.blit(heart, (x-16, y-16))

def apply_mod(game):
    game["draw_lives"] = draw_hearts
```

---

### 3. Как заменить класс (например, сделать врага с новым поведением)

```python
from enemy import Enemy

class SlowEnemy(Enemy):
    def update(self, player_pos, enemy_bullets, camera_pos, game_api=None):
        # Враг двигается медленно и не стреляет
        direction = (player_pos - self.pos)
        if direction.length() > 1:
            self.pos += direction.normalize() * 0.5

def apply_mod(game):
    game["Enemy"] = SlowEnemy
```

---

### 4. Как изменить или расширить логику объекта (например, добавить прыжок игроку)

```python
import pygame

def player_update_with_jump(self):
    keys = pygame.key.get_pressed()
    if not hasattr(self, "jump_vel"):
        self.jump_vel = 0
        self.is_jumping = False
    if keys[pygame.K_SPACE] and not self.is_jumping:
        self.is_jumping = True
        self.jump_vel = -15
    if self.is_jumping:
        self.pos.y += self.jump_vel
        self.jump_vel += 1
        if self.pos.y >= self.config.height // 2:
            self.pos.y = self.config.height // 2
            self.is_jumping = False
            self.jump_vel = 0
    # Можно добавить вызов оригинального update, если нужно

def apply_mod(game):
    game["player"].update = lambda: player_update_with_jump(game["player"])
```

---

### 5. Как заменить или добавить спрайт

```python
import pygame
import os

def apply_mod(game):
    sprite_path = os.path.join(os.path.dirname(__file__), "my_player.png")
    if os.path.exists(sprite_path):
        game["player"].sprite = pygame.image.load(sprite_path).convert_alpha()
```

---

### 6. Как заменить звук

```python
import pygame
import os

def apply_mod(game):
    new_sound = os.path.join(os.path.dirname(__file__), "laser.wav")
    if os.path.exists(new_sound):
        game["sounds"]["shoot"] = pygame.mixer.Sound(new_sound)
```

---

### 7. Как вмешаться в игровой цикл (on_tick)

```python
def print_score_tick(game):
    print("Текущий счёт:", game["state"]["score"])

def apply_mod(game):
    game["on_tick"].append(lambda: print_score_tick(game))
```

---

### 8. Как добавить новую переменную или метод к объекту

```python
def apply_mod(game):
    game["player"].is_super = True
    def super_attack(self):
        print("Суператака!")
    game["player"].super_attack = super_attack.__get__(game["player"])
```

---

### 9. Как полностью переписать игровой процесс (например, сделать игрока бессмертным)

```python
def immortal_damage(amount=1, source=None):
    print("Игрок бессмертен!")

def apply_mod(game):
    game["give_damage"] = immortal_damage
```

---

### 10. Как изменить FPS

```python
def apply_mod(game):
    game["set_fps"](30)  # Ограничить игру 30 кадрами в секунду
```

---

### 11. Как добавить свой обработчик событий

```python
import pygame

def my_event_handler(state, achievements, game_api=None):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            print("Вы нажали H!")
    # Можно вызвать оригинальный обработчик, если нужно:
    # return game_api["handle_events"](state, achievements, game_api)

def apply_mod(game):
    game["handle_events"] = my_event_handler
```

---

### 12. Как добавить новый эффект или механику

```python
def speed_boost_tick(game):
    player = game["player"]
    if not hasattr(player, "boost"):
        player.boost = 1.0
    player.vel *= player.boost

def apply_mod(game):
    game["player"].boost = 2.0
    game["on_tick"].append(lambda: speed_boost_tick(game))
```

---

### 13. Как добавить новый ключ в game или state

```python
def apply_mod(game):
    game["my_param"] = 42
    game["state"]["my_list"] = []
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

**Минимальный пример:**
```python
def apply_mod(game):
    print("Мод загружен!")
```