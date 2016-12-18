class BoardError(Exception):
    """
    Error class dedicated to Board errors
    """
    def __init__(self, msg, cause=None):
        super(BoardError, self).__init__(msg)
        self.cause = cause

    def __str__(self):
        return str(self.cause) if self.cause else super().__str__()

class Board:
    """
    Layered supertype for a minesweeper board.
    """

    def __init__(self):
        self._observers = set()
        self._state = None

    def _notify_observers(self):
        """
        Notifies observers with the current state of the board.

        :return:None
        """
        for observer in self._observers:
            observer(self._state)

    def add_observer(self, observer):
        """
        Adds an observer to the list of observers of the board.

        :param observer: Function that takes the state as a parameter
        :return: None
        """
        self._observers.add(observer)
        observer(self._state)

    def step_on_cell(self, position):
        """
        Abstract method for stepping on cell on the
        minesweeper board.

        :param position: The position of the cell.
        :return: None
        """
        pass

    def mark_cell_toggle(self, position):
        """
        Abstract method for marking a cell on the
        minesweeper board.

        :param position: The position of the cell.
        :return: None
        """
        pass

    def reset(self):
        """
        Abstract method for resetting the board.

        :return: None
        """
        pass
