from minesweeper.board import Board
from minesweeper.minesweeper_cell import MinesweeperCell
from random import randint
from itertools import chain

class MinesweeperBoard(Board):
    """
    Implements full logic of minesweeper
    """

    def __init__(self, rows, columns, bomb_ratio):
        """
        Constructs a minesweeper board with the following properties:

        :param rows: The number of rows on the board.
        :param columns: The number of columns in each row.
        :param bomb_ratio: The ratio of bombs of the total cells on the board
        """
        super(MinesweeperBoard, self).__init__()
        self._rows = rows
        self._columns = columns
        self._number_of_bombs = int(rows * columns * bomb_ratio)
        self._bombs = []
        self._cells = [[MinesweeperCell(self) for c in range(columns)] for r in range(rows)]
        self._is_game_over = False
        cells = list(chain(*self._cells))

        # Inserts bombs
        for i in range(self._number_of_bombs):
            index = randint(0, len(cells) - 1)
            cells[index].is_bomb = True
            cells.remove(cells[index])
        for r in range(rows):
            for c in range(columns):
                cell = self._cells[r][c]
                top = bool(r)
                bottom = not r == rows - 1
                left = bool(c)
                right = not c == columns - 1
                neighbours = []
                neighbours.append(self._cells[r - 1][c]) if top else None
                neighbours.append(self._cells[r - 1][c - 1]) if top and left else None
                neighbours.append(self._cells[r - 1][c + 1]) if top and right else None
                neighbours.append(self._cells[r][c - 1]) if left else None
                neighbours.append(self._cells[r][c + 1]) if right else None
                neighbours.append(self._cells[r + 1][c]) if bottom else None
                neighbours.append(self._cells[r + 1][c - 1]) if bottom and left else None
                neighbours.append(self._cells[r + 1][c + 1]) if bottom and right else None
                cell.set_neighbours(neighbours)
        self._update_state()



    def step_on_cell(self, position):
        """
        Steps on a cell with given position

        :param position: The position of the cell as a 2 dimensional tuple.
        :return: None
        """
        if not self._is_game_over:
            cell = self._cells[position[0]][position[1]]
            cell.step_on()
            self._update_state()

    def mark_cell_toggle(self, position):
        """
        Toggles the mark on a cell if the cell is markable

        :param position: The position of the cell.
        :return: None
        """
        if not self._is_game_over:
            cell = self._cells[position[0]][position[1]]
            cell.mark_toggle()
            if self._get_mark_count_left() < 0:
                # revert the mark if the flags were depleted.
                cell.mark_toggle()
            self._update_state()


    def _update_state(self):
        """
        Updates the state and notifies the observers
        if it has changed.

        :return: None
        """
        old_state = self._state
        self._state = "/".join(["".join([str(col) for col in row]) for row in self._cells])
        self._is_game_over = "X" in self._state
        if old_state != self._state:
            self._notify_observers()

    def explode(self):
        """
        Triggers explosion thus ends the game.

        :return:None
        """
        for bomb in self._bombs:
            bomb.is_hidden = False

    def _get_mark_count_left(self):
        """
        Gets the number of marking flags left at the player disposal.

        :return: The number of flags left.
        """
        return self._number_of_bombs - sum([sum([1 for c in row if c.is_marked]) for row in self._cells])

    def _is_win(self):
        """
        Checks if the player has won the game.

        :return: True if the game is won else False.
        """
        return sum([sum([1 for c in row if c.is_marked and c.is_bomb]) for row in self._cells]) == self._number_of_bombs

def observer_function(state):
    rows = state.split("/")
    for r in rows:
        print(r)
    print()

