class Snake:
    def __init__(self, snakeConfig):
        self.length: int = snakeConfig["length"] | 3
        self.show_vision: bool = snakeConfig["show_vision"]
