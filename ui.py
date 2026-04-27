import pygame
from constants import WHITE, YELLOW

class UI:
    def __init__(self, screen, fonts=None):
        self.screen = screen
        self.font_big = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)
        # try loading menu background image from imgs/menu-background.png
        self.bg_image = None
        try:
            img = pygame.image.load(r'imgs/menu-background.png')
            self.bg_image = pygame.transform.scale(img.convert(), (self.screen.get_width(), self.screen.get_height()))
        except Exception:
            self.bg_image = None

    def draw_text(self, text, pos, font=None, color=WHITE):
        if font is None:
            font = self.font
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def _draw_wood_button(self, surface, rect, text, font, hover=False):
        # shadow
        shadow_rect = rect.move(4, 6)
        pygame.draw.rect(surface, (10, 10, 10), shadow_rect, border_radius=8)
        # main wooden slab
        main_color = (160, 110, 60) if not hover else (190, 130, 70)
        border_color = (100, 60, 30)
        pygame.draw.rect(surface, main_color, rect, border_radius=8)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=8)
        # light top band (semi-transparent)
        top_band = pygame.Rect(rect.left+4, rect.top+4, rect.width-8, rect.height//3)
        band_surf = pygame.Surface((top_band.width, top_band.height), pygame.SRCALPHA)
        band_surf.fill((220,190,140,40))
        surface.blit(band_surf, (top_band.left, top_band.top))
        txt = font.render(text, True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    def selection_menu(self, options, title):
        # central modern panel
        clock = pygame.time.Clock()
        w = 600
        hbtn = 64
        gap = 12
        panel_rect = pygame.Rect((self.screen.get_width()-w)//2, 140, w, 120 + len(options)*(hbtn+gap))
        buttons = []
        for i, opt in enumerate(options):
            r = pygame.Rect(panel_rect.left + 40, panel_rect.top + 80 + i*(hbtn+gap), w-80, hbtn)
            buttons.append((r, opt))

        while True:
            dt = clock.tick(60) / 1000.0
            mx, my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return None
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True

            # background - image if available else tiled fallback
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((30, 30, 30))
                tile = pygame.Surface((32,32))
                tile.fill((90, 70, 50))
                for x in range(0, self.screen.get_width(), 32):
                    for y in range(0, self.screen.get_height(), 32):
                        self.screen.blit(tile, (x, y))

            # panel with subtle glow
            pygame.draw.rect(self.screen, (20,30,40), panel_rect, border_radius=12)
            glow = pygame.Surface((panel_rect.width-8, panel_rect.height-8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (100,140,200,40), glow.get_rect(), border_radius=10)
            self.screen.blit(glow, (panel_rect.left+4, panel_rect.top+4))

            title_s = self.font_big.render(title, True, YELLOW)
            tr = title_s.get_rect(center=(panel_rect.centerx, panel_rect.top + 40))
            self.screen.blit(title_s, tr)

            for idx, (r, opt) in enumerate(buttons):
                hover = r.collidepoint(mx, my)
                self._draw_wood_button(self.screen, r, opt, self.font, hover=hover)
                if hover and clicked:
                    return idx

            hint = self.font_small.render("Click to select | Esc to cancel", True, WHITE)
            self.screen.blit(hint, (panel_rect.left + 20, panel_rect.bottom - 30))
            pygame.display.flip()

    def show_message(self, lines):
        waiting = True
        clock = pygame.time.Clock()
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                    return
            # dim background and draw centered box
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            self.screen.blit(overlay, (0,0))
            for i, l in enumerate(lines):
                self.draw_text(l, (50, 50 + i*30), self.font)
            pygame.display.flip()
            clock.tick(10)

    def show_main_menu(self):
        clock = pygame.time.Clock()
        w = 480
        btn_h = 58
        gap = 16
        panel = pygame.Rect((self.screen.get_width()-w)//2, (self.screen.get_height()-300)//2, w, 300)
        # buttons: Play, Settings, Quit
        btns = [pygame.Rect(panel.left + 40, panel.top + 90 + i*(btn_h+gap), w-80, btn_h) for i in range(3)]
        labels = ['Play', 'Settings', 'Quit']
        while True:
            mx, my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return 'quit'
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
            # background: use image if available, otherwise tiled fallback
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((30,30,30))
                tile = pygame.Surface((32,32))
                tile.fill((100,80,50))
                for x in range(0, self.screen.get_width(), 32):
                    for y in range(0, self.screen.get_height(), 32):
                        self.screen.blit(tile, (x,y))

            pygame.draw.rect(self.screen, (20,30,40), panel, border_radius=12)
            # title
            title_str = 'PACMAN ON CRACK'
            x = self.screen.get_width()//2
            y = panel.top + 30
            colors = [(240,80,80),(240,160,80),(240,220,80),(120,200,120),(80,180,240),(160,120,240)]
            total_w = 0
            chars = []
            for i, ch in enumerate(title_str):
                font = pygame.font.SysFont(None, 64)
                surf = font.render(ch, True, colors[i % len(colors)])
                chars.append((surf, surf.get_rect()))
                total_w += surf.get_width()
            start_x = x - total_w//2
            cur_x = start_x
            for surf, rect in chars:
                rect.center = (cur_x + surf.get_width()//2, y)
                self.screen.blit(surf, rect)
                cur_x += surf.get_width()

            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                self._draw_wood_button(self.screen, r, labels[i], self.font, hover=hover)
                if hover and clicked:
                    return labels[i].lower()
            pygame.display.flip()
            clock.tick(60)

    def show_level_menu(self, options, title='Select Level'):
        # Level menu styled like main menu but with Back button
        clock = pygame.time.Clock()
        w = 520
        btn_h = 54
        gap = 12
        panel = pygame.Rect((self.screen.get_width()-w)//2, 120, w, 120 + (len(options))*(btn_h+gap) + 80)
        btns = [pygame.Rect(panel.left + 40, panel.top + 80 + i*(btn_h+gap), w-80, btn_h) for i in range(len(options))]
        back_btn = pygame.Rect(panel.left + 40, panel.bottom - 60, 120, 44)
        while True:
            mx,my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return None
            # background
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((28,28,28))
                tile = pygame.Surface((32,32))
                tile.fill((100,80,50))
                for x in range(0, self.screen.get_width(), 32):
                    for y in range(0, self.screen.get_height(), 32):
                        self.screen.blit(tile, (x,y))
            # title centered above panel
            title_s = self.font_big.render(title, True, YELLOW)
            self.screen.blit(title_s, title_s.get_rect(center=(self.screen.get_width()//2, panel.top+32)))
            pygame.draw.rect(self.screen, (20,30,40), panel, border_radius=12)
            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                self._draw_wood_button(self.screen, r, options[i], self.font, hover=hover)
                if hover and clicked:
                    return i
            hoverb = back_btn.collidepoint(mx,my)
            self._draw_wood_button(self.screen, back_btn, 'Back', self.font, hover=hoverb)
            if hoverb and clicked:
                return None
            pygame.display.flip()
            clock.tick(60)

    def show_settings(self, current_controls='both', current_skin=0):
        clock = pygame.time.Clock()
        w = 640
        panel = pygame.Rect((self.screen.get_width()-w)//2, 120, w, 380)
        # control option rects
        ctrl_opts = ['arrows', 'wasd', 'both']
        ctrl_rects = [pygame.Rect(panel.left+40 + i*200, panel.top+80, 180, 44) for i in range(len(ctrl_opts))]
        skin_rects = [pygame.Rect(panel.left+40 + i*200, panel.top+160, 44, 44) for i in range(3)]
        btn_save = pygame.Rect(panel.centerx-110, panel.bottom-70, 100, 40)
        btn_back = pygame.Rect(panel.centerx+10, panel.bottom-70, 100, 40)
        selected_controls = current_controls
        selected_skin = current_skin
        while True:
            mx,my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
            self.screen.fill((28,28,28))
            pygame.draw.rect(self.screen, (20,30,40), panel, border_radius=12)
            title = self.font_big.render('Settings', True, YELLOW)
            self.screen.blit(title, (panel.left+30, panel.top+20))
            # control choices
            self.draw_text('Controls:', (panel.left+40, panel.top+60), self.font)
            for i, r in enumerate(ctrl_rects):
                hover = r.collidepoint(mx,my)
                color = (90,90,90) if ctrl_opts[i] != selected_controls else (150,120,60)
                pygame.draw.rect(self.screen, color, r, border_radius=8)
                txt = self.font.render(ctrl_opts[i].upper(), True, WHITE)
                self.screen.blit(txt, txt.get_rect(center=r.center))
                if hover and clicked:
                    selected_controls = ctrl_opts[i]
            # skins
            self.draw_text('Skin:', (panel.left+40, panel.top+140), self.font)
            for i, r in enumerate(skin_rects):
                color = (200,180,120) if i == selected_skin else (120,100,70)
                pygame.draw.rect(self.screen, color, r, border_radius=6)
                # simple circle preview
                pygame.draw.circle(self.screen, [(255,255,0),(0,200,200),(200,100,255)][i], r.center, 14)
                if r.collidepoint(mx,my) and clicked:
                    selected_skin = i
            # buttons
            for r, label in [(btn_save, 'Save'), (btn_back, 'Back')]:
                hover = r.collidepoint(mx,my)
                color = (140,120,80) if hover else (100,80,60)
                pygame.draw.rect(self.screen, color, r, border_radius=8)
                txt = self.font.render(label, True, WHITE)
                self.screen.blit(txt, txt.get_rect(center=r.center))
                if hover and clicked:
                    if label == 'Save':
                        return {'controls': selected_controls, 'skin': selected_skin}
                    else:
                        return None
            pygame.display.flip()
            clock.tick(60)

    def show_end(self, score):
        clock = pygame.time.Clock()
        w = 520
        panel = pygame.Rect((self.screen.get_width()-w)//2, (self.screen.get_height()-300)//2, w, 260)
        btns = [pygame.Rect(panel.left+40 + i*160, panel.bottom-70, 140, 44) for i in range(3)]
        labels = ['Retry', 'Menu', 'Quit']
        while True:
            mx,my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return 'quit'
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((5,5,10))
            pygame.draw.rect(self.screen, (20,20,24), panel, border_radius=12)
            title = self.font_big.render('You Died', True, (220,40,60))
            self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top+50)))
            score_txt = self.font.render(f'Score: {score}', True, WHITE)
            self.screen.blit(score_txt, score_txt.get_rect(center=(panel.centerx, panel.top+110)))
            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                self._draw_wood_button(self.screen, r, labels[i], self.font, hover=hover)
                if hover and clicked:
                    return labels[i].lower()
            pygame.display.flip()
            clock.tick(60)

    def show_win(self, score):
        clock = pygame.time.Clock()
        w = 520
        panel = pygame.Rect((self.screen.get_width()-w)//2, (self.screen.get_height()-300)//2, w, 260)
        btns = [pygame.Rect(panel.left+40 + i*160, panel.bottom-70, 140, 44) for i in range(3)]
        labels = ['Replay', 'Menu', 'Quit']
        while True:
            mx,my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return 'quit'
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((6,20,6))
            pygame.draw.rect(self.screen, (20,30,20), panel, border_radius=12)
            title = self.font_big.render('You Win!', True, (240,220,90))
            self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top+50)))
            score_txt = self.font.render(f'Score: {score}', True, WHITE)
            self.screen.blit(score_txt, score_txt.get_rect(center=(panel.centerx, panel.top+110)))
            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                self._draw_wood_button(self.screen, r, labels[i], self.font, hover=hover)
                if hover and clicked:
                    if labels[i].lower() == 'replay':
                        return 'restart'
                    return labels[i].lower()
            pygame.display.flip()
            clock.tick(60)