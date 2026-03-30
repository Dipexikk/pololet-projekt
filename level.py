from constants import TILE_SIZE

class Level:
    """Represent a game level. Tile map uses:
    '#' - wall
    '.' - pellet
    ' ' - empty
    'P' - player start
    'E' - enemy spawn
    'O' - power pellet
    """

    def __init__(self, layout):
        maxw = max(len(r) for r in layout)
        # pad rows to same width
        self.layout = [list(r.ljust(maxw)) for r in layout]
        self.height = len(self.layout)
        self.width = maxw
        self.player_start = None
        self.enemy_spawns = []
        self.pellet_count = 0
        self._analyze()

    def _analyze(self):
        for y, row in enumerate(self.layout):
            for x, ch in enumerate(row):
                if ch == 'P':
                    self.player_start = (x * TILE_SIZE, y * TILE_SIZE)
                    self.layout[y][x] = ' '
                elif ch == 'E':
                    self.enemy_spawns.append((x * TILE_SIZE, y * TILE_SIZE))
                    self.layout[y][x] = ' '
                elif ch == '.':
                    self.pellet_count += 1
                elif ch == 'O':
                    self.pellet_count += 1

    def is_wall(self, grid_x, grid_y):
        if grid_y < 0 or grid_y >= self.height or grid_x < 0 or grid_x >= len(self.layout[grid_y]):
            return True
        return self.layout[grid_y][grid_x] == '#'

    def grid_to_pixel(self, gx, gy):
        return gx * TILE_SIZE, gy * TILE_SIZE

    def pixel_to_grid(self, px, py):
        return px // TILE_SIZE, py // TILE_SIZE

    def neighbors(self, gx, gy):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = gx+dx, gy+dy
            if 0 <= ny < self.height and 0 <= nx < self.width and self.layout[ny][nx] != '#':
                yield nx, ny


# New larger neon-style levels
def load_levels():
    level1 = [
        "############################################",
        "#P......#...........##...........#........P#",
        "#.#######.#####.#####.#####.#####.#######..#",
        "#.#.....#.....#.#...#.#...#.#...#.#.....#..#",
        "#.#.###.#####.#.#.#.#.#.#.#.#.#.#.#####.#..#",
        "#...#.#.......#...#...#...#...#.....#.#...#",
        "###.#.#.#############################.#.###",
        "#...#...#........E...........#.......#....#",
        "#.#.#####.###.###########.###.#####.###.##.#",
        "#.#.......#.#...........#.#.....#...#....#",
        "#.#.#####.#.###########.#.#####.#.###.####.#",
        "#....E.........................E.........#",
        "############################################",
    ]

    level2 = [
        "################################################",
        "#P....#...........#.....#...........#....#...P#",
        "#.##.#.#.#####.###.#.###.#.#####.###.#.#.#.##.#",
        "#.#..#.#.....#...#.#.#.#.#.....#...#.#.#.#..#",
        "#.#.##.#####.###.#.#.#.#.#.###.###.#.#.#.##.#",
        "#......#...........#.....#...........#......#",
        "#.####.#.#############################.####..#",
        "#......#....E.....#.....#.....E....#..#.....#",
        "###.#####.###.###########.###.#####.###.#####",
        "#............#...........#...........#......#",
        "#.#.#####.#.#.#####.#####.#.#####.#.#.#####.#",
        "#E#.....#.#.#.....#.....#.#.....#.#.#.....#E#",
        "################################################",
    ]

    level3 = [
        "################################################",
        "#P..O...#...###....#....###....#...#...O...P..#",
        "#.#.###.#.#.#.#.##.#.##.#.#.#.#.#.#.###.###..#",
        "#.#...#...#.#...#..#..#...#.#...#..#...#....#",
        "#.###.#####.###.#########.###.#####.###.###.#",
        "#......#........E...............E......#....#",
        "#.####.#.###.###########.###.###.#.####.####.#",
        "#......#.....#.....#.....#.....#.....#......#",
        "#E#########################################E#",
        "#............................................#",
        "################################################",
    ]

    return [Level(level1), Level(level2), Level(level3)]