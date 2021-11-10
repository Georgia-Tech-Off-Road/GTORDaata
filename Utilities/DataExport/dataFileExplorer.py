import tkinter as tk
from tkinter import filedialog

def open_data_file(file_type):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilenames(filetypes=((str(file_type) + " files","*" + str(file_type)),("all files","*.*")))

    return file_path