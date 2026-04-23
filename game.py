import pygame
import sys
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE, FULLSCREEN, WHITE, YELLOW, BLUE
from level import load_levels
from player import Player
from enemy import Enemy
from ui import UI

class Game:
    def __init__(self):
        pygame.init()
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption('Refactored Pac-Like Game')
        self.clock = pygame.time.Clock()
        self.levels = load_levels()
        self.ui = UI(self.screen)
        self.current_level_idx = 0
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

    def run(self):
        # Intro/menu
        lvl_idx = self.ui.selection_menu([f'Level {i+1}' for i in range(len(self.levels))], 'Select Level')
        if lvl_idx is None:
            pygame.quit()
            return
        skin_idx = self.ui.selection_menu(['Yellow', 'Cyan', 'Purple'], 'Select Skin')
        if skin_idx is None:
            pygame.quit()
            return
        self.current_level_idx = lvl_idx
        self.start_level(self.current_level_idx, skin_idx)
        self.loop()

    def start_level(self, idx, skin_idx):
        self.level = self.levels[idx]
        start_px = self.level.player_start if self.level.player_start else (TILE_SIZE*2, TILE_SIZE*2)
        self.player = Player(start_px, skin_idx)
        
        self.all_sprites.empty()
        self.enemies.empty()
        self.all_sprites.add(self.player)
        
        # OPRAVA: Nepřátelé se vytvoří POUZE na pozicích definovaných jako 'E' v level.py
        for i, sp in enumerate(self.level.enemy_spawns):
            kind = i % 5
            e = Enemy(sp, kind)
            self.enemies.add(e)
            self.all_sprites.add(e)

    def loop(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

            # update
            self.player.update(dt, self.level)
            for e in list(self.enemies):
                e.update(dt, self.level, self.player)
                if pygame.sprite.collide_rect(e, self.player):
                    self.ui.show_message(['You were caught! Press any key to quit.'])
                    running = False
            
            # draw centered
            self.screen.fill((4,6,12))
            lx = self.level.width * TILE_SIZE
            ly = self.level.height * TILE_SIZE
            offset_x = max(0, (self.screen.get_width() - lx)//2)
            offset_y = max(0, (self.screen.get_height() - ly)//2)
            self.draw_level(self.level, offset_x, offset_y)
            
            for s in self.all_sprites:
                self.screen.blit(s.image, (s.rect.x + offset_x, s.rect.y + offset_y))
            
            hud = f"Collected: {self.player.collected}  Pellets left: {self.count_pellets()}"
            font = pygame.font.SysFont(None, 28)
            surf = font.render(hud, True, WHITE)
            self.screen.blit(surf, (20,20))
            pygame.display.flip()
        pygame.quit()

    def draw_level(self, level, ox, oy):
        wall_color = (40,120,220)
        for y, row in enumerate(level.layout):
            for x, ch in enumerate(row):
                px = ox + x * TILE_SIZE
                py = oy + y * TILE_SIZE
                if ch == '#':
                    pygame.draw.rect(self.screen, (10,20,60), (px, py, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, wall_color, (px+2, py+2, TILE_SIZE-4, TILE_SIZE-4), 2)
                elif ch == '.':
                    pygame.draw.circle(self.screen, (255,220,100), (px + TILE_SIZE//2, py + TILE_SIZE//2), 3)
                elif ch == 'O':
                    pygame.draw.circle(self.screen, (255,100,120), (px + TILE_SIZE//2, py + TILE_SIZE//2), 6)

    def count_pellets(self):
        return sum(row.count('.') + row.count('O') for row in self.level.layout)