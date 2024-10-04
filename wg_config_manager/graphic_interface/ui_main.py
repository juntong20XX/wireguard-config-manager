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
    :param next_action: the next action after item clicked, call passed function
    """
    text: str
    next_action: Callable


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
        self.window_frames: list[tk.Frame] = []

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
        Add an item to the end of menu.
        :param item:
        """
        self.menu.add_command(label=item.text, command=item.next_action)
        self._menu_items.append(item)

    def menu_item_insert(self, index: int, item: MenuListItem):
        """
        Insert an item to menu.
        :param index: index of the new item to be, starts with 0
        :param item:
        """
        self._menu_items.insert(index, item)
        self.menu.add_command(label=item.text, command=item.next_action)

    def menu_item_pop(self, index: int):
        """
        pop the item at `index`
        :param index: index of the item to be popped
        """
        item = self._menu_items.pop(index)
        self.menu.deletecommand(item.text)

    def menu_item_remove(self, remove: str | Callable | MenuListItem):
        """

        :param remove:
        :return:
        """
        if isinstance(remove, MenuListItem):
            index = self._menu_items.index(remove)
            return self.menu_item_pop(index)
        if isinstance(remove, str):
            for index in range(len(self._menu_items)):
                if self._menu_items[index].text == remove:
                    return self.menu_item_pop(index)
        for index in range(len(self._menu_items)):
            if self._menu_items[index].next_action == remove:
                return self.menu_item_pop(index)
        raise KeyError(f"cannot found {remove} in menu list")


def mainloop():
    """
    Run tkinter GUI mainloop.
    """
    root = tk.Tk()
    window = Window(root, cnf_right_window={"bg": "blue"})
    tk.mainloop()
