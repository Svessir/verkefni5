import sys
from minesweeper.board import Board
import socket
import threading

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
        :raises Exception: if connection or state retrieval fails.
        """
        try:
            super(ObserverBoard, self).__init__()
            self.player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.player_socket.connect((player_ip, player_port))
            self._receive_new_state()
            self.thread = threading.Thread(target=self.client_loop)
            self.thread.daemon = True
            self.thread.start()
        except:
            print("Exception occurred please handle it.")

    def client_loop(self):
        """
        Starts the client loop.
        The loop will wait for activity from the player board
        and notify the observers.
        If the connection is lost to the player board the connection
        loss will be handled.

        :return: None
        """
        while True:
            self._receive_new_state()
            self._notify_observers()
        sys.exit(0)

    def _receive_new_state(self):
        """
        waits for new state update from player
        and processes the reponse.
        :return: None
        """
        self._state = self.player_socket.recv(1024).decode("utf-8")