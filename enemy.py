import pygame
import random
from collections import deque
from constants import TILE_SIZE, ENEMY_TPS

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, kind=0):
        super().__init__()
        self.kind = kind
        self.image = self._make_image()
        self.rect = self.image.get_rect()
        self.speed = ENEMY_TPS * TILE_SIZE  # pixels per second
        self.path = []
        self.target = None
        self.teleport_to(pos)

    def teleport_to(self, pos):
        px, py = pos
        cx = (px // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
        cy = (py // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
        self.rect.center = (cx, cy)

    def _make_image(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        colors = [(255, 0, 0), (255, 128, 0), (0, 200, 200), (100, 0, 200), (150,150,150)]
        c = colors[self.kind % len(colors)]
        pygame.draw.rect(surf, c, surf.get_rect())
        return surf

    def find_path(self, level, target_px):
        start = level.pixel_to_grid(self.rect.centerx, self.rect.centery)
        goal = level.pixel_to_grid(*target_px)
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

    def update(self, dt, level, player):
        # Decide on target based on kind
        if self.kind == 0:
            # direct chaser
            self.target = player.rect.center
        elif self.kind == 1:
            # ambusher ahead of player
            ahead = (player.rect.centerx + int(player.vel.x*10), player.rect.centery + int(player.vel.y*10))
            self.target = ahead
        elif self.kind == 2:
            # random wander but sometimes chase
            if random.random() < 0.02:
                self.target = player.rect.center
            else:
                self.target = (random.randint(1, level.width-2)*TILE_SIZE, random.randint(1, level.height-2)*TILE_SIZE)
        elif self.kind == 3:
            # patrol between spawns if any
            self.target = player.rect.center if random.random() < 0.05 else self.rect.center
        else:
            # cautious: approach slowly
            self.target = player.rect.center

        if not self.path or random.random() < 0.02:
            self.path = self.find_path(level, self.target)

        if self.path:
            nextg = self.path[0]
            tx = nextg[0]*TILE_SIZE + TILE_SIZE//2
            ty = nextg[1]*TILE_SIZE + TILE_SIZE//2
            dirv = pygame.math.Vector2(tx - self.rect.centerx, ty - self.rect.centery)
            if dirv.length_squared() > 0:
                vel = dirv.normalize() * self.speed * dt
                self.rect.centerx += int(vel.x)
                self.rect.centery += int(vel.y)
                # reached next tile?
                if abs(self.rect.centerx - tx) < 4 and abs(self.rect.centery - ty) < 4:
                    self.rect.center = (tx, ty)
                    self.path.pop(0)