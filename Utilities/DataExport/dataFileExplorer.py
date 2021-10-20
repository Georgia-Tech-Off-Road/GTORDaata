import tkinter as tk
from tkinter import filedialog

def open_data_file(file_type):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(defaultextension=file_type)

    return file_path