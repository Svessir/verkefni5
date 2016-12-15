import tkinter as tk   # python3
from minesweeper.minesweeper_board import MinesweeperBoard
from PIL import Image, ImageTk
from tkinter import PhotoImage
#from minesweeperUI import Application
from minesweeper_network.observer_board import ObserverBoard
from minesweeper_network.networked_player import NetworkedPlayer
from tkinter import messagebox
import time
	 

class Minesweeper(tk.Tk):
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
	def __init__(self, master, controller):
		tk.Frame.__init__(self, master)
		name_label = tk.Label(self, text='Minesweeper', font=('Helvetica', 16))
		name_label.pack(padx=10, pady=10)
		level_label = tk.Label(self, text='Select a board size', 
			font=('Helvetica',12))
		level_label.pack(padx=10, pady=10)
		small = tk.Button(self, text='4x8', bg='#CCCCCC', 
			command=lambda: MinesweeperGameUI(self, self.create_minesweeper_board(4,8,0.15)))
		small.pack()
		medium = tk.Button(self, text='8x16', bg='#CCCCCC',
			command=lambda: MinesweeperGameUI(self, self.create_minesweeper_board(8,16,0.15)))
		medium.pack()
		large = tk.Button(self, text='12x24', bg='#CCCCCC',
			command=lambda: MinesweeperGameUI(self, self.create_minesweeper_board(12,24,0.15)))
		large.pack()
		back = tk.Button(self, text='Back', bg='#CCCCCC', 
			command=lambda: controller.show_frame(StartingPage))
		back.pack()
		label = tk.Label(self)
		label.pack()
		self.net_player = None

	def create_minesweeper_board(self, height, width, bomb_ratio):
		board = MinesweeperBoard(height, width, bomb_ratio)
		self.net_player = NetworkedPlayer("localhost", 80)
		board.add_observer(self.net_player.notify_observers)
		return board


class MinesweeperGameUI(tk.Frame):
	def __init__(self, master, board):
		tk.Frame.__init__(self, master)
		self.board = board
		self.toplevel = tk.Toplevel(self)
		self.buttons = {}
		self.toolbar = None
		self.grid = None
		self.bomb_path = "images/bomb.jpg"
		self.bomb_image = Image.open(self.bomb_path)
		self.bomb_image = self.bomb_image.resize((35,38), Image.ANTIALIAS)
		self.bomb = ImageTk.PhotoImage(self.bomb_image)
		self.flag_path = "images/flag_trans.jpg"
		self.flag_image = Image.open(self.flag_path)
		self.flag_image = self.flag_image.resize((35,38), Image.ANTIALIAS)
		self.flag = ImageTk.PhotoImage(self.flag_image)
		self.smile_cool_path = "images/smile.jpg"
		self.smile_cool_image = Image.open(self.smile_cool_path)
		self.smile_cool_image = self.smile_cool_image.resize((35,38), Image.ANTIALIAS)
		self.smile_cool = ImageTk.PhotoImage(self.smile_cool_image)
		self.smile_sad_path = "images/smile_lost.jpg"
		self.smile_sad_image = Image.open(self.smile_sad_path)
		self.smile_sad_image = self.smile_sad_image.resize((35,38), Image.ANTIALIAS)
		self.smile_sad = ImageTk.PhotoImage(self.smile_sad_image)
		self.colors = ["white", "blue", "green", "red", "#AA00FF", "#002Eb8", "magenta", "#FF6633", "black"]
		board.add_observer(self.fill_board)

	def right_click_event_handler(self, event):
		print(event.widget.row, event.widget.col)
		self.board.mark_cell_toggle((event.widget.row, event.widget.col))

	def left_click_event_handler(self, event):
		print(event.widget.row, event.widget.col)
		self.board.step_on_cell((event.widget.row, event.widget.col))
		if event.widget['image'] == '' :
			self.after(5, lambda: event.widget.config(relief=tk.SUNKEN))
			

	def fill_board(self, board_info):
		terminal, self.number_of_flags, state = board_info.split(',')
		print(terminal, self.number_of_flags)
		state = state.split('/')
		print(state)
		if not self.toolbar:
			self.toolbar = tk.Frame(self.toplevel, bg='#EEEEEE')
			self.smile_but = tk.Button(self.toolbar, image=self.smile_cool)
			self.smile_but.bind('<ButtonRelease-1>', self.dostuff)
			self.smile_but.grid(row=0, column=0)
			self.flag_label = tk.Label(self.toolbar, text=self.number_of_flags, fg='blue')
			self.flag_label.grid(row=0, column=1, padx=10)
			self.toolbar.pack()
		if not self.grid :
			self.grid = tk.Frame(self.toplevel)
			if not self.buttons :
				for x, row in enumerate(state) :
					for y, col in enumerate(row) :
						self.but = tk.Button(self.grid, height=2, width=5 , bg='#CCCCCC')
						self.but.grid(row=x, column=y)
						self.but.row = x
						self.but.col = y
						self.buttons[(x,y)] = self.but
						self.but.bind('<ButtonRelease-3>', self.right_click_event_handler)
						self.but.bind('<ButtonRelease-1>', self.left_click_event_handler)
			self.grid.pack()
		self.update_button_states(board_info)

	def dostuff(self, event):
		print('Hommar og lesbiur')
			

	def update_button_states(self, board_info):
		terminal, number_of_flags, state = board_info.split(',')
		state = state.split('/')
		self.flag_label = tk.Label(self.toolbar, text=self.number_of_flags, fg='blue')
		self.flag_label.grid(row=0, column=1, padx=10)
		self.toolbar.pack()
		for x, row in enumerate(state) :
			for y, col in enumerate(row) :	
				self.but = self.buttons[(x,y)]
				if str(col) != 'H':
					if str(col) == '0':
						self.but.config(state=tk.NORMAL, bg = '#EEEEEE', relief=tk.SUNKEN, 
							image='', height=2, width=5)
					elif str(col) == 'X' :
						self.but.config(image=self.bomb, height=35, width=38, bg='red')
					elif str(col) == 'B' :
						self.but.config(image=self.bomb, height=35, width=38)
					elif str(col) == 'M' :
						self.but.config(image=self.flag, height=35, width=38)
					else :
						self.but.config(text=str(col), state=tk.NORMAL, fg = self.colors[int(col)], 
							bg='#EEEEEE', relief=tk.SUNKEN, image='', height=2, width=5)
				else :
					self.but.config(image='', height=2, width=5)
		if terminal == 'loss' :
			#self.on_defeat()
			self.smile_but.config(image=self.smile_sad)
			self.defeat = tk.Label(self.toolbar, text='You lost...', fg='red', font=('Helvetica', 16))
			self.defeat.grid(row=0, column=2, padx=10)
		if terminal == 'win' :
			#self.on_win()
			self.win = tk.Label(self.toolbar, text='You WON!', fg='green', font=('Helvetica', 16))
			self.win.grid(row=0, column=2, padx=10)


	def on_win(self):
		result = messagebox.askquestion("Minesweeper", "You won! Do you want to play again", parent=self.toplevel)

	def on_defeat(self):
		result = messagebox.askquestion("Minesweeper", "You lost.... Do you want to play again", parent=self.toplevel)



class ObserverPage(tk.Frame):
	def __init__(self, master, controller):
		super().__init__(master)
		minesweeper_label = tk.Label(self, text='Minesweeper', font=("Helvetica", 16))
		minesweeper_label.pack(padx=10, pady=10)
		players_label = tk.Label(self, text='Select a player to observe', font=('Helvetica', 12))
		players_label.pack(padx=10, pady=10)
		observe = tk.Button(self, text='Observe', bg='#CCCCCC', 
			command=lambda: MinesweeperGameUI(self, ObserverBoard("localhost", 80)))
		observe.pack()

		back = tk.Button(self, text='Back', bg='#CCCCCC', 
			command=lambda: controller.show_frame(StartingPage))
		back.pack()

class MinesweeperGame(tk.Frame):
	def __init__(self, master, controller, size):
		tk.Frame.__init__(self, master)
		self.height = size
		self.width = size
		print(size)

app = Minesweeper()
app.mainloop()


