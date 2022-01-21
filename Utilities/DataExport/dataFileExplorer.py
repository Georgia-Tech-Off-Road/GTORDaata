import tkinter as tk
from tkinter import filedialog

def open_data_file(file_type):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=((str(file_type) + " files","*" + str(file_type)),("all files","*.*")))

    print(file_path)

    return file_path