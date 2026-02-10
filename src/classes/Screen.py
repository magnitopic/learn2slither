import pygame
from .Board import Board

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Screen:
    def __init__(self, screenConfig):
        pygame.init()
        pygame.font.init()

        self.size = screenConfig["size_px"]

        self.screen = pygame.display.set_mode((self.size, self.size))
        pygame.display.set_caption("Learn2Slither")

    def print_board(self, board: Board):
        self.screen.fill(BLACK)
        pygame.display.flip()
