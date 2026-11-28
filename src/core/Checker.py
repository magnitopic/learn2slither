
from aux.enums import CellType


class Checker:
    def danger_immediate(self, vision, direction):
        if len(vision[direction]) > 0:
            first_cell = vision[direction][0]
            if first_cell in [CellType.WALL.value, CellType.SNAKE_BODY.value,]:
                return 1.0
        return 0.0

    def green_apple_visible(self, vision, direction):
        for cell in vision[direction]:
            if cell == CellType.GREEN_APPLE.value:
                return 1.0
            if cell not in [CellType.EMPTY.value, CellType.GREEN_APPLE.value]:
                break
        return 0.0

    def red_apple_immediate(self, vision, direction):
        if len(vision[direction]) > 0:
            first_cell = vision[direction][0]
            if first_cell == CellType.RED_APPLE.value:
                return 1.0
        return 0.0

    def dist_nearest_body(self, vision, direction):
        for i, cell in enumerate(vision[direction]):
            if cell == CellType.SNAKE_BODY.value:
                # 1/distance: 1.0 when adjacent, smaller the farther away.
                # Independent of the board size.
                return 1.0 / (i + 1)
        return 0.0  # no body in sight
