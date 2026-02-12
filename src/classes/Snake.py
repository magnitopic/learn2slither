from enums import Move


class Snake:
    def __init__(self, snakeConfig):
        self.length: int = snakeConfig.get("initial_length", 3)
        self.show_vision: bool = snakeConfig.get("show_vision", False)
        self.current_direction: Move = Move.RIGHT
        self.body = []

    def move(self):
        return None