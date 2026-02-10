from classes.Snake import Snake
from enums import CellType
import numpy as np


class Board:
    def __init__(self, boardConfig, snakeConfig):
        self.size = boardConfig["size"]
        self.num_green_apples = boardConfig["num_green_apples"]
        self.num_red_apples = boardConfig["num_red_apples"]
        self.value = np.full((self.size, self.size), CellType.EMPTY.value)

        # Place walls around the edges
        self.value[0, :] = CellType.WALL.value
        self.value[-1, :] = CellType.WALL.value
        self.value[:, 0] = CellType.WALL.value
        self.value[:, -1] = CellType.WALL.value

        self.snake = Snake(snakeConfig)

        self.place_snake()
        self.place_initial_apples()

    def place_snake(self):
        min_space = self.snake.length + 1

        if self.size < min_space:
            raise ValueError(
                "Board size is too small for the snake's initial length.")

        direction = np.random.choice(["up", "down", "left", "right"])
        if direction in ["up", "down"]:
            x = np.random.randint(1, self.size - 1)
            y = np.random.randint(1, self.size - min_space)
            for i in range(self.snake.length):
                self.value[y + i, x] = CellType.SNAKE_BODY.value
        else:
            x = np.random.randint(1, self.size - min_space)
            y = np.random.randint(1, self.size - 1)
            for i in range(self.snake.length):
                self.value[y, x + i] = CellType.SNAKE_BODY.value

    def place_apple(self, type):
        empty_cells = np.argwhere(self.value == CellType.EMPTY.value)
        if len(empty_cells) == 0:
            raise ValueError("No empty cells available to place an apple.")
        y, x = empty_cells[np.random.choice(len(empty_cells))]
        self.value[y, x] = type.value

    def place_initial_apples(self):
        for _ in range(self.num_green_apples):
            self.place_apple(CellType.GREEN_APPLE)
        for _ in range(self.num_red_apples):
            self.place_apple(CellType.RED_APPLE)
