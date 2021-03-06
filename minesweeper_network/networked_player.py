import sys
import socket
import select
import threading


class NetworkedPlayerError(Exception):
    """
    Error class dedicated to Networked Player errors
    """

    def __init__(self, msg):
        """
        Constructs an error with error message
        :param msg: The message of this error.
        """
        super(NetworkedPlayerError, self).__init__(msg)


class NetworkedPlayer:
    """
    The networked player class starts a thread
    that accepts observing players and notifies
    them with the state on a state change.
    """

    def __init__(self, host, port):
        """
        Constructs a new networked player and starts the
        the server loop on a new thread.

        :param host: The ip address of the host
        :param port: The port number
        """
        try:
            self.state = ""
            self.sockets = []
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(10)
            self.sockets.append(self.server_socket)
            self.thread = threading.Thread(target=self.server_loop)
            self.thread.daemon = True
            self.is_server_on = False
            self.thread.start()
        except Exception as error:
            raise NetworkedPlayerError("Could not start player server:{0}".format(str(error)))

    def server_loop(self):
        """
        Accepts new observers and notifies them with the current state.
        If an observer leaves this method will also remove the observer
        from the list of observers.

        :return: None
        """
        self.is_server_on = True
        while self.is_server_on:
            ready_to_read, ready_to_write, in_error = select.select(self.sockets, [], [], 1)
            if not self.is_server_on:
                break
            for sock in ready_to_read:
                if sock == self.server_socket:
                    sock_fd, address = self.server_socket.accept()
                    self.sockets.append(sock_fd)
                    self.notify(sock_fd)
                else:
                    if sock in self.sockets:
                        self.sockets.remove(sock)
        self.sockets = [self.server_socket]
        sys.exit(0)

    def notify_observers(self, state):
        """
        Notifies all the observers with the new state.

        :param state: The new state
        :return: None
        """
        self.state = state + "\r\n" if not state.endswith("\r\n") else state
        for observer in self.sockets:
            if observer != self.server_socket:
                self.notify(observer)

    def notify(self, sock):
        """
        Notifies a single observer with the state.

        :param sock: The observer socket
        :return: None
        """
        try:
            sock.send(bytes(self.state, "ascii"))
        except:
            if sock in self.sockets:
                sock.close()
                self.sockets.remove(sock)

    def shutdown_server(self):
        """
        Shutdown the serving loop.
        The server might not be shutdown immediately but in few seconds it
        will eventually.
        :return: None
        """
        self.is_server_on = False
        for sock in self.sockets:
            sock.close()

if __name__ == "__main__":

    def observer_function(state):
        print("observer_function: {0}".format(state))

    from minesweeper_network.observer_board import ObserverBoard

    # Networked player is set up and in production is observing the player board
    player = NetworkedPlayer('localhost', 80)

    # When the player board updates it notifies player via its observer function
    # This function in return notifies the remote observers
    player.notify_observers("continue,2,HHHH/HHHH/HHHH")

    # A remote observer connects to the player
    observer_board = ObserverBoard("localhost", 80)

    # The ui observes the observer board
    observer_board.add_observer(observer_function)

    # State change happens at the player -> remote observers should be notified
    # -> The ui at remote observer should be notified that is the observer_function
    player.notify_observers("continue,2,01HH/1HHH/HHHH")
    player.notify_observers("loss,2,01HH/1XHH/HBHH")
    player.shutdown_server()
    input()
