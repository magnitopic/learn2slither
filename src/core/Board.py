from core.Snake import Snake
from aux.enums import CellType, Move
import numpy as np
import random as rnd


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
        margin = 1

        # Check that board if big enough for snake len
        if self.size < self.snake.length + margin:
            raise ValueError(
                "Board size is too small for the snake's initial length.")

        self.snake.current_direction = rnd.choice(
            [Move.LEFT, Move.RIGHT, Move.UP, Move.DOWN])

        # How far one step moves in this direction, as (dy, dx)
        deltas = {
            Move.UP:    (-1, 0),
            Move.DOWN:  (1, 0),
            Move.LEFT:  (0, -1),
            Move.RIGHT: (0, 1),
        }
        dy, dx = deltas[self.snake.current_direction]

        def axis_range(d):
            if d == 1:    # moving toward higher indices: body trails toward lower ones
                return self.snake.length, self.size - margin
            if d == -1:   # moving toward lower indices: body trails toward higher ones
                return 1 + margin, self.size - self.snake.length + 1
            return 1, self.size  # this axis is not affected

        min_x, max_x = axis_range(dx)
        min_y, max_y = axis_range(dy)

        x = rnd.randint(min_x, max_x)
        y = rnd.randint(min_y, max_y)

        # Place head
        self.value[y, x] = CellType.SNAKE_HEAD.value
        self.snake.head_pos = (y, x)
        snake_body = [(y, x)]

        # Place body, opposite to the movement direction
        for i in range(1, self.snake.length):
            pos = (y - dy * i, x - dx * i)
            self.value[pos] = CellType.SNAKE_BODY.value
            snake_body.append(pos)

        self.snake.body = snake_body

    def place_apple(self, type):
        empty_cells = np.argwhere(self.value == CellType.EMPTY.value)
        """         print(empty_cells)
        print(len(empty_cells)) 
        """
        if len(empty_cells) == 0:
            return
        y, x = empty_cells[np.random.choice(len(empty_cells))]
        self.value[y, x] = type.value

    def place_initial_apples(self):
        empty_cells = np.argwhere(self.value == CellType.EMPTY.value)
        if len(empty_cells) < self.num_green_apples + self.num_red_apples:
            raise ValueError("Not enough space for apples")

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

    def snakeVision(self):
        snakeHeadPos: tuple = self.snake.head_pos
        vision = ""
        for i in range(self.size + 2):
            for j in range(self.size + 2):
                if i == snakeHeadPos[0] or j == snakeHeadPos[1]:
                    vision += self.value[i][j]
                else:
                    vision += " "
            vision += "\n"
        return vision
