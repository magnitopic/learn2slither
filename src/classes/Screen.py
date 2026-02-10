from enums import CellType
from .Board import Board
import pygame
import numpy as np


class Screen:
    def __init__(self, screenConfig):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Learn2Slither")

        self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.font2 = pygame.font.SysFont('Arial', 20)

        self.size = screenConfig["size_px"]
        self.screen = pygame.display.set_mode((self.size, self.size))
        self.show_grid = screenConfig["show_grid"]
        self.show_stats = screenConfig["show_stats"]

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
        board_value = board.value
        coords = np.where(board_value == CellType.SNAKE_BODY.value)
        coordinates = list(zip(coords[0], coords[1]))
        cell_size = self.board_width // board.size
        padding = 1
        for y, x in coordinates:
            rect = pygame.Rect((self.offset_x + x * cell_size + padding + 1),
                               (self.offset_y + y * cell_size + padding + 1),
                               cell_size - 3 * padding, cell_size - 3 * padding)
            pygame.draw.rect(self.screen, self.snake_colour, rect)

    def draw_apples(self, board: Board):
        board_value = board.value
        coords_green = np.where(board_value == CellType.GREEN_APPLE.value)
        coords_red = np.where(board_value == CellType.RED_APPLE.value)
        coordinates_green = list(zip(coords_green[0], coords_green[1]))
        coordinates_red = list(zip(coords_red[0], coords_red[1]))

        cell_size = self.board_width // board.size
        for y, x in coordinates_green:
            rect = pygame.Rect((self.offset_x + x * cell_size + cell_size // 7),
                               (self.offset_y + y * cell_size + cell_size // 7),
                               cell_size // 1.3, cell_size // 1.3)
            pygame.draw.ellipse(self.screen, self.green_apple_colour, rect)
        for y, x in coordinates_red:
            rect = pygame.Rect((self.offset_x + x * cell_size + cell_size // 7),
                               (self.offset_y + y * cell_size + cell_size // 7),
                               cell_size // 1.3, cell_size // 1.3)
            pygame.draw.ellipse(self.screen, self.red_apple_colour, rect)

    def draw_stats(self):
        pass

    def draw_name(self):
        text1 = "learn2slither"
        text2 = "By alaparic"
        text1_surface = self.title_font.render(text1, True, self.black)
        text2_surface = self.font2.render(text2, True, self.black)
        self.draw_text(text1, self.size // 2 - text1_surface.get_width() //
                       2, self.size * 0.8, self.title_font, self.black)
        self.draw_text(text2, self.size // 2 - text2_surface.get_width() //
                       2, self.size * 0.8 + 50, self.font2, self.black)

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

        """ Stats area """
        if self.show_stats:
            self.draw_stats()
        else:
            self.draw_name()

        pygame.display.flip()

    """ Aux functions """

    def draw_text(self, text, x, y, font, color):
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
