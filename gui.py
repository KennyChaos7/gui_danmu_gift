from tkinter import Tk, Toplevel, ttk
import ttkwidgets

tree_view_index = 0


def create_window(window_title: str, width: int, height: int) -> Tk:
    window = Tk()
    window.title(window_title)
    window.configure(bg="#FFFFFF")

    window.geometry(f"{width}x{height}")
    window.bind("<Destroy>", window.destroy)
    window.protocol("WM_DELETE_WINDOW", window.destroy)
    return window


def create_child_window(window_title: str, width: int, height: int) -> Tk:
    window = Toplevel()
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
    vertical_bar = ttk.Scrollbar(root, orient="vertical", command=tree_view.yview)
    tree_view.configure(yscrollcommand=vertical_bar.set)
    vertical_bar.pack(side='right', fill='y')
    tree_view.pack(side='left', fill='both', expand=True)
    return tree_view


def create_checked_tree_view(root: Tk, column_titles: tuple, column_widths: tuple) -> ttkwidgets.CheckboxTreeview:
    i = 0
    columns = []
    while i < len(column_titles):
        columns.append(f'#{i}')
        i += 1
    tree_view = ttkwidgets.CheckboxTreeview(root, columns=tuple(columns), show=('headings', 'tree'), height=10)
    i = 0
    while i < len(column_titles):
        tree_view.column(f'#{i}', width=column_widths[i], anchor='w')
        tree_view.heading(f'#{i}', text=column_titles[i])
        i += 1
    vertical_bar = ttk.Scrollbar(root, orient="vertical", command=tree_view.yview)
    tree_view.configure(yscrollcommand=vertical_bar.set)
    vertical_bar.pack(side='right', fill='y')
    tree_view.pack(side='left', fill='both', expand=True)
    return tree_view


def update_tree_view(tree_view, content: tuple):
    global tree_view_index
    tree_view.insert('', 'end', iid=f"{tree_view_index}", text=content[0], values=content[1:])
    # tree_view.grid()
    tree_view.see(f"{tree_view_index}")
    tree_view_index += 1

