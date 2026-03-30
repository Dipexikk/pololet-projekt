import pygame
from constants import TILE_SIZE, PLAYER_TPS

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, skin_index=0):
        super().__init__()
        self.skin_index = skin_index
        self.image = self._make_image()
        self.rect = self.image.get_rect()
        self.teleport_to(pos)
        self.target_grid = None
        self.speed = PLAYER_TPS * TILE_SIZE  # pixels per second
        self.vel = pygame.math.Vector2(0,0)
        self.collected = 0

    def _make_image(self):
        surf = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4), pygame.SRCALPHA)
        colors = [(255, 255, 0), (0, 200, 200), (200, 100, 255)]
        c = colors[self.skin_index % len(colors)]
        pygame.draw.circle(surf, c, ((TILE_SIZE-4)//2, (TILE_SIZE-4)//2), (TILE_SIZE-4)//2)
        return surf

    def update(self, dt, level):
        keys = pygame.key.get_pressed()
        gx, gy = level.pixel_to_grid(self.rect.centerx, self.rect.centery)

        desired = None
        if keys[pygame.K_LEFT]: desired = (-1,0)
        elif keys[pygame.K_RIGHT]: desired = (1,0)
        elif keys[pygame.K_UP]: desired = (0,-1)
        elif keys[pygame.K_DOWN]: desired = (0,1)

        if desired and self.target_grid is None:
            nx, ny = gx + desired[0], gy + desired[1]
            if not level.is_wall(nx, ny):
                self.target_grid = (nx, ny)
                target_px = (nx * TILE_SIZE + TILE_SIZE//2, ny * TILE_SIZE + TILE_SIZE//2)
                self.vel = pygame.math.Vector2(target_px[0]-self.rect.centerx, target_px[1]-self.rect.centery).normalize() * self.speed

        if self.target_grid:
            move = self.vel * dt
            self.rect.centerx += int(move.x)
            self.rect.centery += int(move.y)
            tx, ty = self.target_grid
            txp = tx * TILE_SIZE + TILE_SIZE//2
            typ = ty * TILE_SIZE + TILE_SIZE//2
            if (self.vel.x > 0 and self.rect.centerx >= txp) or (self.vel.x < 0 and self.rect.centerx <= txp) or (self.vel.y > 0 and self.rect.centery >= typ) or (self.vel.y < 0 and self.rect.centery <= typ):
                self.rect.center = (txp, typ)
                self.target_grid = None
                self.vel = pygame.math.Vector2(0,0)

        # after movement, check for pellet at current grid
        gx, gy = level.pixel_to_grid(self.rect.centerx, self.rect.centery)
        if level.layout[gy][gx] == '.':
            level.layout[gy][gx] = ' '
            self.collected += 1
        if level.layout[gy][gx] == 'O':
            level.layout[gy][gx] = ' '
            self.collected += 5

    def set_skin(self, index):
        self.skin_index = index
        self.image = self._make_image()

    def teleport_to(self, pos):
        # pos expected in pixels; center on tile
        px, py = pos
        cx = (px // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
        cy = (py // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
        self.rect.center = (cx, cy)