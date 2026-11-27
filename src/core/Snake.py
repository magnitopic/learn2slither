from aux.enums import Move


class Snake:
    def __init__(self, snakeConfig):
        self.length: int = snakeConfig.get("initial_length", 3)
        self.show_vision: bool = snakeConfig.get("show_vision", False)
        self.current_direction: Move = Move.RIGHT
        self.body = []
        self.head_pos = None

    def get_relative_directions(self):
        """
        Returns the relative directions of the snake's current direction.
        The order is [front, left, right].
        """
        direction_map = {
            Move.UP: {
                'front': Move.UP,
                'left': Move.LEFT,
                'right': Move.RIGHT
            },
            Move.DOWN: {
                'front': Move.DOWN,
                'left': Move.RIGHT,
                'right': Move.LEFT
            },
            Move.LEFT: {
                'front': Move.LEFT,
                'left': Move.DOWN,
                'right': Move.UP
            },
            Move.RIGHT: {
                'front': Move.RIGHT,
                'left': Move.UP,
                'right': Move.DOWN
            }
        }
        return direction_map[self.current_direction]
