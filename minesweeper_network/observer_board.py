import sys
from minesweeper.board import Board, BoardError
import socket
import threading
import re


class ObserverBoard(Board):
    """
    The observer board does not implement the
    gameplay logic. It is networked and connects
    to a networked player server. All board
    updates will be notified from the player to
    the observer board.
    """

    def __init__(self, player_ip, player_port):
        """
        Constructs the observer board.
        Attempts to connect to the networked player
        and receive its state. On successful connection
        the Board will start a thread that listens to
        the player activity.

        :param player_ip: The ip address of the player.
        :param player_port: The port number of the player.
        :raises BoardError: if connection or state retrieval fails.
        """
        try:
            super(ObserverBoard, self).__init__()
            self.player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.player_socket.connect((player_ip, player_port))
            self._receive_new_state(5)
            if not self._state:
                raise BoardError("Board did not receive a legal state string from server.")
            self.thread = threading.Thread(target=self.client_loop)
            self.thread.daemon = True
            self.is_client_on = False
            self.thread.start()
        except Exception as error:
            raise BoardError("Constructing board failed:{0}".format(str(error)), error)

    def client_loop(self):
        """
        Starts the client loop.
        The loop will wait for activity from the player board
        and notify the observers.
        If the connection is lost to the player board the connection
        loss will be handled by turning off the client.

        :return: None
        """
        self.is_client_on = True
        while self.is_client_on:
            self._receive_new_state()
            self._notify_observers()
        sys.exit(0)

    def _receive_new_state(self, timeout=None):
        """
        waits for new state update from player
        and processes the response.
        :return: None
        """
        try:
            self.player_socket.settimeout(timeout)
            state = self.player_socket.recv(1024).decode("utf-8")

            if not state:
                if self._state:
                    state_end = self._state.split(",", 1)[1]
                    self._state = "connection_loss,{0}".format(state_end)
                    self._notify_observers()
                self.shutdown_client()
                sys.exit(-1)

            state = re.sub("\r\n", "", state)
            if self.is_state_valid(state):
                self._state = state
        except ConnectionAbortedError as error:
            self.shutdown_client()
            sys.exit(0)

    def shutdown_client(self):
        """
        Shutdown the client loop.

        :return: None
        """
        self.is_client_on = False
        self.player_socket.close()

    def is_state_valid(self, state):
        """
        Checks if state string is valid.

        :return: True if valid else False
        """
        is_valid = True
        split = state.split(",")
        is_valid = is_valid and len(split) == 3
        is_valid = is_valid and bool(re.findall("continue|loss|win", split[0]))
        is_valid = is_valid and bool(re.match("[0-9 ]+", split[1]))
        is_valid = is_valid and bool(re.match("^[0-8HMBX/ ]+$", split[2]))
        return is_valid
