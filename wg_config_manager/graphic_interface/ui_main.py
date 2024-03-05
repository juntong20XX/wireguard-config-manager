"""
The ui based on tkinter.
"""
import tkinter as tk
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class MenuListItem[_T]:
    """
    dataclass to describe an item

    :param text: the label of menu, the text to display
    :param next_action: the next action after item clicked, show next MenuListItem or call passed function
    """
    text: str
    next_action: _T | Callable

    def get_menu(self, master: tk.Menu) -> tk.Menu:
        """
        :param master: the master of returned object
        :return: menu to display
        """
        ret = tk.Menu(master)
        if isinstance(self.next_action, MenuListItem):
            raise NotImplemented


class Window(tk.Frame):
    """
    The main window, should be a part of the main-window (like tk.Tk).
    Three key frames in a window object:
    1. Menu (self.menu) on top
    2. Frame (self.left_bar) on left to switch action items
    3. Frame (self.right_window) on right to display different action items
    """

    def __init__(self, master: tk.Tk,
                 cnf_window: Optional[dict] = None,
                 cnf_left_bar: Optional[dict] = None,
                 cnf_right_window: Optional[dict] = None,
                 *, auto_park=True):
        """

        """
        # -- init object
        super().__init__(master, {} if cnf_window is None else cnf_window)
        self._menu_items: list[MenuListItem] = []

        # -- setup frame on window
        # init
        self.left_bar = tk.Frame(self, {} if cnf_left_bar is None else cnf_left_bar)
        self.right_window = tk.Frame(self, {} if cnf_right_window is None else cnf_right_window)
        # pack
        self.left_bar.pack(side="left", fill="y", expand=False)
        self.right_window.pack(side="right", fill="both", expand=True)

        # -- setup menu
        self.menu = menu = tk.Menu(master)
        master.config(menu=menu)

        # -- park
        if auto_park:
            self.pack(fill="both", expand=True)

    def menu_item_append(self, item: MenuListItem):
        """

        :param item:
        :return:
        """
        if isinstance(item.next_action, MenuListItem):
            self.menu.add_cascade()
        self._menu_items.append(item)


def mainloop():
    """
    Run tkinter GUI mainloop.
    """
    root = tk.Tk()
    window = Window(root, cnf_right_window={"bg": "blue"})
    tk.mainloop()
