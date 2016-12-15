class MinesweeperCell:
    """
    Implements the logic for a minesweeper cell
    """

    def __init__(self, board):
        """
        Constructs a single cell on the board.

        :param board: The board the cell belongs too.
        """
        self.board = board
        self.is_hidden = True
        self.is_bomb = False
        self.is_exploded = False
        self.is_marked = False
        self._number_of_bomb_neighbours = 0
        self._neighbours = []

    def set_neighbours(self, neighbours):
        """
        Sets the neigbouring cell of this cell

        :param neighbours: A list of Minesweeper cells.
        :return: None
        """
        self._neighbours = neighbours
        self._number_of_bomb_neighbours = sum([1 for neighbour in self._neighbours if neighbour.is_bomb])

    def mark_toggle(self):
        """
        Toggles the mark of the cell if the cell is markable.

        :return: None
        """
        if self.is_hidden:
            self.is_marked = not self.is_marked

    def step_on(self):
        """
        Steps on cell:
        * If cell is a bomb then the cell will explode the board
        * Else the cell will be revealed. If the cell contains no neighbouring bombs
          then the neighbouring cells will also be stepped on.
        :return:
        """
        if not self.is_marked and self.is_hidden:
            self.is_hidden = False
            if self.is_bomb:
                self.board.explode()
                self.is_exploded = True
            else:
                self.is_marked = False
                if self._number_of_bomb_neighbours == 0:
                    for neighbour in self._neighbours:
                        neighbour.is_marked = False
                        neighbour.step_on()

    def __str__(self):
        """
        returns the str representation of the cell
        according to the state of the cell
        :return: string representation of cell.
        """
        if self.is_marked:
            return "M"
        elif self.is_hidden:
            return "H"
        elif self.is_bomb and self.is_exploded:
            return "X"
        elif self.is_bomb:
            return "B"
        return str(self._number_of_bomb_neighbours)