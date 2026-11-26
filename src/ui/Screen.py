from aux.enums import CellType, GameMode, Move
from aux.colours import GREEN, YELLOW, RESET
from core.Board import Board
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
        self.button_colour = screenConfig["colour"]["button"]

        # Clickable areas of the lobby, filled when drawing it
        self.lobby_buttons = {}

        # Run control, used by the Trainer through the methods below
        self.clock = pygame.time.Clock()
        self.game_speed = 1  # Speed from 1-5
        self.paused = False
        self.step_requested = False  # 'd' key while paused: one turn
        self.move = None  # Last direction asked with the arrows (human)

        # Values shown in the stats panel
        self.stats = {}
        self.previous_episode_length = 0
        self.session_max_length = 0

    """ Run control, called from the Trainer in every turn """

    def update_previous_episode_length(self, length: int):
        self.previous_episode_length = length

    def update_session_max_length(self, length: int):
        self.session_max_length = length

    def render(self, board: Board, stats: dict):
        self.stats = stats
        self.draw_board(board)

    def handle_events(self, board: Board = None) -> bool:
        """ Returns False if the user wants to quit """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.paused:
                        print(f"{YELLOW}⏸️ Game paused{RESET}")
                    else:
                        print(f"{GREEN}▶️ Game resumed{RESET}")
                elif event.key == pygame.K_d and self.paused:
                    self.step_requested = True
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    self.game_speed = event.key - pygame.K_0
                    print(f"{YELLOW}⚡ Game speed set to "
                          f"{self.game_speed}{RESET}")
                else:
                    self.read_move_key(event.key, board)
        return True

    def wait_for_key_step_by_step(self, board: Board = None):
        """ Waits for SPACE to advance one turn. Returns 'quit' or 'space'.
        The arrows still steer the snake while waiting (human player) """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'quit'
                    elif event.key == pygame.K_SPACE:
                        return 'space'
                    self.read_move_key(event.key, board)
            pygame.time.wait(50)

    def clock_tick(self):
        if not self.paused:
            self.clock.tick(self.game_speed * 2)

    def read_move_key(self, key, board: Board = None):
        keys = {
            pygame.K_UP: Move.UP,
            pygame.K_DOWN: Move.DOWN,
            pygame.K_LEFT: Move.LEFT,
            pygame.K_RIGHT: Move.RIGHT
        }
        opposite = {Move.UP: Move.DOWN, Move.DOWN: Move.UP,
                    Move.LEFT: Move.RIGHT, Move.RIGHT: Move.LEFT}
        if key not in keys:
            return
        if board is None or opposite[keys[key]] != \
                board.snake.current_direction:
            self.move = keys[key]

    def draw_grid(self, board: Board):
        cell_size = self.board_width // board.size
        for x in range(board.size + 1):
            pygame.draw.line(self.screen, self.black,
                             (self.offset_x + x * cell_size, self.offset_y),
                             (self.offset_x + x * cell_size,
                              self.offset_y + self.board_height))
        for y in range(board.size + 1):
            pygame.draw.line(self.screen, self.black,
                             (self.offset_x, self.offset_y + y * cell_size),
                             (self.offset_x + self.board_width,
                              self.offset_y + y * cell_size))

    def draw_snake(self, board: Board):
        board_value = board.value
        coords = np.where(board_value == CellType.SNAKE_BODY.value)
        coords = np.concatenate(
            (coords,
             np.where(board_value == CellType.SNAKE_HEAD.value)),
            axis=1)
        coordinates = list(zip(coords[0] - 1, coords[1] - 1))
        cell_size = self.board_width // board.size
        padding = 1
        for y, x in coordinates:
            rect = pygame.Rect((self.offset_x + x * cell_size + padding + 1),
                               (self.offset_y + y * cell_size + padding + 1),
                               cell_size - 3 * padding,
                               cell_size - 3 * padding)
            pygame.draw.rect(self.screen, self.snake_colour, rect)

    def draw_apples(self, board: Board):
        board_value = board.value
        coords_green = np.where(board_value == CellType.GREEN_APPLE.value)
        coords_red = np.where(board_value == CellType.RED_APPLE.value)
        coordinates_green = list(zip(coords_green[0] - 1, coords_green[1] - 1))
        coordinates_red = list(zip(coords_red[0] - 1, coords_red[1] - 1))

        cell_size = self.board_width // board.size
        for y, x in coordinates_green:
            rect = pygame.Rect(
                (self.offset_x + x * cell_size + cell_size // 7),
                (self.offset_y + y * cell_size + cell_size // 7),
                cell_size // 1.3, cell_size // 1.3)
            pygame.draw.ellipse(self.screen, self.green_apple_colour, rect)
        for y, x in coordinates_red:
            rect = pygame.Rect(
                (self.offset_x + x * cell_size + cell_size // 7),
                (self.offset_y + y * cell_size + cell_size // 7),
                cell_size // 1.3, cell_size // 1.3)
            pygame.draw.ellipse(self.screen, self.red_apple_colour, rect)

    def draw_stats(self):
        stats = self.stats
        lines = [
            f"Session: {stats.get('episode', 0)}",
            f"Length: {stats.get('length', 0)}",
            f"Steps: {stats.get('steps', 0)}",
            f"Previous length: {self.previous_episode_length}",
            f"Max length: {self.session_max_length}",
            f"Epsilon: {stats.get('epsilon', 0):.3f}",
        ]
        for i, line in enumerate(lines):
            self.draw_text(line, self.offset_x, self.size * 0.8 + i * 24,
                           self.font2, self.black)

    def draw_name(self, is_lobby=False):
        text1 = "learn2slither"
        text2 = "By alaparic"
        text1_surface = self.title_font.render(text1, True, self.black)
        text2_surface = self.font2.render(text2, True, self.black)
        if is_lobby:
            self.draw_text(text1, self.size // 2 - text1_surface.get_width() //
                           2, self.size * 0.2, self.title_font, self.black)
            self.draw_text(text2, self.size // 2 - text2_surface.get_width() //
                           2, self.size * 0.2 + 50, self.font2, self.black)
        else:
            self.draw_text(text1, self.size // 2 - text1_surface.get_width() //
                           2, self.size * 0.8, self.title_font, self.black)
            self.draw_text(text2, self.size // 2 - text2_surface.get_width() //
                           2, self.size * 0.8 + 50, self.font2, self.black)

    def draw_board(self, board: Board):
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

    def draw_button(self, text, x, y, width, height, font, color):
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, button_rect)
        text_surface = font.render(text, True, self.black)
        text_x = x + (width - text_surface.get_width()) // 2
        text_y = y + (height - text_surface.get_height()) // 2

        self.screen.blit(text_surface, (text_x, text_y))

        return button_rect

    def run_lobby(self, board: Board) -> bool:
        """ Shows the lobby until a button is pressed. The game mode is set
        in the board. Returns False if the user wants to quit """
        while board.show_lobby:
            self.draw_lobby()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    return False
                elif (event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1):
                    choice = self.get_lobby_choice(event.pos)
                    if choice == "human":
                        board.set_game_mode(GameMode.HUMAN)
                    elif choice == "ai":
                        # The lobby is only shown when not training
                        board.set_game_mode(GameMode.AI_TEST)
                    elif choice == "exit":
                        return False
            self.clock.tick(30)
        return True

    def draw_lobby(self):
        self.screen.fill(self.bg_colour)
        self.draw_name(True)
        self.lobby_buttons = {
            "ai": self.draw_button(
                "AI Player", self.size // 2 - 100, self.size * 0.5,
                200, 50, self.font2, self.button_colour),
            "human": self.draw_button(
                "Human Player", self.size // 2 - 100, self.size * 0.6,
                200, 50, self.font2, self.button_colour),
            "exit": self.draw_button(
                "Exit", self.size // 2 - 100, self.size * 0.7,
                200, 50, self.font2, self.button_colour),
        }
        pygame.display.flip()

    def get_lobby_choice(self, pos):
        """ Name of the lobby button at pos ("ai", "human", "exit") """
        for name, rect in self.lobby_buttons.items():
            if rect.collidepoint(pos):
                return name
        return None

    """ Aux functions """

    def draw_text(self, text, x, y, font, color):
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def close(self):
        pygame.quit()
