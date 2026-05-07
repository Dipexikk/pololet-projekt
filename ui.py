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
        # Load skin images for preview
        self.skin_images = []
        self.skin_names = ['Bejcek', 'Majkl', 'Komi', 'Seda']
        skin_files = [r'imgs/bejcek.png', r'imgs/majkl.png', r'imgs/komi.png', r'imgs/seda.png']
        for skin_file in skin_files:
            try:
                img = pygame.image.load(skin_file).convert_alpha()
                self.skin_images.append(img)
            except Exception:
                self.skin_images.append(None)
        # Load background character image for menu
        self.bg_character = None
        try:
            img = pygame.image.load(r'imgs/background-character.png')
            self.bg_character = img.convert_alpha()
        except Exception:
            self.bg_character = None

    def draw_text(self, text, pos, font=None, color=WHITE):
        if font is None:
            font = self.font
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def _draw_modern_button(self, surface, rect, text, font, hover=False, active=False, animation_time=0):
        """Draw modern dark blue gradient button with rounded corners and animation"""
        # Dark blue color scheme
        if active:
            color_start = (40, 80, 140)
            color_end = (20, 60, 120)
        elif hover:
            # Lighten on hover with animation
            lighten_factor = min(1.0, animation_time * 0.1)
            color_start = (int(40 + 40 * lighten_factor), int(80 + 40 * lighten_factor), int(140 + 40 * lighten_factor))
            color_end = (int(20 + 30 * lighten_factor), int(60 + 30 * lighten_factor), int(120 + 30 * lighten_factor))
        else:
            color_start = (40, 80, 140)
            color_end = (20, 60, 120)
        
        # Draw main button with gradient
        pygame.draw.rect(surface, color_end, rect, border_radius=15)
        inner_rect = pygame.Rect(rect.left + 3, rect.top + 3, rect.width - 6, rect.height - 6)
        pygame.draw.rect(surface, color_start, inner_rect, border_radius=12)
        
        # Add nice border
        border_color = (80, 120, 180) if hover else (60, 100, 160)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)
        
        # Add subtle inner glow on hover
        if hover:
            glow_rect = pygame.Rect(rect.left + 6, rect.top + 6, rect.width - 12, rect.height - 12)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (100, 140, 200, 30), glow_surf.get_rect(), border_radius=9)
            surface.blit(glow_surf, glow_rect)
        
        # Text with shadow and slight animation
        txt = font.render(text, True, WHITE)
        shadow = font.render(text, True, (0, 0, 0))
        shadow_offset = 1 + int(animation_time * 0.5)
        shadow_rect = txt.get_rect(center=(rect.centerx + shadow_offset, rect.centery + shadow_offset))
        surface.blit(shadow, shadow_rect)
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
        # Animation tracking
        hover_times = [0.0] * len(buttons)

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
                self.screen.fill((30, 30, 40))

            # panel with subtle glow
            pygame.draw.rect(self.screen, (20,30,50), panel_rect, border_radius=12)
            glow = pygame.Surface((panel_rect.width-8, panel_rect.height-8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (100,140,200,40), glow.get_rect(), border_radius=10)
            self.screen.blit(glow, (panel_rect.left+4, panel_rect.top+4))

            title_s = self.font_big.render(title, True, YELLOW)
            tr = title_s.get_rect(center=(panel_rect.centerx, panel_rect.top + 40))
            self.screen.blit(title_s, tr)

            for idx, (r, opt) in enumerate(buttons):
                hover = r.collidepoint(mx, my)
                if hover:
                    hover_times[idx] = min(1.0, hover_times[idx] + dt * 4)
                else:
                    hover_times[idx] = max(0.0, hover_times[idx] - dt * 4)
                
                self._draw_modern_button(self.screen, r, opt, self.font, hover=hover, animation_time=hover_times[idx])
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
        w = 550  # Made wider for better title fit
        btn_h = 58
        gap = 16
        panel = pygame.Rect((self.screen.get_width()-w)//2, (self.screen.get_height()-300)//2, w, 300)
        # buttons: Play, Settings, Quit
        btns = [pygame.Rect(panel.left + 40, panel.top + 90 + i*(btn_h+gap), w-80, btn_h) for i in range(3)]
        labels = ['Play', 'Settings', 'Quit']
        # Animation tracking
        hover_times = [0.0] * len(btns)
        
        while True:
            dt = clock.tick(60) / 1000.0
            mx, my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return 'quit'
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
            
            # background: use image if available, otherwise modern fallback
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((20, 20, 30))
            
            # Draw background character on the right side
            if self.bg_character:
                char_height = int(self.screen.get_height())
                char_scale = char_height / self.bg_character.get_height()
                char_width = int(self.bg_character.get_width() * char_scale)
                char_img = pygame.transform.scale(self.bg_character, (char_width, char_height))
                char_x = self.screen.get_width() - char_width
                char_y = self.screen.get_height() - char_height
                self.screen.blit(char_img, (char_x, char_y))

            pygame.draw.rect(self.screen, (20,30,50), panel, border_radius=12)
            # title
            title_str = 'PAC-M´S VS PÉŤABYTE'
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
                if hover:
                    hover_times[i] = min(1.0, hover_times[i] + dt * 4)  # Smooth animation
                else:
                    hover_times[i] = max(0.0, hover_times[i] - dt * 4)
                
                self._draw_modern_button(self.screen, r, labels[i], self.font, hover=hover, animation_time=hover_times[i])
                if hover and clicked:
                    return labels[i].lower()
            pygame.display.flip()

    def show_level_menu(self, options, title='Select Level'):
        # Level menu styled like main menu but with Back button
        clock = pygame.time.Clock()
        w = 520
        btn_h = 54
        gap = 12
        panel = pygame.Rect((self.screen.get_width()-w)//2, 120, w, 120 + (len(options))*(btn_h+gap) + 80)
        btns = [pygame.Rect(panel.left + 40, panel.top + 80 + i*(btn_h+gap), w-80, btn_h) for i in range(len(options))]
        back_btn = pygame.Rect(panel.left + 40, panel.bottom - 60, 120, 44)
        # Animation tracking for all buttons
        hover_times = [0.0] * (len(btns) + 1)  # +1 for back button
        
        while True:
            dt = clock.tick(60) / 1000.0
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
                self.screen.fill((20, 20, 30))
            
            # title centered above panel
            title_s = self.font_big.render(title, True, YELLOW)
            self.screen.blit(title_s, title_s.get_rect(center=(self.screen.get_width()//2, panel.top+32)))
            pygame.draw.rect(self.screen, (20,30,50), panel, border_radius=12)
            
            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                if hover:
                    hover_times[i] = min(1.0, hover_times[i] + dt * 4)
                else:
                    hover_times[i] = max(0.0, hover_times[i] - dt * 4)
                
                self._draw_modern_button(self.screen, r, options[i], self.font, hover=hover, animation_time=hover_times[i])
                if hover and clicked:
                    return i
            
            hoverb = back_btn.collidepoint(mx,my)
            back_idx = len(btns)
            if hoverb:
                hover_times[back_idx] = min(1.0, hover_times[back_idx] + dt * 4)
            else:
                hover_times[back_idx] = max(0.0, hover_times[back_idx] - dt * 4)
            
            self._draw_modern_button(self.screen, back_btn, 'Back', self.font, hover=hoverb, animation_time=hover_times[back_idx])
            if hoverb and clicked:
                return None
            pygame.display.flip()

    def show_settings(self, current_controls='both', current_skin=0):
        clock = pygame.time.Clock()
        w = 700
        panel = pygame.Rect((self.screen.get_width()-w)//2, 80, w, 480)
        # control option rects
        ctrl_opts = ['arrows', 'wasd', 'both']
        ctrl_rects = [pygame.Rect(panel.left+40 + i*200, panel.top+80, 180, 44) for i in range(len(ctrl_opts))]
        skin_rects = [pygame.Rect(panel.left+40 + i*160, panel.top+200, 80, 100) for i in range(4)]
        btn_save = pygame.Rect(panel.centerx-110, panel.bottom-70, 100, 40)
        btn_back = pygame.Rect(panel.centerx+10, panel.bottom-70, 100, 40)
        selected_controls = current_controls
        selected_skin = current_skin
        # Animation tracking
        hover_times = [0.0] * (len(ctrl_rects) + 2)  # controls + save + back
        
        while True:
            dt = clock.tick(60) / 1000.0
            mx,my = pygame.mouse.get_pos()
            clicked = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    clicked = True
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return None
            
            if self.bg_image:
                self.screen.blit(self.bg_image, (0,0))
            else:
                self.screen.fill((20, 20, 30))
            
            pygame.draw.rect(self.screen, (20,30,50), panel, border_radius=12)
            title = self.font_big.render('Settings', True, YELLOW)
            self.screen.blit(title, (panel.left+30, panel.top+20))
            # control choices
            self.draw_text('Controls:', (panel.left+40, panel.top+60), self.font)
            for i, r in enumerate(ctrl_rects):
                hover = r.collidepoint(mx,my)
                active = ctrl_opts[i] == selected_controls
                if hover:
                    hover_times[i] = min(1.0, hover_times[i] + dt * 4)
                else:
                    hover_times[i] = max(0.0, hover_times[i] - dt * 4)
                
                self._draw_modern_button(self.screen, r, ctrl_opts[i].upper(), self.font_small, hover=hover, active=active, animation_time=hover_times[i])
                if hover and clicked:
                    selected_controls = ctrl_opts[i]
            # skins with actual image previews
            self.draw_text('Skins:', (panel.left+40, panel.top+160), self.font)
            for i, r in enumerate(skin_rects):
                hover = r.collidepoint(mx,my)
                active = i == selected_skin
                
                # Border for selection
                if active:
                    pygame.draw.rect(self.screen, (100, 200, 255), r, 3, border_radius=8)
                elif hover:
                    pygame.draw.rect(self.screen, (200, 230, 255), r, 2, border_radius=8)
                else:
                    pygame.draw.rect(self.screen, (60, 80, 120), r, 2, border_radius=8)
                
                # Draw skin image if available
                if self.skin_images[i]:
                    img = pygame.transform.smoothscale(self.skin_images[i], (r.width - 6, r.height - 24))
                    img_rect = img.get_rect(center=(r.centerx, r.centery - 8))
                    self.screen.blit(img, img_rect)
                else:
                    pygame.draw.rect(self.screen, (80, 80, 100), pygame.Rect(r.left+3, r.top+3, r.width-6, r.height-24))
                
                # Skin name
                name_surf = self.font_small.render(self.skin_names[i], True, WHITE)
                name_rect = name_surf.get_rect(center=(r.centerx, r.bottom - 10))
                self.screen.blit(name_surf, name_rect)
                
                if hover and clicked:
                    selected_skin = i
            # buttons
            buttons = [(btn_save, 'Save'), (btn_back, 'Back')]
            for i, (r, label) in enumerate(buttons):
                hover = r.collidepoint(mx,my)
                btn_idx = len(ctrl_rects) + i
                if hover:
                    hover_times[btn_idx] = min(1.0, hover_times[btn_idx] + dt * 4)
                else:
                    hover_times[btn_idx] = max(0.0, hover_times[btn_idx] - dt * 4)
                
                self._draw_modern_button(self.screen, r, label, self.font_small, hover=hover, animation_time=hover_times[btn_idx])
                if hover and clicked:
                    if label == 'Save':
                        return {'controls': selected_controls, 'skin': selected_skin}
                    else:
                        return None
            pygame.display.flip()

    def show_end(self, score):
        clock = pygame.time.Clock()
        w = 520
        panel = pygame.Rect((self.screen.get_width()-w)//2, (self.screen.get_height()-300)//2, w, 260)
        btns = [pygame.Rect(panel.left+40 + i*160, panel.bottom-70, 140, 44) for i in range(3)]
        labels = ['Retry', 'Menu', 'Quit']
        # Animation tracking
        hover_times = [0.0] * len(btns)
        
        while True:
            dt = clock.tick(60) / 1000.0
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
            pygame.draw.rect(self.screen, (40,20,20), panel, border_radius=12)
            title = self.font_big.render('You Died', True, (220,40,60))
            self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top+50)))
            score_txt = self.font.render(f'Score: {score}', True, WHITE)
            self.screen.blit(score_txt, score_txt.get_rect(center=(panel.centerx, panel.top+110)))
            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                if hover:
                    hover_times[i] = min(1.0, hover_times[i] + dt * 4)
                else:
                    hover_times[i] = max(0.0, hover_times[i] - dt * 4)
                
                self._draw_modern_button(self.screen, r, labels[i], self.font_small, hover=hover, animation_time=hover_times[i])
                if hover and clicked:
                    return labels[i].lower()
            pygame.display.flip()

    def show_win(self, score):
        clock = pygame.time.Clock()
        w = 520
        panel = pygame.Rect((self.screen.get_width()-w)//2, (self.screen.get_height()-300)//2, w, 260)
        btns = [pygame.Rect(panel.left+40 + i*160, panel.bottom-70, 140, 44) for i in range(3)]
        labels = ['Replay', 'Menu', 'Quit']
        # Animation tracking
        hover_times = [0.0] * len(btns)
        
        while True:
            dt = clock.tick(60) / 1000.0
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
            pygame.draw.rect(self.screen, (20,40,20), panel, border_radius=12)
            title = self.font_big.render('You Win!', True, (240,220,90))
            self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top+50)))
            score_txt = self.font.render(f'Score: {score}', True, WHITE)
            self.screen.blit(score_txt, score_txt.get_rect(center=(panel.centerx, panel.top+110)))
            for i, r in enumerate(btns):
                hover = r.collidepoint(mx,my)
                if hover:
                    hover_times[i] = min(1.0, hover_times[i] + dt * 4)
                else:
                    hover_times[i] = max(0.0, hover_times[i] - dt * 4)
                
                self._draw_modern_button(self.screen, r, labels[i], self.font_small, hover=hover, animation_time=hover_times[i])
                if hover and clicked:
                    if labels[i].lower() == 'replay':
                        return 'restart'
                    return labels[i].lower()
            pygame.display.flip()