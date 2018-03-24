import os
import subprocess
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, RIDGE, X, LEFT
from PIL import ImageTk, Image

MINICAP = os.getcwd() + "\\bin\\MiniCap.exe"


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Eu quero ibagens")

        # Creation of widgets
        self.path = StringVar()
        self.pathToPreviewImg = "preview.png"
        self.previewImg = ImageTk.PhotoImage(Image.open(self.pathToPreviewImg))

        self.preview = Label(master, image = self.previewImg)

        self.ssButton   = Button(master, text="Capturar ibagem")
        self.ssButton.bind('<Button-1>', self.update_preview_widget)
        self.saveButton = Button(master, text='Salvar ibagem')        

        self.iframe = Frame(master, bd=2, relief=RIDGE)
        self.pathLabel = Label(self.iframe, text='Destino: ')
        self.pathEntry = Entry(self.iframe, textvariable=self.path, bg='white')
        self.path.set(r"C:\Scripts\Imagens")

        # Layout of widgets
        self.ssButton.pack(pady=10)
        self.preview.pack()
        self.iframe.pack(padx=50,fill=X)
        self.pathLabel.pack(side=LEFT, padx=5, pady=5)
        self.pathEntry.pack(padx=5, pady=5, fill=X)
        self.saveButton.pack(pady=5)

    @classmethod
    def update_current_image(self):
        status = subprocess.call([MINICAP, "-captureregselect", "-exit", "-save", "..\\preview.png"])
        return status
    
    def update_preview_widget(self, event):
        status = self.update_current_image()
        if(status == 0):
            self.previewImg = ImageTk.PhotoImage(Image.open(self.pathToPreviewImg))
            self.preview.configure(image=self.previewImg)
            self.preview.image = self.previewImg
        return status

def main():
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()

main()
