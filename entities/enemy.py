import pygame
import random
from collections import deque
from config.constants import TILE_SIZE, ENEMY_TPS
from utils.resources import resource_path


class Enemy(pygame.sprite.Sprite):
    color = (255, 70, 70)
    name = "Enemy"

    def __init__(self, pos):
        super().__init__()
        self.spawn_pos = pos
        self.base_image = self._load_base_image()
        self.image = pygame.transform.smoothscale(self.base_image, (TILE_SIZE - 4, TILE_SIZE - 4))
        self.rect = self.image.get_rect()
        self.render_angle = 0.0

        self.speed = ENEMY_TPS * TILE_SIZE
        self.path = []
        self.target = None
        self.target_timer = 0.0
        self.teleport_to(pos)

    def _load_base_image(self):
        skin_file = r'imgs/enemy.png'
        try:
            img = pygame.image.load(resource_path(skin_file)).convert_alpha()
            return self._tint_image(img)
        except Exception:
            surf = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3), pygame.SRCALPHA)
            pygame.draw.circle(surf, self.color, (surf.get_width() // 2, surf.get_height() // 2), surf.get_width() // 2)
            return surf

    def _tint_image(self, img):
        tinted = img.copy()
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, 80))
        tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return tinted

    def teleport_to(self, pos):
        px, py = pos
        cx = (px // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
        cy = (py // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
        self.rect.center = (cx, cy)

    def find_path(self, level, target_px):
        start = level.pixel_to_grid(self.rect.centerx, self.rect.centery)
        goal = level.pixel_to_grid(*target_px)

        if level.is_wall(goal[0], goal[1]):
            found_alt = False
            for nb in level.neighbors(goal[0], goal[1]):
                goal = nb
                found_alt = True
                break
            if not found_alt:
                return []

        if start == goal:
            return []

        q = deque([start])
        prev = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            for nb in level.neighbors(*cur):
                if nb not in prev:
                    prev[nb] = cur
                    q.append(nb)

        if goal not in prev:
            return []

        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def random_open_target(self, level):
        for _ in range(50):
            gx = random.randint(1, level.width - 2)
            gy = random.randint(1, level.height - 2)
            if not level.is_wall(gx, gy):
                return (gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2)
        return self.rect.center

    def choose_target(self, dt, level, player):
        return player.rect.center

    def update(self, dt, level, player):
        self.target_timer -= dt
        self.target = self.choose_target(dt, level, player)

        if not self.path or random.random() < 0.02:
            self.path = self.find_path(level, self.target)

        if self.path:
            self._move_along_path(dt, level)

        self._check_wall_collision(level)

    def _move_along_path(self, dt, level):
        next_tile = self.path[0]
        tx, ty = level.grid_to_pixel(next_tile[0], next_tile[1])
        target_x = tx + TILE_SIZE // 2
        target_y = ty + TILE_SIZE // 2

        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = pygame.math.Vector2(dx, dy)

        if distance.length() <= 0:
            return

        move_dist = self.speed * dt
        if distance.length() <= move_dist:
            self.rect.center = (target_x, target_y)
            self.path.pop(0)
            return

        direction = distance.normalize()
        if direction.x < 0:
            self.render_angle = 180
        elif direction.x > 0:
            self.render_angle = 0
        self.rect.centerx += direction.x * move_dist
        self.rect.centery += direction.y * move_dist

    def _check_wall_collision(self, level):
        gx, gy = level.pixel_to_grid(self.rect.centerx, self.rect.centery)
        if level.is_wall(gx, gy):
            self.teleport_to((gx * TILE_SIZE, gy * TILE_SIZE))


class ChaserEnemy(Enemy):
    color = (255, 70, 70)
    name = "Lovec"

    def choose_target(self, dt, level, player):
        return player.rect.center


class PredatorEnemy(Enemy):
    color = (255, 150, 40)
    name = "Predator"

    def choose_target(self, dt, level, player):
        look_ahead = 4 * TILE_SIZE
        if player.vel.length() > 0:
            direction = player.vel.normalize()
        else:
            direction = pygame.math.Vector2(-1 if player.render_angle == 180 else 1, 0)
        return (
            player.rect.centerx + int(direction.x * look_ahead),
            player.rect.centery + int(direction.y * look_ahead),
        )


class WandererEnemy(Enemy):
    color = (70, 210, 220)
    name = "Bloudil"

    def choose_target(self, dt, level, player):
        if self.target is None or not self.path or self.target_timer <= 0:
            self.target_timer = random.uniform(1.0, 2.5)
            return self.random_open_target(level)
        return self.target


class GuardEnemy(Enemy):
    color = (150, 90, 230)
    name = "Strazce"

    def choose_target(self, dt, level, player):
        distance_to_player = pygame.math.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        ).length()
        if distance_to_player < 7 * TILE_SIZE:
            return player.rect.center
        if self.target is None or not self.path or self.target_timer <= 0:
            self.target_timer = random.uniform(1.5, 3.0)
            return self._patrol_target(level)
        return self.target

    def _patrol_target(self, level):
        sx, sy = level.pixel_to_grid(*self.spawn_pos)
        candidates = []
        radius = 5
        for y in range(max(0, sy - radius), min(level.height, sy + radius + 1)):
            for x in range(max(0, sx - radius), min(level.width, sx + radius + 1)):
                if not level.is_wall(x, y):
                    candidates.append((x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
        if candidates:
            return random.choice(candidates)
        return (sx * TILE_SIZE + TILE_SIZE // 2, sy * TILE_SIZE + TILE_SIZE // 2)


class CowardEnemy(Enemy):
    color = (170, 170, 170)
    name = "Zbabelec"

    def choose_target(self, dt, level, player):
        distance_to_player = pygame.math.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        ).length()
        if distance_to_player < 6 * TILE_SIZE:
            if self.target is None or not self.path or self.target_timer <= 0:
                self.target_timer = random.uniform(0.8, 1.6)
                return self._flee_target(level, player)
            return self.target
        return player.rect.center

    def _flee_target(self, level, player):
        px, py = player.rect.center
        best = None
        best_dist = -1
        for _ in range(40):
            target = self.random_open_target(level)
            dist = (target[0] - px) ** 2 + (target[1] - py) ** 2
            if dist > best_dist:
                best = target
                best_dist = dist
        return best if best else self.rect.center
