from curses import wrapper
import curses
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

        self.screen = screen

    def do_cylce(self):
        while not self.game_over:
            tetromino = Tetromino(self.grid_width)
            can_move = True
            while can_move:
                time.sleep(0.1)
                self.clear_firs_row(tetromino)
                can_move = tetromino.move_down(self.grid_height, self.shadow_grid)
                if not can_move:
                    row = tetromino.position.row
                    col = tetromino.position.col

                    for i in range(row, row + len(tetromino.shape)):
                        for j in range(col, col + len(tetromino.shape[0])):
                            self.shadow_grid[i][j] = tetromino.shape[i - row][j - col] if self.shadow_grid[i][j] == 0 else 1
                self.draw_tetromino(tetromino, self.shadow_grid)

    def render(self):
        # Draw top left corner
        self.screen.addstr(0, 0, self.get_unicode_by_number(3))
        # Draw top border
        for i in range(1, self.grid_width + 1):
            self.screen.addstr(0, i, self.get_unicode_by_number(1))
        # Draw top right corner
        self.screen.addstr(0, self.grid_width + 1, self.get_unicode_by_number(4))

        for i in range(1, self.grid_height + 1):
            # Draw the first character for each row
            self.screen.addstr(i, 0, self.get_unicode_by_number(2))
            # Draw the grid content
            for j in range(1, self.grid_width + 1):
                self.screen.addstr(i, j, ' ')
            # Draw the last character for each row
            self.screen.addstr(i, self.grid_width + 1, self.get_unicode_by_number(2))
        # Draw bottom left corner
        self.screen.addstr(self.grid_height, 0, self.get_unicode_by_number(5))
        # Draw bottom border
        for i in range(1, self.grid_width + 1):
            self.screen.addstr(self.grid_height, i, self.get_unicode_by_number(1))
        self.screen.refresh()
        # Draw bottom right corner
        self.screen.addstr(self.grid_height, self.grid_width + 1, self.get_unicode_by_number(6))

    def draw_tetromino(self, tetromino, shadow_grid):
        row = tetromino.position.row
        col = tetromino.position.col

        # Draw the tetromino by iterating relatively in the grid and relatively in the shape also
        for i in range(row, row + len(tetromino.shape)):
            for j in range(col, col + len(tetromino.shape[0])):
                shape_value = tetromino.shape[i - row][j - col];
                block_char = self.get_unicode_by_number(7)
                match shape_value:
                    case 1:
                        self.screen.addstr(i, j, block_char, tetromino.color)
                    case 0 if shadow_grid[i][j] == 0:
                        self.screen.addstr(i, j, ' ')


        self.screen.refresh()

    def clear_firs_row(self, tetromino):
        if tetromino.position.row > 0:
            for col in range(tetromino.position.col, tetromino.position.col + len(tetromino.shape[0])):
                self.screen.addstr(tetromino.position.row, col, ' ')
            self.screen.refresh()

    def get_random_shape(self):
        return random.choice(shapes)

    def get_unicode_by_number(self, num):
        match num:
            case 1:
                return "\u2500"
            case 2:
                return "\u2502"
            case 3:
                return "\u256D"
            case 4:
                return "\u256E"
            case 5:
                return "\u2570"
            case 6:
                return "\u256F"
            case 7:
                return "\u2588"
            case _:
                return " "

class Tetromino:
    def __init__(self, grid_width) -> None:
        self.shape = random.choice(shapes)
        self.position = Position(1, random.choice(range(1, grid_width - len(self.shape[0]))))
        self.color = curses.color_pair(random.randint(1, 5))

    def move_down(self, grid_height, shadow_grid) -> bool:
        row = self.position.row
        col = self.position.col

        for i in range(row, row + len(self.shape)):
            for j in range(col, col + len(self.shape[0])):
                if self.shape[i - row][j - col] == 1 and shadow_grid[i + 1][j] == 1:
                    return False

        if (row) + len(self.shape) == grid_height:
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
