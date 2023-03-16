from typing import List, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
import random
import time
import os
import sys
import re
from enum import Enum

T = TypeVar('T')


class Subcommand(ABC):
    @abstractmethod
    def validate():
        pass


class Position:
    def __init__(self, row_index: int, col_index: int) -> None:
        self.row_index = row_index
        self.col_index = col_index


class GridSize(Subcommand):
    def __init__(self) -> None:
        self.name = 'grid_size'
        self.shorthand = 'GS'

    def validate(self, arg_value: str):
        allowed_format = "<width: int><separator: @see allowed_separators><height: int>"
        pattern = r'^(?=[1-9][0-9]{1})(?=[^,x]{0,2}[x,][^,x]{0,2}|[^,x]{0,2}[,][^,x]{0,2})[1-9][0-9]{1}[,x][1-9][0-9]{1}$'
        if re.match(pattern, arg_value):
            values = arg_value.split(arg_value[2])
            return (values[0], values[1]), None
        else:
            return None, f"Invalid value for argument: {self.name}, expected format: {allowed_format} actual value: {arg_value}"


class SubcommandParser:
    def __init__(self, settings: List[Subcommand]) -> None:
        self.settings = settings

    def parse(self, argv_str) -> GameSettings:
        valid_results = []
        pairs = self.parse_to_pairs(argv_str)

        pair_by_validator = self.get_pairs_by_validator(pairs)

        for entry in pair_by_validator:
            print(entry)
            if entry[0] is not None:
                validation = entry[0].value_validator(
                    entry[0].name, entry[1][1])
                match validation:
                    case (_, None):
                        valid_results.append(validation)
                    case _: pass
        return valid_results

    def parse_to_pairs(self, args: List[str]):
        argument_pairs = []
        if len(args) % 2 == 1:
            args.append("_")
        for first, second in zip(args[::2], args[1::2]):
            argument_pairs.append((first, second.replace("_", "")))
        return argument_pairs

    def get_pairs_by_validator(self, pairs: List[tuple[str, None] | tuple[str, str]]):
        result = []
        for idx, pair in enumerate(pairs):
            t = self.find_setting(pair, idx)
            result.append((t[0], pair))
        return result

    def find_setting(self, pair: (tuple[str, None] | tuple[str, str]), index: int) -> (tuple[Subcommand, None] | tuple[None, str]):
        if not pair[0].startswith("--"):
            return None, f"Error parsing argument [{index}] [{pair[0]}]: Argument name must start with: '--'"

        argument_name = pair[0][2:]
        for s in self.settings:
            if s.name == argument_name:
                return s, None
        return None, f"Invalid argument [{index}] [{pair[0]}]"
# ARGUMENT PARSER END


# Arguments:
# grid_size


def main():
    game_settings = SubcommandParser([
        GridSize()
    ]).parse(sys.argv[1:])

    # grid_size = (30, 10)
    # game = Tetris(grid_size)
    # game.start()


# def parse_args(args: List[str]) -> GameSettings:
#     return GameSettings()


class Tetris:
    # grid_size: tuple of 2 elements: width, height
    def __init__(self, grid_size):
        # TODO:
        # [ ] - validate grid size, it must be at least the size of the smallest tetrominoe
        self.grid_size = grid_size
        self.grid = [[0] * grid_size[0] for _ in range(grid_size[1])]
        self.in_game_tetrominoes = []
        # NOTE: find another solution for keeping track of the tetrominoe type
        self.in_game_tetrominoes.append(tetrominoe(
            representation=TetrominoeType(1), starting_position=(0, 0)))

        # absolute dog shit initialization for borders
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

    def start(self):
        # make this dynamic
        while not self.game_over():
            # validate game by checking if there is anything in the first row
            self.render()

            # the tetrominoe for the current iteration is always the last one from the list
            self.in_game_tetrominoes[-1].move_down()

    def iterate(self):
        # generating new tetrominoe
        random_tetrominoe_index = random.choice(range(1, 4))
        tetrominoe_starting_col_index = random.choice(
            range(0, self.grid_size[0]))
        starting_position = (0, tetrominoe_starting_col_index)
        self.in_game_tetrominoes.append(tetrominoe(representation=TetrominoeType(
            random_tetrominoe_index), starting_position=starting_position))

    def do_cycle(self):
        os.system("clear")
        self.render()
        time.sleep(1)

    def render(self):
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
                # loop through all in game tetrominoes
                current_index = (row_index, col_index)
                current_char = 'x' if self.is_any_tetrominoe_intersecting(
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

    def generate_random_starting_position_for_tetrominoe(self):
        return random.choice(range(0, self.grid_size[0]))

    def is_any_tetrominoe_intersecting(self, current_index):
        # current_index is: (row, col)
        for t in self.in_game_tetrominoes:
            # verify if any of the tetrominoe is intersecting the current index
            if t.intersects(current_index):
                return True
        return False

    def game_over(self):
        return False


class tetrominoe:
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
        # TODO: somehow verify if the position of the current tetrominoe intersect the coordinates passed
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


class TetrominoeType(Enum):
    VERTICAL_LINE = 1
    HORIZONTAL_LINE = 2
    BOX = 3
    L_FORM = 4


main()
