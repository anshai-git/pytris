from curses import wrapper
import curses
import random
import time

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
         [0,1,0]]
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
        self.grid_width = 70
        self.grid_height = 40
        self.screen = curses.initscr()
        self.screen.keypad(True)
        self.game_over = False
        curses.noecho()
        curses.cbreak()
        self.screen = screen

    def do_cylce(self):
        while not self.game_over:
            tetromino = Tetromino(self.grid_width)
            can_move = True
            while can_move:
                time.sleep(0.8)
                self.clear_firs_row(tetromino)
                self.draw_tetromino(tetromino)
                can_move = tetromino.move_down(self.grid_height)

    def render(self):
        # Draw top border
        for i in range(0, self.grid_width + 2):
            self.screen.addstr(0, i, '-')
        for i in range(1, self.grid_height + 1):
            # Draw the first character for each row
            self.screen.addstr(i, 0, '|')
            # Draw the grid content
            for j in range(1, self.grid_width + 1):
                self.screen.addstr(i, j, ' ')
            # Draw the last character for each row
            self.screen.addstr(i, self.grid_width + 1, '|')
        # Draw bottom border
        for i in range(self.grid_width + 2):
            self.screen.addstr(self.grid_height + 1, i, '-')
        self.screen.refresh()

    def draw_tetromino(self, tetromino):
        row = tetromino.position.row
        col = tetromino.position.col

        # Draw the tetromino by iterating relatively in the grid and relatively in the shape also
        for i in range(row, row + len(tetromino.shape)):
            for j in range(col, col + len(tetromino.shape[0])):
                self.screen.addstr(i, j, str(tetromino.shape[i - (row + len(tetromino.shape))][j - (col + len(tetromino.shape[0]))]))
        self.screen.refresh()

    def clear_firs_row(self, tetromino):
        if tetromino.position.row - 1 > 0:
            for col in range(tetromino.position.col, tetromino.position.col + len(tetromino.shape[0])):
                self.screen.addstr(tetromino.position.row - 1, col, ' ')
            self.screen.refresh()

    def get_random_shape(self):
        return random.choice(shapes)

class Tetromino:
    def __init__(self, grid_width) -> None:
        self.shape = random.choice(shapes)
        self.position = Position(1, random.choice(range(1, grid_width - len(self.shape[0]))))

    def move_down(self, grid_height) -> bool:
        # TODO: contune here: check for intersections / collissions between objects while moving down
        if ((self.position.row) + 1 == grid_height) or ():
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
