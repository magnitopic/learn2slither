import pygame
from .Board import Board


class Screen:
    def __init__(self, screenConfig):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Learn2Slither")

        self.size = screenConfig["size_px"]
        self.screen = pygame.display.set_mode((self.size, self.size))
        self.show_grid = screenConfig["show_grid"]

        self.board_height = self.size * 0.7
        self.board_width = self.board_height
        self.offset_x = (self.size - self.board_width) // 2
        self.offset_y = self.size * .03

        # Colours
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.bg_colour = screenConfig["colour"]["bg"]
        self.snake_colour = screenConfig["colour"]["snake"]
        self.green_apple_colour = screenConfig["colour"]["apple_green"]
        self.red_apple_colour = screenConfig["colour"]["apple_red"]

    def draw_grid(self, board: Board):
        cell_size = self.board_width // board.size
        for x in range(board.size + 1):
            pygame.draw.line(self.screen, self.black, (self.offset_x + x * cell_size, self.offset_y),
                             (self.offset_x + x * cell_size, self.offset_y + self.board_height))
        for y in range(board.size + 1):
            pygame.draw.line(self.screen, self.black, (self.offset_x, self.offset_y + y * cell_size),
                             (self.offset_x + self.board_width, self.offset_y + y * cell_size))

    def draw_snake(self, board: Board):
        pass

    def draw_apples(self, board: Board):
        pass

    def print_board(self, board: Board):
        self.screen.fill(self.bg_colour)

        """ Game area """
        board_rect = pygame.Rect(self.offset_x, self.offset_y,
                                 self.board_width, self.board_height)
        pygame.draw.rect(self.screen, self.white, board_rect)
        # Draw border
        pygame.draw.rect(self.screen, self.black, board_rect, 3)

        if self.show_grid:
            self.draw_grid(board)

        self.draw_snake(board)
        self.draw_apples(board)

        pygame.display.flip()
