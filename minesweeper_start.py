import tkinter as tk
from minesweeper.minesweeper_board import MinesweeperBoard
from PIL import Image, ImageTk
from minesweeper_network.observer_board import ObserverBoard
from minesweeper_network.networked_player import NetworkedPlayer


class Minesweeper(tk.Tk):
    """
    Class that handles the display frames
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartingPage, SelectLevelPage, ObserverPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartingPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartingPage(tk.Frame):
    """
    Class for the elements in the starting page
    """
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        minesweeper_label = tk.Label(self, text='Minesweeper', font=("Helvetica", 16))
        minesweeper_label.pack(padx=10, pady=10)
        new_game_button = tk.Button(self, text='New Game', bg='#CCCCCC',
                                    command=lambda: controller.show_frame(SelectLevelPage))
        new_game_button.pack()
        observer_button = tk.Button(self, text='Observer', bg='#CCCCCC',
                                    command=lambda: controller.show_frame(ObserverPage))
        observer_button.pack()


class SelectLevelPage(tk.Frame):
    """
    Class for the elements of the level selection page
    """
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.host_name_string = 'Enter host name...'
        self.port_name_string = 'Enter port number...'
        name_label = tk.Label(self, text='Minesweeper', font=('Helvetica', 16))
        name_label.pack(padx=10, pady=10)
        connection_label = tk.Label(self, text='To establish a server for observers to connect to.',
                                    font=('Helvetica', 10), fg='blue')
        connection_label.pack(padx=10, pady=2)
        self.error_label = tk.Label(self, text='Wrong hostname or portnumber!', fg='red')
        host_entry = tk.Entry(self, bd=1)
        host_entry.insert(0, self.host_name_string)
        host_entry.bind('<ButtonRelease-1>', self.on_entry_click)
        host_entry.config(fg='grey')
        host_entry.pack()
        self.host_entry = host_entry
        port_entry = tk.Entry(self)
        port_entry.insert(0, self.port_name_string)
        port_entry.bind('<ButtonRelease-1>', self.on_entry_click)
        port_entry.config(fg='grey')
        port_entry.pack()
        self.port_entry = port_entry
        level_label = tk.Label(self, text='Select a board size',
                               font=('Helvetica', 12))
        level_label.pack(padx=10, pady=10)

        small = tk.Button(self, text='4x8', bg='#CCCCCC',
                          command=lambda: self.create_minesweeper_board(4, 8, 0.15))
        small.pack()
        medium = tk.Button(self, text='8x16', bg='#CCCCCC',
                           command=lambda: self.create_minesweeper_board(8, 16, 0.15))
        medium.pack()
        large = tk.Button(self, text='12x24', bg='#CCCCCC',
                          command=lambda: self.create_minesweeper_board(12, 24, 0.15))
        large.pack()
        back = tk.Button(self, text='Back', bg='#CCCCCC',
                         command=lambda: controller.show_frame(StartingPage))
        back.pack()
        label = tk.Label(self)
        label.pack()
        self.net_player = None

    def on_entry_click(self, event):
        event.widget.delete(0, "end")
        event.widget.insert(0, '')
        event.widget.config(text='', fg='black')

    def create_minesweeper_board(self, height, width, bomb_ratio):
        self.error_label.pack_forget()
        board = MinesweeperBoard(height, width, bomb_ratio)
        if (self.host_entry.get() == self.host_name_string and self.port_entry.get() == self.port_name_string) or (
                self.host_entry.get() == '' and self.port_entry.get() == ''):
            MinesweeperGameUI(self, board)
        elif self.host_entry.get() == self.host_name_string:
            try:
                self.net_player = NetworkedPlayer('', int(self.port_entry.get()))
                board.add_observer(self.net_player.notify_observers)
                MinesweeperGameUI(self, board, self.net_player.shutdown_server)
            except:
                self.error_label.pack()
        elif self.port_entry.get() == self.port_name_string:
            try:
                self.net_player = NetworkedPlayer(self.host_entry.get(), '')
                board.add_observer(self.net_player.notify_observers)
                MinesweeperGameUI(self, board, self.net_player.shutdown_server)
            except:
                self.error_label.pack()

        elif self.host_entry.get() != self.host_name_string and self.port_entry.get() != self.port_name_string:
            print(self.host_entry.get(), self.port_entry.get())
            try:
                self.net_player = NetworkedPlayer(self.host_entry.get(), int(self.port_entry.get()))
                board.add_observer(self.net_player.notify_observers)
                MinesweeperGameUI(self, board, self.net_player.shutdown_server)
            except:
                self.error_label.pack()


class MinesweeperGameUI(tk.Frame):
    """
    Class for the game UI
    """
    def __init__(self, master, board, on_close=None):
        tk.Frame.__init__(self, master)
        self.board = board
        self.toplevel = tk.Toplevel(self)
        self.on_close = on_close
        self.toplevel.protocol("WM_DELETE_WINDOW", self.shutdown_network_player)
        self.buttons = {}
        self.toolbar = None
        self.grid = None
        self.result = None
        self.bomb_path = "images/bomb.jpg"
        self.bomb_image = Image.open(self.bomb_path)
        self.bomb_image = self.bomb_image.resize((35, 38), Image.ANTIALIAS)
        self.bomb = ImageTk.PhotoImage(self.bomb_image)
        self.flag_path = "images/flag_trans.jpg"
        self.flag_image = Image.open(self.flag_path)
        self.flag_image = self.flag_image.resize((35, 38), Image.ANTIALIAS)
        self.flag = ImageTk.PhotoImage(self.flag_image)
        self.smile_cool_path = "images/smile.jpg"
        self.smile_cool_image = Image.open(self.smile_cool_path)
        self.smile_cool_image = self.smile_cool_image.resize((35, 38), Image.ANTIALIAS)
        self.smile_cool = ImageTk.PhotoImage(self.smile_cool_image)
        self.smile_sad_path = "images/smile_lost.jpg"
        self.smile_sad_image = Image.open(self.smile_sad_path)
        self.smile_sad_image = self.smile_sad_image.resize((35, 38), Image.ANTIALIAS)
        self.smile_sad = ImageTk.PhotoImage(self.smile_sad_image)
        self.colors = ["white", "blue", "green", "red", "#AA00FF", "#002Eb8", "magenta", "#FF6633", "black"]
        board.add_observer(self.fill_board)

    def right_click_event_handler(self, event):
        self.board.mark_cell_toggle((event.widget.row, event.widget.col))

    def left_click_event_handler(self, event):
        self.board.step_on_cell((event.widget.row, event.widget.col))
        if event.widget['image'] == '':
            self.after(5, lambda: event.widget.config(relief=tk.SUNKEN))


    def fill_board(self, board_info):
        """
        Inintializes the game-grid and all its elements
        """
        terminal, self.number_of_flags, state = board_info.split(',')
        state = state.split('/')
        if not self.toolbar:
            self.toolbar = tk.Frame(self.toplevel, bg='#EEEEEE')
            self.smile_but = tk.Button(self.toolbar, image=self.smile_cool)
            self.smile_but.bind('<ButtonRelease-1>', lambda e: self.board.reset())
            self.smile_but.grid(row=0, column=0)
            self.flag_label = tk.Label(self.toolbar, text=self.number_of_flags, fg='blue')
            self.flag_label.grid(row=0, column=1, padx=10)
            self.toolbar.pack()
        if not self.grid:
            self.grid = tk.Frame(self.toplevel)
            if not self.buttons:
                for x, row in enumerate(state):
                    for y, col in enumerate(row):
                        self.but = tk.Button(self.grid, height=2, width=5, bg='#CCCCCC')
                        self.but.grid(row=x, column=y)
                        self.but.row = x
                        self.but.col = y
                        self.buttons[(x, y)] = self.but
                        self.but.bind('<ButtonRelease-3>', self.right_click_event_handler)
                        self.but.bind('<ButtonRelease-1>', self.left_click_event_handler)
            self.grid.pack()
        self.update_button_states(board_info)

    def update_button_states(self, board_info):
        terminal, number_of_flags, state = board_info.split(',')
        state = state.split('/')
        self.flag_label = tk.Label(self.toolbar, text=self.number_of_flags, fg='blue')
        self.flag_label.grid(row=0, column=1, padx=10)
        self.toolbar.pack()
        for x, row in enumerate(state):
            for y, col in enumerate(row):
                self.but = self.buttons[(x, y)]
                if str(col) != 'H':
                    if str(col) == '0':
                        self.but.config(state=tk.NORMAL, bg='#EEEEEE', relief=tk.SUNKEN,
                                        image='', height=2, width=5)
                    elif str(col) == 'X':
                        self.but.config(image=self.bomb, height=35, width=38, bg='red')
                    elif str(col) == 'B':
                        self.but.config(image=self.bomb, height=35, width=38)
                    elif str(col) == 'M':
                        self.but.config(image=self.flag, height=35, width=38)
                    else:
                        self.but.config(text=str(col), state=tk.NORMAL, fg=self.colors[int(col)],
                                        bg='#EEEEEE', relief=tk.SUNKEN, image='', height=2, width=5)
                else:
                    self.but.config(image='', height=2, width=5, bg='#CCCCCC', text='', relief=tk.RAISED)
                    self.smile_but.config(image=self.smile_cool)
                    if self.result:
                        self.result.config(text='')
                        self.result.grid(row=0, column=2)

        if terminal == 'loss':
            self.smile_but.config(image=self.smile_sad)
            self.result = tk.Label(self.toolbar, text='You lost...', fg='red', font=('Helvetica', 16))
            self.result.grid(row=0, column=2, padx=10)
        if terminal == 'win':
            self.result = tk.Label(self.toolbar, text='You WON!', fg='green', font=('Helvetica', 16))
            self.result.grid(row=0, column=2, padx=10)
        if terminal == 'connection_loss':
            self.result = tk.Label(self.toolbar, text='Lost connection to player', fg='red', font=('Helvetica', 16))
            self.result.grid(row=0, column=2, padx=10)

    def shutdown_network_player(self):
        if self.on_close:
            self.on_close()
        self.toplevel.destroy()


class ObserverPage(tk.Frame):
    """
    Class that handles the observer GUI items
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.host_name_string = 'Enter host name...'
        self.port_name_string = 'Enter port number...'
        minesweeper_label = tk.Label(self, text='Minesweeper', font=("Helvetica", 16))
        minesweeper_label.pack(padx=10, pady=10)
        players_label = tk.Label(self, text='Select a player to observe', font=('Helvetica', 12))
        players_label.pack(padx=10, pady=10)
        self.error_label = tk.Label(self, text='Wrong hostname or portnumber!', fg='red')
        connection_label = tk.Label(self, text='Establish connection to players server', font=('Helvetica', 10),
                                    fg='blue')
        connection_label.pack(padx=10, pady=2)
        self.error_label = tk.Label(self, text='Wrong hostname or portnumber!', fg='red')
        host_entry = tk.Entry(self, bd=1)
        host_entry.insert(0, self.host_name_string)
        host_entry.bind('<ButtonRelease-1>', self.on_entry_click)
        host_entry.config(fg='grey')
        host_entry.pack()
        self.host_entry = host_entry
        port_entry = tk.Entry(self)
        port_entry.insert(0, self.port_name_string)
        port_entry.bind('<ButtonRelease-1>', self.on_entry_click)
        port_entry.config(fg='grey')
        port_entry.pack()
        self.port_entry = port_entry
        observe = tk.Button(self, text='Observe', bg='#CCCCCC',
                            command=lambda: self.on_observe())
        observe.pack()

        back = tk.Button(self, text='Back', bg='#CCCCCC',
                         command=lambda: controller.show_frame(StartingPage))
        back.pack()

    def on_entry_click(self, event):
        event.widget.delete(0, "end")
        event.widget.insert(0, '')
        event.widget.config(text='', fg='black')

    def on_observe(self):
        self.error_label.pack_forget()
        try:
            board = ObserverBoard(self.host_entry.get(), int(self.port_entry.get()))
            MinesweeperGameUI(self, board, board.shutdown_client)
        except Exception as error:
            self.error_label = tk.Label(self, text=str(error), fg='red')
            self.error_label.pack()


app = Minesweeper()
app.title('Minesweeper')
app.mainloop()
