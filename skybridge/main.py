import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from gui.radio_display import RadioDisplay

def main():
    root = tk.Tk()
    app = RadioDisplay(root)
    root.mainloop()

if __name__ == "__main__":
    main() 