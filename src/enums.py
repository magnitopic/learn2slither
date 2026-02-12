from enum import Enum


class CellType(Enum):
    EMPTY = '0'         # Empty cell
    WALL = 'W'          # Wall
    SNAKE_HEAD = 'H'    # Snake head
    SNAKE_BODY = 'S'    # Snake body
    GREEN_APPLE = 'G'   # Green apple (+1 length)
    RED_APPLE = 'R'     # Red apple (-1 length)


class Move(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
