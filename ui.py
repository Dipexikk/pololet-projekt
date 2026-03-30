import pygame
from constants import WHITE, YELLOW

class UI:
    def __init__(self, screen, fonts=None):
        self.screen = screen
        self.font_big = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 28)

    def draw_text(self, text, pos, font=None, color=WHITE):
        if font is None:
            font = self.font
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

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

            # background vignette
            self.screen.fill((8,10,20))
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0,0,0,140), overlay.get_rect())
            self.screen.blit(overlay, (0,0))

            # panel with subtle glow
            pygame.draw.rect(self.screen, (30,40,60), panel_rect, border_radius=12)
            glow = pygame.Surface((panel_rect.width-8, panel_rect.height-8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (100,140,200,40), glow.get_rect(), border_radius=10)
            self.screen.blit(glow, (panel_rect.left+4, panel_rect.top+4))

            title_s = self.font_big.render(title, True, YELLOW)
            tr = title_s.get_rect(center=(panel_rect.centerx, panel_rect.top + 40))
            self.screen.blit(title_s, tr)

            for r, opt in buttons:
                hover = r.collidepoint(mx, my)
                color = (70,130,180) if hover else (50,70,100)
                pygame.draw.rect(self.screen, color, r, border_radius=10)
                # inner lighter bar
                inner = r.inflate(-6, -6)
                pygame.draw.rect(self.screen, (110,160,220,40), inner, border_radius=8)
                txt = self.font.render(opt, True, WHITE)
                tr = txt.get_rect(center=r.center)
                self.screen.blit(txt, tr)
                if hover:
                    # subtle highlight
                    pygame.draw.rect(self.screen, (255,255,255,24), r, border_radius=10)
                if hover and clicked:
                    return buttons.index((r,opt))

            hint = self.font.render("Click to select | Esc to cancel", True, WHITE)
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
            self.screen.fill((0,0,0))
            for i, l in enumerate(lines):
                self.draw_text(l, (50, 50 + i*30), self.font)
            pygame.display.flip()
            clock.tick(10)