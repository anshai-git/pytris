from curses import wrapper
import curses
from enum import Enum
import random
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('mylog.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

shapes = [
        # Box
        [[1,1],
         [1,1]],
        # L
        [[1,0],
         [1,0],
         [1,1]],
        # Horizontal line
        [[1],
         [1],
         [1]],
        # Vertical line
        [[1,1,1]],
        # T
        [[1,1,1],
         [0,1,0],
         [0,1,0]],
        # S
        [[0,1,1],
         [0,1,0],
         [1,1,0]],
        # Z
        [[1,1,0],
         [0,1,0],
         [0,1,1]]
]

class UnicodeCharacters:
        HORIZONTAL_LINE = "\u2500"
        VERTICAL_LINE = "\u2502"
        TOP_LEFT_CORNER = "\u256D"
        TOP_RIGHT_CORNER = "\u256E"
        BOTTOM_LEFT_CORNER = "\u2570"
        BOTTOM_RIGHT_CORNER = "\u256F"
        FILLED_BLOCK = "\u2588"

def main(screen):
    game = Tetris(screen)
    game.render()
    game.do_cylce()
    game.screen.getkey()
    
    # End
    curses.endwin()

class Tetris:
    def __init__(self, screen) -> None:
        self.grid_width = 40
        self.grid_height = 20
        self.screen = curses.initscr()
        self.screen.keypad(True)
        self.in_game_objects = []
        self.game_over = False
        self.shadow_grid = [[0 for _ in range(self.grid_width + 2)] for _ in range(self.grid_height + 2)]
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        self.screen = screen

    def do_cylce(self):
        while not self.game_over:
            tetromino = Tetromino(self.grid_width)
            can_move = True
            while can_move:
                time.sleep(0.1)
                self.clear_first_row(tetromino)
                can_move = tetromino.move_down(self.grid_height, self.shadow_grid)
                if not can_move:
                    row = tetromino.position.row
                    col = tetromino.position.col

                    for i in range(row, row + len(tetromino.shape)):
                        for j in range(col, col + len(tetromino.shape[0])):
                            self.shadow_grid[i][j] = tetromino.shape[i - row][j - col] if self.shadow_grid[i][j] == 0 else 1
                self.draw_tetromino(tetromino, self.shadow_grid)

    def render(self):
        draw = self.screen.addstr

        draw(0, 0, UnicodeCharacters.TOP_LEFT_CORNER)
        for i in range(1, self.grid_width + 1):
            draw(0, i, UnicodeCharacters.HORIZONTAL_LINE)
        draw(0, self.grid_width + 1, UnicodeCharacters.TOP_RIGHT_CORNER)

        for i in range(1, self.grid_height + 1):
            draw(i, 0, UnicodeCharacters.VERTICAL_LINE)
            for j in range(1, self.grid_width + 1):
                draw(i, j, ' ')
            draw(i, self.grid_width + 1, UnicodeCharacters.VERTICAL_LINE)
        draw(self.grid_height, 0, UnicodeCharacters.BOTTOM_LEFT_CORNER)
        for i in range(1, self.grid_width + 1):
            draw(self.grid_height, i, UnicodeCharacters.HORIZONTAL_LINE)
        self.screen.refresh()
        draw(self.grid_height, self.grid_width + 1, UnicodeCharacters.BOTTOM_RIGHT_CORNER)

    def draw_tetromino(self, tetromino, shadow_grid):
        row = tetromino.position.row
        col = tetromino.position.col
        draw = self.screen.addstr

        for i in range(row, row + len(tetromino.shape)):
            for j in range(col, col + len(tetromino.shape[0])):
                match tetromino.shape[i - row][j - col]:
                    case 1:
                        draw(i, j, UnicodeCharacters.FILLED_BLOCK, tetromino.color)
                    case 0 if shadow_grid[i][j] == 0:
                        draw(i, j, ' ')

        self.screen.refresh()

    def clear_first_row(self, tetromino):
        col = tetromino.position.col
        row = tetromino.position.row
        draw = self.screen.addstr

        if tetromino.position.row > 0:
            for col in range(col, col + len(tetromino.shape[0])):
                draw(row, col, ' ')
            self.screen.refresh()

class Tetromino:
    def __init__(self, grid_width) -> None:
        self.shape = random.choice(shapes)
        self.position = Position(1, random.choice(range(1, grid_width - len(self.shape[0]))))
        self.color = curses.color_pair(random.randint(1, 7))

    def move_down(self, grid_height, shadow_grid) -> bool:
        for i in range(len(self.shape)):
            for j in range(len(self.shape[0])):
                if self.shape[i][j] == 1 and shadow_grid[i + self.position.row + 1][j + self.position.col] == 1:
                    return False

        if (self.position.row) + len(self.shape) == grid_height:
            return False
        else:
            self.position.row += 1
            return True

    def move_right(self):
        # TODO: contune here: check for intersections / collissions between objects while moving right
        self.position.col += 1

    def move_left(self):
        # TODO: contune here: check for intersections / collissions between objects while moving left
        self.position.col -= 1

class Position:
    def __init__(self, row, col) -> None:
        self.row = row
        self.col = col

# startup
wrapper(main)
