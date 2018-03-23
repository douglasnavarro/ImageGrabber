import os
import subprocess
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

MINICAP = os.getcwd() + "\\bin\\MiniCap.exe"

def grab_image(name):
    return subprocess.call([MINICAP, "-captureregselect", "-exit", "-save", r"..\images\\" + name])


def main():

    root = Tk()

    ssButton = Button(root, text="Capturar ibagem")
    ssButton.pack(pady=10)

    previewImg = ImageTk.PhotoImage(Image.open("preview.png"))
    preview = Label(root, image = previewImg)
    preview.pack()

    iframe = Frame(root, bd=2, relief=RIDGE)
    iframe.pack(padx=50,fill=X)

    pathLabel = Label(iframe, text='Destino: ')
    pathLabel.pack(side=LEFT, padx=5, pady=5)

    path = StringVar()
    pathEntry = Entry(iframe, textvariable=path, bg='white')
    path.set(r'C:\scritps\images\preview.png')
    pathEntry.pack(padx=5, pady=5, fill=X)

    saveButton = Button(root, text='Salvar ibagem')
    saveButton.pack(pady=5)
    
    root.mainloop()

main()
