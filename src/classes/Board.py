class Board:
    def __init__(self, boardConfig):
        self.size = boardConfig["size"]
        self.num_green_apples = boardConfig["num_green_apples"]
        self.num_red_apples = boardConfig["num_red_apples"]
