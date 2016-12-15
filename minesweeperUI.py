import tkinter as tk
from PIL import Image, ImageTk
from tkinter import PhotoImage
import random
from minesweeper.minesweeper_board import MinesweeperBoard



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        #master.minsize(height=175, width=165)
        #self.pack()
        bomb_path = "images/bomb.jpg"
        bomb_image = Image.open(bomb_path)
        bomb_image = bomb_image.resize((35,34), Image.ANTIALIAS)
        self.bomb = ImageTk.PhotoImage(bomb_image)
        flag_path = "images/flag_trans.jpg"
        flag_image = Image.open(flag_path)
        flag_image = flag_image.resize((35,34), Image.ANTIALIAS)
        self.flag = ImageTk.PhotoImage(flag_image)
        self.colors = ["", "blue", "green", "red", "#AA00FF", "#002Eb8", "magenta", "#FF6633", "black"]
        #self.create_widgets()


    def locate_bomb(self, event):
        number = random.randint(1,8)
        event.widget['text'] = str(number)
        event.widget['fg'] = self.colors[number] 
        event.widget['bg'] = 'white'
        event.widget.config(relief=tk.SUNKEN)

    def place_flag(self, event):
        event.widget.config(image=self.flag, width=35, height=33) # keep a reference!
        
    def starting_menu(self):
        new_game = tk.Button(self, height=8, width=16, text='New game', 
            bg='#CCCCCC', state='normal')
        new_game.grid(row=0, column=0)
        new_game.on = False
        self.new_game = new_game
        observe = tk.Button(self, height=8, width=16, text='Observe game', 
            bg='#CCCCCC', state='normal')
        observe.grid(row=1, column=0)
        observe.on = False
        self.observe = observe
        if self.new_game['state'] == 'normal':
            new_game.bind('<Button-1>', self.create_widgets)
        #if self.observe['state'] == 'normal':
        #    observe.bind('<Button-1>', self.create_widgets)



    def create_widgets(self):
        #self.new_game.destroy()
        #self.observe.destroy()
        for r in range(10):
            for c in range(10):
                but = tk.Button(self, height=2, width=5 , bg='#CCCCCC')
                but.grid(row=r, column=c)
                but.row = r
                but.col = c
                but.on = False
                #but.bind('<Button-3>', self.place_flag)
                #but.bind('<Button-1>', self.locate_bomb)


    def update_widget(self, event):
        pass               

#root = tk.Tk()
#app = Application(master=root)
#app.mainloop()


