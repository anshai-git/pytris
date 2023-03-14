import random
import time
from enum import Enum
import os


def main():
    grid_size = (30, 10)
    game = Game(grid_size)
    # game.run()

    # make this dynamic
    while not game.game_over():
        # validate game by checking if there is anything in the first row
        os.system("clear")
        game.print_map()

        # print(game.in_game_objects[-1].position)
        time.sleep(1)
        # the object for the current iteration is always the last object from the list
        game.in_game_objects[-1].move_down()


class Game:
    # grid_size: tuple of 2 elements: width, height
    def __init__(self, grid_size):
        # TODO:
        # [ ] - validate grid size
        #       it must be at least the size of the smallest object
        self.grid_size = grid_size
        self.grid = [[0] * grid_size[0] for _ in range(grid_size[1])]
        self.in_game_objects = []
        self.in_game_objects.append(object(
            representation=ObjectType(1), starting_position=(0, 0)))

        # absolute dogshit initialization for borders
        top_row = [1 for _ in range(grid_size[0])]
        top_row[:0] = [3]
        top_row.append(4)

        middle_char = 2

        bottom_row = [1 for _ in range(grid_size[0])]
        bottom_row[:0] = [5]
        bottom_row.append(6)

        self.grid_borders = (
            top_row,
            middle_char,
            bottom_row
        )

    def iterate(self):
        # generating new object
        random_object_index = random.choice(range(1, 4))
        object_starting_col_index = random.choice(range(0, self.grid_size[0]))
        starting_position = (0, object_starting_col_index)
        self.in_game_objects += object(
            representation=ObjectType[random_object_index], starting_position=starting_position)

    def run(self):
        self.print_map()

    def print_map(self):
        # print top row
        for c in self.grid_borders[0]:
            print(c, end='')
        print('')

        # print grid content
        for row_index, row in enumerate(self.grid):
            # print left border for each row
            print(self.grid_borders[1], end='')

            # print row
            for col_index, col in enumerate(row):
                # loop through all in game objects
                current_index = (row_index, col_index)
                current_char = 'x' if self.is_any_object_present(
                    current_index) else ' '
                print(current_char, end='')

            # print right border for each row
            print(self.grid_borders[1], end='')
            # print an empty line between rows
            print('')

        # print bottom row
        for c in self.grid_borders[2]:
            print(c, end='')
        print('')

    def generate_random_starting_position_for_object(self):
        return random.choice(range(0, self.grid_size[0]))

    def is_any_object_present(self, current_index):
        # current_index is: (row, col)
        for obj in self.in_game_objects:
            # verify if any of the object is intersecting the current index
            if obj.intersects(current_index):
                return True
        return False

    def game_over(self):
        for col_index in range(self.grid_size[1]):
            if self.grid[0][col_index] is not ' ':
                for row in range(self.grid_size[0]):
                    if self.grid[row][col_index] is ' ':
                        return False
        return True


class object:
    def __init__(self, representation, starting_position):
        self.representation = representation
        self.position = starting_position

    def move_down(self):
        self.position = (self.position[0] + 1, self.position[1])

    # TODO: verify bounds, currently it can move out of the map
    def move_left(self):
        self.position = (self.position[0], self.position[1] - 1)

    # TODO: verify bounds, currently it can move out of the map
    def move_right(self):
        self.position = (self.position[0], self.position[1] + 1)

    def intersects(self, coords):
        # TODO: somehow verify if the position of the current object intersect the coordinates passed
        # if any((c[0] == coords[0] and c[1] == coords[1]) for c in vertical_line(self.position)):
        #     print(vertical_line(self.position))
        return any((c[0] == coords[0] and c[1] == coords[1]) for c in vertical_line(self.position))


# coords: (row, col)
def vertical_line(pos):
    return [
        (pos[0], pos[1]),
        (pos[0] + 1, pos[1]),
        (pos[0] + 2, pos[1])
    ]


class ObjectType(Enum):
    VERTICAL_LINE = 1
    HORIZONTAL_LINE = 2
    BOX = 3
    L_FORM = 4


main()
