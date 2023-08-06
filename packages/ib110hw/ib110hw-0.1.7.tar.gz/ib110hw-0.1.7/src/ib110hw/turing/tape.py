from enum import Enum
from typing import List

START_SYMBOL = ">"
EMPTY_SYMBOL = ""


class Direction(Enum):
    LEFT = -1
    STAY = 0
    RIGHT = 1

    # shorthand aliases
    L = -1
    S = 0
    R = 1

    def __repr__(self):
        return self.name


class Cell:
    """Represents one cell of a Turing machine memory tape."""

    def __init__(
        self, value: str = EMPTY_SYMBOL, right: "Cell" = None, left: "Cell" = None
    ) -> None:
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return self.value or " "


class Tape:
    """Represents Turing machine memory tape as a linked list."""

    def __init__(self, start: Cell = None) -> None:
        self.start = start or Cell()
        self.current = self.start

    def __repr__(self) -> str:
        curr_cell: Cell = self.start

        # find the leftmost cell
        while curr_cell.left:
            curr_cell = curr_cell.left

        cells: List[Cell] = []

        while curr_cell:
            cells.append(curr_cell)
            curr_cell = curr_cell.right

        # ['a', 'b'] -> | a | b |
        str_cells = f"| {' | '.join([repr(c) for c in cells])} |\n"

        # adds spaces to put the cursor '^' below the current cell
        str_cursor = f"{' ' * (2 + cells.index(self.current) * 4)}^\n"

        return str_cells + str_cursor

    def move(self, direction: Direction) -> None:
        """Moves the tape cursor based on the provided direction.

        Args:
            direction (Direction): Specifies the move direction.
        """
        if direction == Direction.LEFT:
            self.move_left()
        elif direction == Direction.RIGHT:
            self.move_right()

    def move_left(self):
        """Moves the tape cursor to the left. (current will be current.left)"""
        if not self.current.left:
            self.current.left = Cell(right=self.current)

        self.current = self.current.left

    def move_right(self):
        """Moves the tape cursor to the right. (current will be current.right)"""
        if not self.current.right:
            self.current.right = Cell(left=self.current)

        self.current = self.current.right

    def write(self, text: str) -> None:
        """Writes the provided text on the tape.

        Args:
            text (str): Text to be written on the tape.
        """
        for symbol in text:
            self.current.value = symbol
            self.move_right()

        self.current = self.start

    def write_symbol(self, symbol: str) -> None:
        """Overwrites the current cell with the provided symbol.

        Args:
            symbol (str): Symbol to be written on the current cell.
        """
        cell = self.current

        if cell.value == START_SYMBOL:
            return

        self.current.value = symbol

    def clear(self) -> None:
        """Clears the tape contents and places the cursor on the start."""
        self.start = Cell()
        self.current = self.start

    def read(self) -> str:
        """
        Retrieves the content written on the tape.

        Returns:
            str: Content written on the tape.
        """
        current = self.start
        result = ""

        while current.right:
            result += current.value
            current = current.right

        return result


if __name__ == "__main__":
    pass
