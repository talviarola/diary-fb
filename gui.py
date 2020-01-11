#!/usr/bin/env python3

from tkinter import *
from tkinter.filedialog import askopenfilename


class Window:
    def __init__(self):
        self.root = Tk()
        frame = Frame(self.root, height=100, width=200)
        frame.pack(side='top', fill='x')

        self.login_edit = Text(frame)
        self.login_edit.place(x=10, y=10, width=100, height=20)

        open_button = Button(frame, text='Open')
        open_button.bind("<ButtonRelease-1>", self.load_file)
        open_button.place(x=115, y=10, width=40, height=20)

        quit_button = Button(frame, text='Quit')
        quit_button.bind("<Button-1>", self.quit)
        quit_button.place(x=110, y=50, width=40, height=40)

        self.login = None
        self.password = None
        self.community = None

    def run(self):
        self.root.mainloop()

    def load_file(self, ev):
        filename = askopenfilename(filetypes=[('*.txt files', '.txt')])
        self.login_edit.delete('1.0', 'end')
        if not filename:
            return
        self.login_edit.insert('1.0', filename)
        return True

    def quit(self, ev):
        self.root.destroy()


if __name__ == "__main__":
    w = Window()
    w.run()
