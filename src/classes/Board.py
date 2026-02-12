from classes.Snake import Snake
from enums import CellType, Move
import numpy as np


class Board:
    def __init__(self, boardConfig, snakeConfig):
        self.size = boardConfig["size"]
        self.num_green_apples = boardConfig["num_green_apples"]
        self.num_red_apples = boardConfig["num_red_apples"]
        self.value = np.full(
            (self.size + 1, self.size + 1), CellType.EMPTY.value)

        # Place walls around the edges
        self.value[0, :] = CellType.WALL.value
        self.value[-1, :] = CellType.WALL.value
        self.value[:, 0] = CellType.WALL.value
        self.value[:, -1] = CellType.WALL.value

        self.snake = Snake(snakeConfig)

        self.place_snake()
        self.place_initial_apples()

    def place_snake(self):
        min_space = self.snake.length + 2
        snake_body = []

        if self.size < min_space:
            raise ValueError(
                "Board size is too small for the snake's initial length.")

        direction = np.random.choice(["up", "down", "left", "right"])
        x = np.random.randint(self.snake.length, self.size - self.snake.length)
        y = np.random.randint(self.snake.length, self.size - self.snake.length)
        self.value[y, x] = CellType.SNAKE_HEAD.value
        snake_body.append((y, x))
        self.snake.head_pos = (y, x)

        if direction in ["up", "down"]:
            for i in range(self.snake.length - 1):
                self.value[y + (i + 1), x] = CellType.SNAKE_BODY.value
                snake_body.append((y + (i + 1), x))
        else:
            for i in range(self.snake.length - 1):
                self.value[y, x + (i + 1)] = CellType.SNAKE_BODY.value
                snake_body.append((y, x + (i + 1)))

        self.snake.body = snake_body

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

    def moveSnake(self, move: Move):
        new_head_pos = None
        eating_red_apple = False
        eating_green_apple = False

        if move == Move.UP:
            new_head_pos = (self.snake.head_pos[0] - 1, self.snake.head_pos[1])
        elif move == Move.DOWN:
            new_head_pos = (self.snake.head_pos[0] + 1, self.snake.head_pos[1])
        elif move == Move.LEFT:
            new_head_pos = (self.snake.head_pos[0], self.snake.head_pos[1] - 1)
        elif move == Move.RIGHT:
            new_head_pos = (self.snake.head_pos[0], self.snake.head_pos[1] + 1)

        print(self.value[new_head_pos])

        self.snake.body.insert(0, new_head_pos)
        self.snake.head_pos = new_head_pos

        self.snake.body.pop()

    def updateBoardValue(self):
        # remove all snake body and head
        self.value[self.value ==
                   CellType.SNAKE_HEAD.value] = CellType.EMPTY.value
        self.value[self.value ==
                   CellType.SNAKE_BODY.value] = CellType.EMPTY.value

        for index, (y, x) in enumerate(self.snake.body):
            if index == 0:
                self.value[y, x] = CellType.SNAKE_HEAD.value
            else:
                self.value[y, x] = CellType.SNAKE_BODY.value

    def handleTurn(self, move: Move):
        if move is None:
            move = self.snake.current_direction

        self.moveSnake(move)

        self.updateBoardValue()

    """ Aux functions """

    def __str__(self):
        return "\n".join(" ".join(row) for row in self.value)
