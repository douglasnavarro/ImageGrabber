import os
import subprocess
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, Checkbutton, RIDGE, X, LEFT, Radiobutton, N, IntVar
from PIL import ImageTk, Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'B:/dev/ImageGrabber/env/Tesseract-OCR/tesseract'
MINICAP = os.getcwd() + "\\bin\\MiniCap.exe"


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Eu quero ibagens")
        self.warning = StringVar()
        self.error = StringVar()
        self.button = StringVar()
        self.message = StringVar()
        self.extensionVar = StringVar()
        self.extensionVar.set(".png")

        # Creation of widgets
        self.path = StringVar()
        self.fileName = StringVar()
        self.pathToPreviewImg = "preview.png"
        self.previewImg = ImageTk.PhotoImage(Image.open(self.pathToPreviewImg))

        self.preview = Label(master, image = self.previewImg)

        self.lowerButtonsFrame = Frame(master, bd=0)
        self.ssButton   = Button(master, text="Capturar ibagem")
        self.ssButton.bind('<Button-1>', self.update_preview_widget)
        self.saveButton = Button(self.lowerButtonsFrame, text='Salvar ibagem')
        self.ocrButton = Button(self.lowerButtonsFrame, text='Rodar OCR')
        self.ocrButton.bind('<Button-1>', self.update_name_entry)
        
        self.iframe = Frame(master, bd=2, relief=RIDGE)
        self.pathLabel = Label(self.iframe, text='Destino: ')
        self.pathEntry = Entry(self.iframe, textvariable=self.path, bg='white')
        self.path.set(r"C:\Scripts\Imagens")

        self.i2frame   = Frame(master, bd=2, relief=RIDGE)
        self.nameEntry = Entry(self.i2frame, textvariable=self.fileName, bg='white')
        self.nameLabel = Label(self.i2frame, text='Nome do arquivo: ')
        self.cbFrame   = Frame(self.i2frame, bd=1, relief=RIDGE)
        self.warningCB = Checkbutton(self.cbFrame, text="Warning", variable=self.warning, onvalue="_warning", offvalue="")
        self.errorCB   = Checkbutton(self.cbFrame, text="Error", variable=self.error, offvalue="", onvalue="_error")
        self.buttonCB  = Checkbutton(self.cbFrame, text="Button", variable=self.button, offvalue="", onvalue="_button")
        self.messageCB = Checkbutton(self.cbFrame, text="Message", variable=self.message, offvalue="", onvalue="_message")
        self.pngRB     = Radiobutton(self.cbFrame, text=".png", variable=self.extensionVar, value=".png")
        self.jpgRB     = Radiobutton(self.cbFrame, text=".jpg", variable=self.extensionVar, value=".jpg")
        self.sufixLabel = Label(self.cbFrame, text="Adicionar sufixo: ")

        # Layout of widgets
        self.ssButton.pack(pady=5)
        self.preview.pack(pady=5)
        self.iframe.pack(padx=50,fill=X)
        self.pathLabel.pack(side=LEFT, padx=32, pady=5)
        self.pathEntry.pack(padx=5, pady=5, fill=X)

        self.i2frame.pack(padx=50, fill=X)
        self.nameLabel.pack(side=LEFT, anchor=N, padx=5, pady=3)
        self.nameEntry.pack(padx=5, pady=3, fill=X)
        self.cbFrame.pack(side=LEFT, pady=3)

        self.sufixLabel.grid(row=0, column=0)
        self.warningCB.grid(row=0, column=1)
        self.errorCB.grid(row=0, column=2)
        self.buttonCB.grid(row=0, column=3)
        self.messageCB.grid(row=0, column=4)
        self.pngRB.grid(row=0, column=5)
        self.jpgRB.grid(row=0, column=6)

        self.lowerButtonsFrame.pack(pady=5)
        self.saveButton.grid(row=0, column=0, padx=5)
        self.ocrButton.grid(row=0, column=1, padx=5)
        
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
            print("Updated preview widget")
        return status

    def update_name_entry(self, event):
        ocr_string = pytesseract.image_to_string(Image.open('preview.png'))
        if (ocr_string == ""):
            print("OCR failed.")
            print("Adding only sufixes: " + " ".join([self.warning.get(), self.error.get(), self.button.get(), self.extensionVar.get()]))
            self.fileName.set(self.warning.get() + self.error.get() + self.button.get() + self.extensionVar.get())
        else:
            print("ocr_string: " + ocr_string)
            ocr_string = ocr_string.replace(" ", "_")
            print("Adding ocr_string and sufixes: " + " ".join([self.warning.get(), self.error.get(), self.button.get(), self.extensionVar.get()]))
            self.fileName.set(ocr_string + self.warning.get() + self.error.get() + self.button.get() + self.extensionVar.get())

def main():
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()

main()
