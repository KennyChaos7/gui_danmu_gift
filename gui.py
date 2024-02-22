import time
from tkinter import StringVar, IntVar, Tk, ttk, Menu, Label, messagebox, Button


def create_window(window_title: str, width: int, height: int) -> Tk:
    window = Tk()
    window.title(window_title)
    window.configure(bg="#FFFFFF")
    window.geometry(f"{width}x{height}")
    window.bind("<Destroy>", window.destroy)
    window.protocol("WM_DELETE_WINDOW", window.destroy)
    return window


def create_tree_view(root: Tk, column_titles: tuple, column_widths: tuple) -> ttk.Treeview:
    i = 0
    columns = []
    while i < len(column_titles):
        columns.append(f'#{i}')
        i += 1
    tree_view = ttk.Treeview(root, columns=tuple(columns), show=('headings', 'tree'), height=10)
    i = 0
    while i < len(column_titles):
        tree_view.column(f'#{i}', width=column_widths[i], anchor='w')
        tree_view.heading(f'#{i}', text=column_titles[i])
        i += 1
    tree_view.pack()
    return tree_view


def update_tree_view(tree_view: ttk.Treeview, content: tuple):
    tree_view.insert('', 'end', text=content[0], values=content[1])
    tree_view.grid()

