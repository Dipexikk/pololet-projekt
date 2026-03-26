import pygame
import sys
import traceback
import logging
import random
import pickle
import os
from pygame import display, event, draw, time, key, font
from collections import deque
from tkinter import messagebox, Tk

# Nastaveni rozhraní
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 400
FPS = 60
TITLE = "Pac-Man"
TILE_SIZE = 24
GHOST_MOVE_DELAY = 30
PLAYER_MOVE_DELAY = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

logging.basicConfig(filename="game_error.log", level=logging.ERROR)

SAVE_FILE = "save.dat"

# Levely
LEVELS = [
    [
        list("###################"),
        list("#........#........#"),
        list("#.###.###.#.###.#.#"),
        list("#.#.......P.....#.#"),
        list("#.###.#.#####.#.###"),
        list("#.....#...#...#...#"),
        list("#####.###.#.###.###"),
        list("#........G........#"),
        list("###################"),
    ],
    [
        list("#######################"),
        list("#.........#.........#.#"),
        list("#.#####.#.#.#####.#.#.#"),
        list("#.#.....#...#.....#...#"),
        list("#.###.#######.#####.###"),
        list("#...#...P.....#...G...#"),
        list("###.#.###.###.#.###.###"),
        list("#.............G......#"),
        list("#######################"),
    ],
    [
        list("#############################"),
        list("#...........#.............#.#"),
        list("#.#####.###.#.###.#####.###.#"),
        list("#.#.....#.......#.....#.....#"),
        list("#.###.#####.###.#####.###.###"),
        list("#...#...P.....#...G.....#...#"),
        list("###.#.###.###.#.###.###.#.###"),
        list("#.........................G.#"),
        list("#############################"),
    ]
]

fullscreen = True
paused = False
running = True
level_index = 0
MAP = []
player_pos = [0, 0]
ghosts = []
player_direction = [0, 0]
next_direction = [0, 0]
score = 0
max_score = 0
player_timer = 0
ghost_timer = 0

# Funkce
def confirm_exit():
    root = Tk()
    root.withdraw()
    result = messagebox.askyesno("Ukončit", "Opravdu chcete zavřít hru?")
    root.destroy()
    return result

def toggle_fullscreen(screen):
    global fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        return display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        return display.set_mode((WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT), pygame.RESIZABLE)

def safe_quit():
    save_game()
    pygame.quit()
    sys.exit()

def save_game():
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump({"last_level": level_index}, f)

def load_game():
    global level_index
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'rb') as f:
            data = pickle.load(f)
            level_index = data.get("last_level", 0)

def init_level():
    global MAP, player_pos, ghosts, score, max_score, player_direction, next_direction
    MAP = [row[:] for row in LEVELS[level_index]]
    ghosts.clear()
    score = 0
    player_direction = [0, 0]
    next_direction = [0, 0]
    for y, row in enumerate(MAP):
        for x, char in enumerate(row):
            if char == "P":
                player_pos = [x, y]
                MAP[y][x] = " "
            elif char == "G":
                ghosts.append([x, y])
                MAP[y][x] = " "
    max_score = sum(row.count(".") for row in MAP) * 10

def draw_map(screen, scale, font_obj):
    for y, row in enumerate(MAP):
        for x, char in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE * scale, y * TILE_SIZE * scale, TILE_SIZE * scale, TILE_SIZE * scale)
            if char == "#":
                draw.rect(screen, BLUE, rect)
            elif char == ".":
                draw.circle(screen, WHITE, rect.center, int(3 * scale))

    draw.circle(screen, YELLOW, (player_pos[0] * TILE_SIZE * scale + TILE_SIZE//2 * scale, 
                                 player_pos[1] * TILE_SIZE * scale + TILE_SIZE//2 * scale), int(TILE_SIZE//2 * scale))

    for gx, gy in ghosts:
        draw.circle(screen, RED, (gx * TILE_SIZE * scale + TILE_SIZE//2 * scale,
                                  gy * TILE_SIZE * scale + TILE_SIZE//2 * scale), int(TILE_SIZE//2 * scale))

    score_surface = font_obj.render(f"Skóre: {score}", True, WHITE)
    screen.blit(score_surface, (10, 10))

def move_player():
    global player_pos, score
    nx = player_pos[0] + player_direction[0]
    ny = player_pos[1] + player_direction[1]
    if MAP[ny][nx] != "#":
        player_pos = [nx, ny]
        if MAP[ny][nx] == ".":
            MAP[ny][nx] = " "
            score += 10

def bfs(start, goal):
    queue = deque([(start, [])])
    visited = set()
    while queue:
        (current, path) = queue.popleft()
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        x, y = current
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(MAP) and 0 <= nx < len(MAP[0]) and MAP[ny][nx] != "#":
                queue.append(((nx, ny), path + [(nx, ny)]))
    return []

def move_ghosts():
    global ghost_timer
    ghost_timer += 1
    if ghost_timer >= GHOST_MOVE_DELAY:
        for i, (gx, gy) in enumerate(ghosts):
            path = bfs((gx, gy), tuple(player_pos))
            if path:
                ghosts[i] = list(path[0])
        ghost_timer = 0

def check_collision():
    return any(g == player_pos for g in ghosts)

def check_win():
    return score >= max_score

def draw_text_center(surface, text, font_obj, color, y_offset=0):
    width, height = surface.get_size()
    text_surface = font_obj.render(text, True, color)
    rect = text_surface.get_rect(center=(width // 2, height // 2 + y_offset))
    surface.blit(text_surface, rect)

def start_menu(screen):
    fnt = font.SysFont(None, 48)
    load_game()
    selected = level_index
    while True:
        screen.fill(BLACK)
        draw_text_center(screen, "Vyber level (1 - %d): %d" % (len(LEVELS), selected + 1), fnt, YELLOW, -60)
        draw_text_center(screen, "Sipky = zmena levelu | Enter = start | Q = konec", fnt, WHITE, 10)
        display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                safe_quit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    safe_quit()
                elif e.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(LEVELS)
                elif e.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(LEVELS)
                elif e.key == pygame.K_RETURN:
                    return selected

def ask_continue(screen, fnt):
    while True:
        screen.fill(BLACK)
        draw_text_center(screen, "Vyhral jsi level!", fnt, YELLOW, -40)
        draw_text_center(screen, "Enter = dalsi level | Q = konec", fnt, WHITE, 40)
        display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                safe_quit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return True
                elif e.key == pygame.K_q:
                    return False

def main():
    global running, paused, player_direction, next_direction, player_timer, level_index
    try:
        pygame.init()
        screen = display.set_mode((WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT), pygame.RESIZABLE)
        display.set_caption(TITLE)
        clock = time.Clock()
        fnt = font.SysFont(None, 32)

        level_index = start_menu(screen)
        while running:
            init_level()
            win = lose = False
            while not win and not lose:
                for e in event.get():
                    if e.type == pygame.QUIT:
                        if confirm_exit(): safe_quit()
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            if confirm_exit(): safe_quit()
                        elif e.key == pygame.K_RETURN and key.get_mods() & pygame.KMOD_ALT:
                            screen = toggle_fullscreen(screen)
                        elif e.key == pygame.K_s and key.get_mods() & pygame.KMOD_CTRL:
                            save_game()
                        elif e.key in [pygame.K_UP, pygame.K_w]: next_direction = [0, -1]
                        elif e.key in [pygame.K_DOWN, pygame.K_s]: next_direction = [0, 1]
                        elif e.key in [pygame.K_LEFT, pygame.K_a]: next_direction = [-1, 0]
                        elif e.key in [pygame.K_RIGHT, pygame.K_d]: next_direction = [1, 0]
                    elif e.type == pygame.WINDOWMINIMIZED:
                        paused = True
                    elif e.type == pygame.WINDOWRESTORED:
                        paused = False

                if paused:
                    continue

                width, height = screen.get_size()
                scale = min(width / (TILE_SIZE * len(MAP[0])), height / (TILE_SIZE * len(MAP)))
                screen.fill(BLACK)

                nx, ny = player_pos[0] + next_direction[0], player_pos[1] + next_direction[1]
                if MAP[ny][nx] != "#":
                    player_direction = next_direction

                player_timer += 1
                if player_timer >= PLAYER_MOVE_DELAY:
                    move_player()
                    player_timer = 0

                move_ghosts()
                if check_collision(): lose = True
                if check_win(): win = True

                draw_map(screen, scale, fnt)
                display.flip()
                clock.tick(FPS)

            if win:
                if level_index + 1 < len(LEVELS):
                    if ask_continue(screen, fnt):
                        level_index += 1
                        save_game()
                        continue
                draw_text_center(screen, "Dokoncil jsi vsechny levely!", fnt, YELLOW)
                display.flip()
                time.delay(2000)
                break
            if lose:
                draw_text_center(screen, "Prohral jsi!", fnt, RED)
                display.flip()
                time.delay(2000)
                break
    except Exception as e:
        logging.error("Unhandled exception:\n" + traceback.format_exc())
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
