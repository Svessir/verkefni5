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
		small = tk.Button(self, text='8x16', bg='#CCCCCC', 
			command=lambda: MinesweeperGameUI(self, self.create_minesweeper_board(8,16,0.15)))
		small.pack()
		medium = tk.Button(self, text='12x24', bg='#CCCCCC',
			command=lambda: MinesweeperGameUI(self, self.create_minesweeper_board(12,24,0.15)))
		medium.pack()
		large = tk.Button(self, text='16x32', bg='#CCCCCC',
			command=lambda: MinesweeperGameUI(self, self.create_minesweeper_board(16,32,0.15)))
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
		self.t = tk.Toplevel(self)
		self.buttons = {}
		self.bomb_path = "images/bomb.jpg"
		self.bomb_image = Image.open(self.bomb_path)
		self.bomb_image = self.bomb_image.resize((35,34), Image.ANTIALIAS)
		self.bomb = ImageTk.PhotoImage(self.bomb_image)
		self.flag_path = "images/flag_trans.jpg"
		self.flag_image = Image.open(self.flag_path)
		self.flag_image = self.flag_image.resize((35,34), Image.ANTIALIAS)
		self.flag = ImageTk.PhotoImage(self.flag_image)
		self.colors = ["white", "blue", "green", "red", "#AA00FF", "#002Eb8", "magenta", "#FF6633", "black"]
		board.add_observer(self.fill_board)

	def right_click_event_handler(self, event):
		print(event.widget.row, event.widget.col)
		self.board.mark_cell_toggle((event.widget.row, event.widget.col))

	def left_click_event_handler(self, event):
		print(event.widget.row, event.widget.col)
		self.board.step_on_cell((event.widget.row, event.widget.col))
		if event.widget['image'] == '' :
			event.widget.config(relief=tk.SUNKEN)

	def hax(self, event):
		event.widget.config(relief=tk.SUNKEN)

	def fill_board(self, state):
		print(state)
		state = state.split('/')
		if not self.buttons :
			for x, row in enumerate(state) :
				for y, col in enumerate(row) :
					self.but = tk.Button(self.t, height=2, width=5 , bg='#CCCCCC')
					self.but.grid(row=x, column=y)
					self.but.row = x
					self.but.col = y
					self.buttons[(x,y)] = self.but
					self.but.bind('<ButtonRelease-3>', self.right_click_event_handler)
					self.but.bind('<ButtonRelease-1>', self.left_click_event_handler)
		self.update_button_states(state)
			

	def update_button_states(self, state):
		for x, row in enumerate(state) :
			for y, col in enumerate(row) :	
				self.but = self.buttons[(x,y)]
				if str(col) != 'H':
					if str(col) == '0':
						self.but.config(state=tk.NORMAL, bg = '#EEEEEE', relief=tk.SUNKEN)
					elif str(col) == 'X' :
						self.but.config(image=self.bomb, width=35, height=35, bg='red')
					elif str(col) == 'B' :
						self.but.config(image=self.bomb, width=35, height=35)
					elif str(col) == 'M' :
						self.but.config(image=self.flag, width=35, height=35)
					else :
						self.but.config(text=str(col), state=tk.NORMAL, fg = self.colors[int(col)], 
							bg='#EEEEEE', relief=tk.SUNKEN)
				else :
					self.but.config(image='', height=2, width=5)


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

def on_exit():
	messagebox.showinfo("test", "test")
	app.destroy() 

app = Minesweeper()
app.protocol("WM_DELETE_WINDOW", on_exit)
app.mainloop()


