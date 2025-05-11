import os
import sys
import tkinter as tk
from skybridge.gui.radio_display import RadioDisplay

def main():
    """Main entry point for the SkyBridge application"""
    root = tk.Tk()
    app = RadioDisplay(root)
    root.mainloop()

if __name__ == "__main__":
    main() 