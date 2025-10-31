import tkinter as tk
from gui import GUI
from cli import CLI
import sys


if __name__ == "__main__":
    # GUI mode
    if len(sys.argv) == 1:
        root = tk.Tk()
        app = GUI(root)
        root.mainloop()

    else:

        # CLI mode (make sure to enter search.py <filename> <method>)
        if len(sys.argv) != 3:
            raise SystemExit("Usage: python search.py <filename> <method>")
        
        filename = sys.argv[1]
        method = sys.argv[2]      

        cli = CLI(filename, method)
        cli.search()

    