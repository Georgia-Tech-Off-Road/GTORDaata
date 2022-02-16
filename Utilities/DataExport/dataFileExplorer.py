from tkinter import filedialog
import tkinter as tk


def open_data_file(file_type: str):
    # e.g. file_type = ".csv" or ".mat"
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=((str(file_type) + " files","*" + str(file_type)),("all files","*.*")))

    return file_path


if __name__ == "__main__":
    a = open_data_file(".csv .mat")
    print(a)
