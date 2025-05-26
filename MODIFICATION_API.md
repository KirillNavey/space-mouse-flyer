# Документация MODIFICATION API для Space Mouse Flyer

## Как работают моды

- Все `.py`-файлы, находящиеся в папке `mods`, автоматически загружаются при запуске игры.
- Каждый мод должен реализовать функцию `apply_mod(game)`, которая вызывается после инициализации основных игровых объектов.
- В функцию `apply_mod(game)` передаётся словарь `game` (`game_api`) с доступом к основным объектам, функциям и параметрам игры.

---

## Доступные объекты и функции в game_api

| Ключ                      | Описание                                                                 |
|---------------------------|--------------------------------------------------------------------------|
| `player`                  | Объект игрока (`Player`)                                                 |
| `enemies`                 | Список всех врагов (`Enemy`)                                             |
| `bullets`                 | Список всех пуль игрока (`Bullet`)                                       |
| `enemy_bullets`           | Список всех вражеских пуль (`Bullet`)                                    |
| `bonuses`                 | Список всех бонусов (`Bonus`)                                            |
| `config`                  | Конфиг игры (размеры экрана и др.)                                       |
| `score()`                 | Получить текущий счёт игрока                                             |
| `set_score(val)`          | Установить счёт                                                          |
| `current_level`           | Текущий уровень                                                          |
| `set_level(val)`          | Установить уровень                                                       |
| `get_level()`             | Получить уровень                                                         |
| `add_enemy(obj)`          | Добавить врага в игру (например, свой класс врага)                       |
| `add_bonus(obj)`          | Добавить бонус в игру                                                    |
| `add_bullet(obj)`         | Добавить пулю игрока                                                     |
| `add_enemy_bullet(obj)`   | Добавить пулю врага                                                      |
| `remove_enemy(obj)`       | Удалить врага                                                            |
| `remove_bullet(obj)`      | Удалить пулю игрока                                                      |
| `remove_enemy_bullet(obj)`| Удалить пулю врага                                                       |
| `remove_bonus(obj)`       | Удалить бонус                                                            |
| `spawn_enemy(pos, etype)` | Спавнить врага (можно заменить своей функцией)                           |
| `spawn_bonus(pos, btype)` | Спавнить бонус                                                           |
| `spawn_explosion(pos, color, type)` | Создать взрыв                                                  |
| `give_damage(amount=1)`   | Нанести урон игроку (можно заменить своей функцией)                      |
| `heal_player()`           | Вылечить игрока                                                          |
| `camera`                  | Объект камеры (`Camera`), можно менять shake, kickback, pos и т.д.       |
| `sounds`                  | Словарь всех игровых звуков (см. ниже)                                   |
| `achievements`            | Объект достижений                                                        |
| `events`                  | Список активных игровых событий (например, метеоритный дождь, blackhole) |
| `on_tick`                 | Список функций, вызываемых каждый кадр (можно добавить свою)             |
| `set_game_state(state)`   | Установить состояние игры                                                |
| `get_game_state()`        | Получить текущее состояние игры                                          |

---

## Работа со звуками

Вы можете заменить любой игровой звук, не изменяя файлы игры, а только через мод.  
Для этого используйте ключ `sounds` в API:

```python
import pygame
import os

def apply_mod(game):
    # Заменить звук выстрела своим
    my_sound = os.path.join(os.path.dirname(__file__), "my_shoot.wav")
    if os.path.exists(my_sound):
        game["sounds"]["shoot"] = pygame.mixer.Sound(my_sound)
```

Список доступных ключей: `"shoot"`, `"hit"`, `"player_hit"`, `"achievement"`, `"levelup"`, `"death"`, `"bonus"`.

---

## Примеры модификаций

### 1. Добавить нового врага

```python
import pygame
from enemy import Enemy

class SuperEnemy(Enemy):
    def __init__(self, pos, config):
        super().__init__(pos, config, "tank")
        self.radius = 60
        self.hp = 20

    def draw(self, surface, camera_pos):
        super().draw(surface, camera_pos)
        pygame.draw.circle(surface, (255, 0, 255), (int(self.pos.x - camera_pos.x + self.config.width // 2), int(self.pos.y - camera_pos.y + self.config.height // 2)), self.radius, 4)

def apply_mod(game):
    # Добавить супер-врага в начале игры
    game["add_enemy"](SuperEnemy(game["player"].pos + pygame.Vector2(400, 0), game["config"]))
```

---

### 2. Добавить функцию, вызываемую каждый кадр

```python
def my_tick(game):
    # Например, сделать игрока бессмертным
    game["player"].lives = 99

def apply_mod(game):
    game["on_tick"].append(lambda: my_tick(game))
```

---

### 3. Удалить всех врагов и бонусы

```python
def apply_mod(game):
    game["enemies"].clear()
    game["bonuses"].clear()
```

---

### 4. Запретить появление новых бонусов

```python
def apply_mod(game):
    game["on_tick"].append(lambda: game["bonuses"].clear())
```

---

### 5. Заменить функцию урона игрока

```python
def custom_damage():
    print("Мод: игрок неуязвим!")

def apply_mod(game):
    game["give_damage"] = custom_damage
```

---

### 6. Изменить поведение камеры

```python
def crazy_camera(game):
    game["camera"].shake(strength=8, duration=2)

def apply_mod(game):
    game["on_tick"].append(lambda: crazy_camera(game))
```

---

## Советы

- Моды могут импортировать любые классы из папки `src` (например, `from enemy import Enemy`).
- Не забудьте проверять совместимость с версией игры.
- Не используйте блокирующие операции или бесконечные циклы в своих модах.
- Для сложных модов создавайте отдельные папки с ресурсами (спрайты, звуки и т.д.).
- Не удаляйте сами списки (`game["enemies"] = None`), только их содержимое.

---

## Как поделиться модом

- Просто отправьте файл или папку с модом другому игроку.
- Для установки мода скопируйте его в папку `mods` и перезапустите игру.

---