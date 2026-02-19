from classes.Snake import Snake
from enums import CellType, Move
import numpy as np


class Board:
    def __init__(self, boardConfig, snakeConfig):
        self.size = boardConfig["size"]
        self.num_green_apples = boardConfig["num_green_apples"]
        self.num_red_apples = boardConfig["num_red_apples"]
        self.value = np.full(
            (self.size + 2, self.size + 2), CellType.EMPTY.value)

        # Place walls around the edges
        self.value[0, :] = CellType.WALL.value
        self.value[-1, :] = CellType.WALL.value
        self.value[:, 0] = CellType.WALL.value
        self.value[:, -1] = CellType.WALL.value

        self.snake = Snake(snakeConfig)

        self.place_snake()
        self.place_initial_apples()

    def place_snake(self):
        # Place snake in the middle of the board, facing right
        y = self.size // 2
        x = self.size // 2

        snake_body = []

        # Check if there's enough space for the snake body
        if x < self.snake.length:
            raise ValueError(
                "Board size is too small for the snake's initial length.")

        # Place head at the middle
        self.value[y, x] = CellType.SNAKE_HEAD.value
        snake_body.append((y, x))
        self.snake.head_pos = (y, x)

        # Body extends to the left (snake facing right)
        for i in range(self.snake.length - 1):
            self.value[y, x - (i + 1)] = CellType.SNAKE_BODY.value
            snake_body.append((y, x - (i + 1)))

        self.snake.body = snake_body
        self.snake.current_direction = Move.RIGHT

    def place_apple(self, type):
        empty_cells = np.argwhere(self.value == CellType.EMPTY.value)
        if len(empty_cells) == 0:
            return
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

        if self.value[new_head_pos] == CellType.RED_APPLE.value:
            eating_red_apple = True
        elif self.value[new_head_pos] == CellType.GREEN_APPLE.value:
            eating_green_apple = True
        elif self.value[new_head_pos] == CellType.WALL.value:
            raise ValueError("Snake hit the wall.")
        elif self.value[new_head_pos] == CellType.SNAKE_BODY.value:
            raise ValueError("Snake hit itself.")

        self.snake.body.insert(0, new_head_pos)
        self.snake.head_pos = new_head_pos
        if eating_red_apple:
            self.snake.body.pop()
            self.snake.body.pop()
            self.place_apple(CellType.RED_APPLE)
        elif not eating_green_apple:
            self.snake.body.pop()
        else:
            self.place_apple(CellType.GREEN_APPLE)

        self.snake.length = len(self.snake.body)
        self.snake.current_direction = move

        if self.snake.length == 0:
            raise ValueError("Snake has died.")

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
