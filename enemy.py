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
        
        # Rychlost - mírně snížená, aby se lépe manévrovalo v zatáčkách
        self.speed = ENEMY_TPS * TILE_SIZE 
        self.path = []
        self.target = None
        self.teleport_to(pos)

    def teleport_to(self, pos):
        px, py = pos
        # Přesné vycentrování na střed dlaždice při startu
        cx = (px // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
        cy = (py // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
        self.rect.center = (cx, cy)

    def _make_image(self):
        surf = pygame.Surface((TILE_SIZE - 4, TILE_SIZE - 4), pygame.SRCALPHA)
        colors = [(255, 0, 0), (255, 128, 0), (0, 200, 200), (100, 0, 200), (150,150,150)]
        c = colors[self.kind % len(colors)]
        pygame.draw.rect(surf, c, surf.get_rect())
        return surf

    def find_path(self, level, target_px):
        start = level.pixel_to_grid(self.rect.centerx, self.rect.centery)
        goal = level.pixel_to_grid(*target_px)
        
        # Pokud je cíl ve zdi (např. hráč se opírá o zeď), najdeme nejbližší volné sousedství
        if level.is_wall(goal[0], goal[1]):
            found_alt = False
            for nb in level.neighbors(goal[0], goal[1]):
                goal = nb
                found_alt = True
                break
            if not found_alt: return []

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
        # --- ROZHODOVÁNÍ O CÍLI ---
        if random.random() < 0.01: 
            self.target = (random.randint(1, level.width-2)*TILE_SIZE, random.randint(1, level.height-2)*TILE_SIZE)
        else:
            if self.kind == 1: # Mírný ambush
                look_ahead = 4
                ahead = (
                    player.rect.centerx + int(player.vel.x * look_ahead), 
                    player.rect.centery + int(player.vel.y * look_ahead)
                )
                self.target = ahead
            else:
                self.target = player.rect.center

        # --- PATHFINDING ---
        if not self.path or random.random() < 0.02:
            self.path = self.find_path(level, self.target)

        # --- POHYB (Oprava zasekávání) ---
        if self.path:
            next_tile = self.path[0]
            tx, ty = level.grid_to_pixel(next_tile[0], next_tile[1])
            # Cílový bod musí být střed dlaždice
            target_x = tx + TILE_SIZE // 2
            target_y = ty + TILE_SIZE // 2

            # Vektor směru k další dlaždici
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            
            distance = pygame.math.Vector2(dx, dy)
            
            if distance.length() > 0:
                move_dist = self.speed * dt
                
                # Pokud jsme blízko cíle, prostě tam skočíme (prevence "přestřelení" do zdi)
                if distance.length() <= move_dist:
                    self.rect.center = (target_x, target_y)
                    self.path.pop(0)
                else:
                    # Normální plynulý pohyb
                    direction = distance.normalize()
                    self.rect.centerx += direction.x * move_dist
                    self.rect.centery += direction.y * move_dist

        # Finální pojistka: Pokud by se rect přesto dotýkal zdi, posuneme ho zpět
        self._check_wall_collision(level)

    def _check_wall_collision(self, level):
        # Tato funkce kontroluje, zda se enemy fyzicky nedotýká zdi
        gx, gy = level.pixel_to_grid(self.rect.centerx, self.rect.centery)
        # Pokud je v kolizi, vycentruje ho zpět do aktuální dlaždice
        if level.is_wall(gx, gy):
            self.teleport_to((gx * TILE_SIZE, gy * TILE_SIZE))