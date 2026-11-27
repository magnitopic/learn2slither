from core.Snake import Snake
from core.Checker import Checker
from aux.enums import CellType, GameMode, Move

import numpy as np
import random as rnd


class Board:
    def __init__(self, config):
        self.boardConfig = config["game"]["board"]
        self.snakeConfig = config["game"]["snake"]
        self.argsConfig = config["args"]

        # reward values
        self.green_apple_reward = config["ai"]["rewards"]["green_apple"]
        self.red_apple_reward = config["ai"]["rewards"]["red_apple"]
        self.death_reward = config["ai"]["rewards"]["death"]
        self.stop_reward = config["ai"]["rewards"]["stop"]

        self.size = self.boardConfig["size"]
        self.snake_initial_len = self.snakeConfig.get("initial_length", 3)
        self.num_green_apples = self.boardConfig["num_green_apples"]
        self.num_red_apples = self.boardConfig["num_red_apples"]
        self.value = np.full(
            (self.size + 2, self.size + 2), CellType.EMPTY.value)
        self.show_lobby = self.argsConfig["showlobby"]
        self.step_by_step = self.boardConfig['step_by_step'] | False

        # Game mode determines whether the player is human or AI.
        # And if AI, if we are training or testing (see GameMode).
        # With the lobby it stays None until a button is pressed,
        # without it, it is decided by the arguments.
        self.game_mode = None
        if not self.show_lobby:
            self.set_game_mode(GameMode.AI_TEST if self.argsConfig["dontlearn"]
                               else GameMode.AI_TRAIN)

        # Place walls around the edges
        self.value[0, :] = CellType.WALL.value
        self.value[-1, :] = CellType.WALL.value
        self.value[:, 0] = CellType.WALL.value
        self.value[:, -1] = CellType.WALL.value

        self.snake = Snake(self.snakeConfig)
        self.checker = Checker()

        self.place_snake()
        self.place_initial_apples()

    def set_game_mode(self, game_mode: GameMode):
        self.game_mode = game_mode
        self.show_lobby = False

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
            if d == 1:
                return self.snake.length, self.size - margin
            if d == -1:
                return 1 + margin, self.size - self.snake.length + 1
            return 1, self.size

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
        reward = 0
        new_head_pos = None
        eating_red_apple = False
        eating_green_apple = False
        game_over = False

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
            reward = self.red_apple_reward
        elif self.value[new_head_pos] == CellType.GREEN_APPLE.value:
            eating_green_apple = True
            reward = self.green_apple_reward
        elif self.value[new_head_pos] == CellType.WALL.value:
            print("Snake hit the wall.")
            game_over = True
            reward = self.death_reward
        elif self.value[new_head_pos] == CellType.SNAKE_BODY.value:
            print("Snake hit itself.")
            game_over = True
            reward = self.death_reward

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
            print("Snake has died.")
            game_over = True
            reward = self.death_reward

        return reward, game_over

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

        return 42, 42  # todo -> change to a more robust system

    def handleTurn(self, move: Move):
        if move is None:
            move = self.snake.current_direction

        game_over, reward = self.moveSnake(move)

        self.updateBoardValue()

        return game_over, reward

    def reset(self):
        self.value = np.full(
            (self.size + 2, self.size + 2), CellType.EMPTY.value)

        # Place walls around the edges
        self.value[0, :] = CellType.WALL.value
        self.value[-1, :] = CellType.WALL.value
        self.value[:, 0] = CellType.WALL.value
        self.value[:, -1] = CellType.WALL.value

        self.snake.length = self.snake_initial_len
        self.snake.body = []

        self.place_snake()
        self.place_initial_apples()

    def get_snake_vision(self):
        pass

    def get_state(self) -> np.ndarray:
        '''
        Returns the current state of the board to be the value vector for the
        neural network.
        '''
        state = np.zeros(16, dtype=np.float32)

        vision = self.get_snake_vision()

        # get relative directions for current position
        rel_dirs = self.snake.get_relative_directions()

        # state[1:3] -> immediate danger
        state[0] = self.checker.danger_immediate(vision, rel_dirs['front'])
        state[1] = self.checker.danger_immediate(vision, rel_dirs['left'])
        state[2] = self.checker.danger_immediate(vision, rel_dirs['right'])

        # state [4:6] -> green apple visible
        state[3] = self.checker.green_apple_visible(vision, rel_dirs['front'])
        state[4] = self.checker.green_apple_visible(vision, rel_dirs['left'])
        state[5] = self.checker.green_apple_visible(vision, rel_dirs['right'])

        # state [7:9] -> red apple immediate
        state[6] = self.checker.red_apple_immediate(vision, rel_dirs['front'])
        state[7] = self.checker.red_apple_immediate(vision, rel_dirs['left'])
        state[8] = self.checker.red_apple_immediate(vision, rel_dirs['right'])

        # state [10:11] -> current direction
        if self.snake.current_direction in [Move.UP, Move.DOWN]:
            state[9] = 0
            state[10] = 0 if self.snake.current_direction == Move.UP else 1
        else:
            state[9] = 1
            state[10] = 0 if self.snake.current_direction == Move.LEFT else 1

        # state [12:13] -> absolute position
        head_y, head_x = self.snake.head_pos
        state[11] = (head_y - 1) / self.size
        state[12] = (head_x - 1) / self.size

        # state [14:16] -> distance to nearest object
        state[13] = self.checker.dist_to_nearest_obj(vision, rel_dirs['front'])
        state[14] = self.checker.dist_to_nearest_obj(vision, rel_dirs['left'])
        state[15] = self.checker.dist_to_nearest_obj(vision, rel_dirs['right'])

        return state

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
