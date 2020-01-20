#!/usr/bin/env python3
import os
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

import util
from diary import Diary
from publish import find_header, split_text_with_comments, split_text_with_posts


class Window:
    def __init__(self):
        self.root = Tk()
        self.root.title("Post-ap text cutter")
        frame = Frame(self.root, width=520, height=240)
        frame.pack(side='top', fill='x')

        login_label = Label(frame, text="Login")
        login_label.place(x=10, y=20)
        self.login_edit = Entry(frame)
        self.login_edit.place(x=70, y=20, width=100, height=20)

        password_label = Label(frame, text="Password")
        password_label.place(x=10, y=50)
        self.password_edit = Entry(frame)
        self.password_edit.place(x=70, y=50, width=100, height=20)

        diary_id_label = Label(frame, text="Diary ID")
        diary_id_label.place(x=240, y=50)
        self.diary_id_edit = Entry(frame)
        self.diary_id_edit.place(x=290, y=50, width=200, height=20)

        filename_label = Label(frame, text="Text file")
        filename_label.place(x=10, y=100)
        self.filename_edit = Entry(frame)
        self.filename_edit.place(x=70, y=100, width=180, height=20)

        open_button = Button(frame, text='Browse...')
        open_button.bind("<ButtonRelease-1>", self.load_file)
        open_button.place(x=260, y=100, width=60, height=20)

        self.split_type = IntVar(value=1)
        usecomments_checkbutton = Radiobutton(text="Post + comments", value=1, variable=self.split_type)
        usecomments_checkbutton.place(x=10, y=130)
        useposts_checkbutton = Radiobutton(text="Multiple posts", value=2, variable=self.split_type)
        useposts_checkbutton.place(x=10, y=160)

        doit_button = Button(frame, text='Do it!', bg="#ff5e0e")
        doit_button.place(x=100, y=190, width=320, height=20)
        doit_button.bind("<ButtonRelease-1>", self.do_it)

    def run(self):
        self.root.mainloop()

    def load_file(self, ev):
        filename = askopenfilename(filetypes=[('*.txt files', '.txt')])
        self.filename_edit.delete(0, 'end')
        if not filename:
            return
        self.filename_edit.insert(0, filename)
        return True

    def do_it(self, ev):
        login = self.login_edit.get()
        password = self.password_edit.get()
        diary_id = self.diary_id_edit.get()
        filename = self.filename_edit.get()
        split_type = self.split_type.get()

        if not login:
            messagebox.showinfo("Error", "Логин не задан")
            return
        if not diary_id:
            messagebox.showinfo("Error", "Адрес сообщества не задан")
            return
        if not filename:
            messagebox.showinfo("Error", "Путь к файлу не задан")
            return

        api = Diary()
        try:
            api.login(login, password)
            text_with_header = util.load(filename)
            prefix = os.path.splitext(filename)[0]
            text_with_header = util.fix_characters(text_with_header)
            header, text = find_header(text_with_header)
            if split_type == 1:
                post, comments = split_text_with_comments(header, text)
                util.store(prefix + "_post.txt", post)
                for i, comment in enumerate(comments):
                    util.store(prefix + "_comment_%d.txt" % (i+1), comment)

                # Send to diary
                post_id = api.new_post(post, diary_id)
                for comment in comments:
                    api.add_comment(post_id, comment)
                messagebox.showinfo("Info", "Пост успешно опубликован, тексты комментариев ищите в файлах *comment_N.txt")
            else:
                posts = split_text_with_posts(header, text)
                for i, post in enumerate(posts):
                    util.store(prefix + "_post_%d.txt" % (i + 1), post)

                # Send to diary
                for post in posts:
                    api.new_post(post, diary_id)
                messagebox.showinfo("Info", "Посты успешно опубликованы. Тексты продублированы в файлы *post_N.txt")
        except Exception as e:
            messagebox.showinfo("Error", str(e))
            return


if __name__ == "__main__":
    w = Window()
    w.run()
