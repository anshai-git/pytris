from typing import List, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
import random
import time
import os
import sys
import re
from enum import Enum
import logging
import asyncio
import keyboard
import queue

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('logs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

class Movement(Enum):
    LEFT = 1,
    RIGHT = 2

movements = queue.Queue()

async def read_input():
    while True:
        if keyboard.is_pressed('l'):
            movements.put(Movement.RIGHT)
        if keyboard.is_pressed('h'):
            movements.put(Movement.LEFT)
        await asyncio.sleep(0.1)

async def run_tetris():
    grid_size = (30, 10)
    game = Tetris(grid_size)
    await game.start()

async def main():
    listen_for_keypress = asyncio.create_task(read_input())
    run_game = asyncio.create_task(run_tetris())
    await asyncio.wait([listen_for_keypress, run_game], return_when=asyncio.FIRST_COMPLETED)


class Tetris:
    # grid_size: tuple of 2 elements: width, height
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = [[0] * grid_size[0] for _ in range(grid_size[1])]
        self.in_game_tetrominoes = []

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

    async def start(self):
        # while not self.game_over():
        iterations = 20
        while iterations > 0:
            position = (0, random.choice(range(1, self.grid_size[0])))
            next_piece = self.generate_tetrominoe(position)
            self.in_game_tetrominoes.append(next_piece)
            await self.do_cycle()
            iterations -= 1

    async def do_cycle(self):
            can_move = True
            while can_move:
                os.system("clear")
                self.render()
                await asyncio.sleep(0.3)
                tetrominoe = self.in_game_tetrominoes[-1]
                while not movements.empty():
                    match movements.get():
                        case Movement.LEFT:
                            tetrominoe.move_left()
                        case Movement.RIGHT:
                            tetrominoe.move_right()
                        case _:
                            pass
                can_move = tetrominoe.position[0] + tetrominoe.height() < self.grid_size[1] and tetrominoe.move_down(self.in_game_tetrominoes[:-1])

    def render(self):
        # print top row
        for c in self.grid_borders[0]:
            uc_char = self.get_unicode_char_by_number(c)
            print(uc_char, end='')
        print('')

        # print grid content
        for row_index, row in enumerate(self.grid):
            # print left border for each row
            border_char = self.grid_borders[1]
            uc_char = self.get_unicode_char_by_number(border_char)
            print(uc_char, end='')

            # print row
            for col_index, col in enumerate(row):
                # loop through all in game tetrominoes
                current_index = (row_index, col_index)
                current_char = 99 if self.is_any_tetrominoe_intersecting(
                    current_index) else ' '
                unicode = self.get_unicode_char_by_number(current_char)
                print(unicode, end='')

            # print right border for each row
            uc_char = self.get_unicode_char_by_number(border_char)
            print(uc_char, end='')
            print('')

        # print bottom row
        for c in self.grid_borders[2]:
            uc_char = self.get_unicode_char_by_number(c)
            print(uc_char, end='')
        print('')

    def generate_tetrominoe(self,position):
        index = random.choice(range(1, 5))
        match index:
            case 1:
                return VL(position)
            case 2:
                return HL(position)
            case 3:
                return L(position)
            case 4:
                return T(position)
            case _:
                return VL(position)

    def get_unicode_char_by_number(self, number):
        match number:
            case 1:
                return "\u2501"
            case 2:
                return "\u2503"
            case 3:
                return "\u250F"
            case 4:
                return "\u2513"
            case 5:
                return "\u2517"
            case 6:
                return "\u251B"
            case 99:
                return "\u2591"
            case _:
                return number


    # TODO: randoml generate orientation for the piece
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


class Tetrominoe(ABC):
    @abstractmethod
    def representation(self) -> List[tuple[int, int]]:
        pass

    @abstractmethod
    def height(self) -> int:
        pass

    @abstractmethod
    def width() -> int:
        pass

    def move_down(self, in_game_pieces):
        self.position = (self.position[0] + 1, self.position[1])
        current = set(self.representation())
        if any((set(piece.representation()) & current) for piece in in_game_pieces):
            self.position = (self.position[0] - 1, self.position[1])
            return False
        return True 

    # FIXME: verify bounds, currently it can move out of the map
    def move_left(self):
        self.position = (self.position[0], self.position[1] - 1)

    # FIXME: verify bounds, currently it can move out of the map
    def move_right(self):
        self.position = (self.position[0], self.position[1] + 1)

    def intersects(self, coords):
        # FIXME: somehow verify if the position of the current tetrominoe intersect the coordinates passed
        # if any((c[0] == coords[0] and c[1] == coords[1]) for c in vertical_line(self.position)):
        #     print(vertical_line(self.position))
        return any((c[0] == coords[0] and c[1] == coords[1]) for c in self.representation())


class VL(Tetrominoe):
    def __init__(self, starting_position):
        self.position = starting_position
    
    def representation(self) -> List[tuple[int, int]]:
        row = self.position[0]
        col = self.position[1]
        return [
            (row,     col),
            (row + 1, col),
            (row + 2, col)
        ]
    
    def height(self) -> int:
        return 3

    def width(self) -> int:
        return 1


class HL(Tetrominoe):
    def __init__(self, starting_position):
        self.position = starting_position
    
    def representation(self) -> List[tuple[int, int]]:
        row = self.position[0]
        col = self.position[1]
        return [
            (row, col),
            (row, col + 1),
            (row, col + 2)
        ]

    def height(self) -> int:
        return 1

    def width(self) -> int:
        return 3


class L(Tetrominoe):
    def __init__(self, starting_position):
        self.position = starting_position
    
    def representation(self) -> List[tuple[int, int]]:
        row = self.position[0]
        col = self.position[1]
        return [
            (row, col),
            (row + 1, col),
            (row + 2, col),
            (row + 2, col + 1),
            (row + 2, col + 2)
        ]

    def height(self) -> int:
        return 3

    def width(self) -> int:
        return 2


class T(Tetrominoe):
    def __init__(self, starting_position):
        self.position = starting_position
    
    def representation(self) -> List[tuple[int, int]]:
        row = self.position[0]
        col = self.position[1]
        return [
            (row, col),
            (row, col + 1),
            (row, col + 2),
            (row + 1, col + 1),
            (row + 2, col + 1)
        ]

    def height(self) -> int:
        return 3

    def width(self) -> int:
        return 3

asyncio.run(main())
