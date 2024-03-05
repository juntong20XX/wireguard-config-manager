"""
The ui based on tkinter.
"""
from wg_config_manager.storage import get_parser_from_config, dump_parser_to_config

import tkinter as tk


class EncryptFrame(tk.Frame):
    """
    About the Encrypt.
    """
    config_gpg_path: tk.Entry

    def setup_ui(self):
        """
        """
        # NOTE: Through read once when load ui, thread safety is guaranteed to a certain extent.
        config = get_parser_from_config()

        # setup widgets
        # -- Encrypt Options
        # TODO
        # -- GnuPG path
        self.config_gpg_path = tk.Entry(self)
        self.config_gpg_path["text"] = config.get("GnuPG", "path")

        # setup layout
        self.config_gpg_path.pack()


def mainloop():
    """
    Run tkinter GUI mainloop.
    """
    window = tk.Tk()

    encrypt_frame = EncryptFrame(window)
    encrypt_frame.setup_ui()
    encrypt_frame.pack()

    tk.mainloop()