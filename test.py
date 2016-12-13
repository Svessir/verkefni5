from minesweeper.minesweeper_board import MinesweeperBoard

def observer_function(state):
    rows = state.split("/")
    for row in rows:
        print(row)
    print()
    
board = MinesweeperBoard(10,10,0.1)
board.add_observer(observer_function)

while True:
    command = input()
    x,y = command.split()
    x = int(x)
    y = int(y)
    board.step_on_cell((x,y))
