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
        # player options
        self.options = {'controls': 'both', 'skin': 0}

    def run(self):
        while True:
            choice = self.ui.show_main_menu()
            if choice == 'quit':
                pygame.quit()
                return
            if choice == 'settings':
                res = self.ui.show_settings(self.options['controls'], self.options['skin'])
                if res:
                    self.options.update(res)
                continue
            if choice == 'play':
                # show levels list using the new level menu
                lvl_idx = self.ui.show_level_menu([f'Level {i+1}' for i in range(len(self.levels))], 'Select Level')
                if lvl_idx is None:
                    # back pressed
                    continue
                # use current options
                action = self.start_and_play(lvl_idx, self.options['skin'], self.options['controls'])
                if action == 'quit':
                    pygame.quit()
                    return
                # if menu, loop back, if restart, restart same level
                if action == 'restart':
                    continue
                if action == 'menu':
                    continue

    def start_and_play(self, idx, skin_idx, controls):
        self.start_level(idx, skin_idx, controls)
        return self.loop()

    def start_level(self, idx, skin_idx, controls):
        self.level = self.levels[idx]
        start_px = self.level.player_start if self.level.player_start else (TILE_SIZE*2, TILE_SIZE*2)
        self.player = Player(start_px, skin_idx, controls)
        
        self.all_sprites.empty()
        self.enemies.empty()
        self.all_sprites.add(self.player)
        
        # OPRAVA: Nepřátelé se vytvoří POUZE na pozicích definovaných jako 'E' v level.py
        for i, sp in enumerate(self.level.enemy_spawns):
            kind = i % 5
            e = Enemy(sp, kind)
            self.enemies.add(e)
            self.all_sprites.add(e)
        # remember initial pellet total
        self.initial_pellets = self.level.pellet_count

    def loop(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

            # update
            self.player.update(dt, self.level)
            for e in list(self.enemies):
                e.update(dt, self.level, self.player)
                if pygame.sprite.collide_rect(e, self.player):
                    choice = self.ui.show_end(self.player.collected)
                    if choice == 'retry' or choice == 'restart':
                        return 'restart'
                    if choice == 'menu':
                        return 'menu'
                    return 'quit'
            
            # win condition: when collected pellets equals initial pellet count
            if self.player.collected >= getattr(self, 'initial_pellets', self.level.pellet_count):
                choice = self.ui.show_win(self.player.collected)
                if choice == 'restart':
                    return 'restart'
                if choice == 'menu':
                    return 'menu'
                return 'quit'
            
            # draw centered and scaled to fit the screen
            self.screen.fill((4,6,12))
            level_pixel_w = self.level.width * TILE_SIZE
            level_pixel_h = self.level.height * TILE_SIZE
            sw, sh = self.screen.get_size()
            # compute scale to fit level to screen (preserve aspect)
            scale = min(sw / level_pixel_w, sh / level_pixel_h)
            if scale <= 0:
                scale = 1.0
            scaled_w = int(level_pixel_w * scale)
            scaled_h = int(level_pixel_h * scale)
            offset_x = max(0, (self.screen.get_width() - scaled_w)//2)
            offset_y = max(0, (self.screen.get_height() - scaled_h)//2)
            # draw level with scale
            self.draw_level(self.level, offset_x, offset_y, scale)
            
            # draw sprites scaled and positioned according to scale
            for s in self.all_sprites:
                # prefer using high-quality base_image if available
                base = getattr(s, 'base_image', s.image)
                # target size based on tile size to keep consistent proportions
                target_w = int((TILE_SIZE - 4) * scale)
                target_h = int((TILE_SIZE - 4) * scale)
                sw_img = max(1, target_w)
                sh_img = max(1, target_h)
                # scale smoothly
                img = pygame.transform.smoothscale(base, (sw_img, sh_img))
                # apply rotation if sprite provides a render_angle (degrees)
                angle = getattr(s, 'render_angle', 0.0)
                if angle:
                    img = pygame.transform.rotozoom(img, angle, 1.0)
                # center the drawn image on the sprite rect position
                draw_x = int(offset_x + s.rect.centerx * scale - img.get_width()//2)
                draw_y = int(offset_y + s.rect.centery * scale - img.get_height()//2)
                self.screen.blit(img, (draw_x, draw_y))
            
            pellets_left = max(0, getattr(self, 'initial_pellets', self.level.pellet_count) - self.player.collected)
            hud = f"Score: {self.player.score}   Collected: {self.player.collected}   Pellets left: {pellets_left}"
            font = pygame.font.SysFont(None, 28)
            surf = font.render(hud, True, WHITE)
            self.screen.blit(surf, (20,20))
            pygame.display.flip()
        return 'quit'

    def draw_level(self, level, ox, oy, scale=1.0):
        wall_color = (40,120,220)
        # scaled tile size
        tile_s = max(1, int(TILE_SIZE * scale))
        inner_border = max(1, int(2 * scale))
        for y, row in enumerate(level.layout):
            for x, ch in enumerate(row):
                px = ox + int(x * TILE_SIZE * scale)
                py = oy + int(y * TILE_SIZE * scale)
                if ch == '#':
                    pygame.draw.rect(self.screen, (10,20,60), (px, py, tile_s, tile_s))
                    pygame.draw.rect(self.screen, wall_color, (px+inner_border, py+inner_border, max(1, tile_s-2*inner_border), max(1, tile_s-2*inner_border)), inner_border)
                elif ch == '.':
                    center = (px + tile_s//2, py + tile_s//2)
                    radius = max(1, int(3 * scale))
                    pygame.draw.circle(self.screen, (255,220,100), center, radius)
                elif ch == 'O':
                    # power pellet visual with glow ring
                    center = (px + tile_s//2, py + tile_s//2)
                    radius = max(1, int(6 * scale))
                    pygame.draw.circle(self.screen, (255,100,120), center, radius)
                    ring = pygame.Surface((tile_s, tile_s), pygame.SRCALPHA)
                    pygame.draw.circle(ring, (255,150,160,80), (tile_s//2, tile_s//2), max(1, int(10 * scale)))
                    self.screen.blit(ring, (px, py))

    def count_pellets(self):
        return sum(row.count('.') + row.count('O') for row in self.level.layout)