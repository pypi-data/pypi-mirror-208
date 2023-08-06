import tktelerik
from tkinter import Tk

root = Tk()

theme = tktelerik.FluentDark()

board = tktelerik.TaskBoard()
board.configure(theme="FluentDark")

column1 = tktelerik.TaskBoardColumnElement()

card1 = tktelerik.TaskCardElement()
card2 = tktelerik.TaskCardElement()

column1.add_card(card1)
column1.add_card(card2)

column2 = tktelerik.TaskBoardColumnElement()

card3 = tktelerik.TaskCardElement()
card4 = tktelerik.TaskCardElement()

column2.add_card(card3)
column2.add_card(card4)

board.add_column(column1)
board.add_column(column2)
board.pack(fill="both", expand="yes")

root.mainloop()
