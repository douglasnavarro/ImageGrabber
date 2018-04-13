# pylint: disable=W0612, E1120, W0614
import sys
import os
import subprocess
from tkinter import * 
from tkinter import messagebox
from PIL import ImageTk, Image, ImageEnhance
import pytesseract
import traceback
import logging
import tkinter.scrolledtext as ScrolledText
from TextHandler import TextHandler
import threading
import queue as Queue
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pytesseract.pytesseract.tesseract_cmd = resource_path('bin\\Tesseract-OCR\\tesseract')
MINICAP = resource_path("bin\\MiniCap.exe")
window_icon = resource_path("icon.ico")


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Quick image grabber")
        self.master.report_callback_exception = self.report_callback_exception
        self.master.iconbitmap(window_icon)

        # we need these attributes to build file name based on checkboxes and radiobutton
        self.warning = StringVar()
        self.error = StringVar()
        self.button = StringVar()
        self.message = StringVar()
        self.success = StringVar()
        self.extensionVar = StringVar()
        self.extensionVar.set(".png")
        self.path = StringVar()
        self.fileName = StringVar()
        self.pathToPreviewImg = resource_path("preview.png")
        self.pathToProcessedImg = resource_path("processed.png")
        self.previewImg = ImageTk.PhotoImage(Image.open(self.pathToPreviewImg))

        # Creation of widgets
        self.preview = Label(master, image = self.previewImg)
        self.lowerButtonsFrame = Frame(master, bd=0)
        self.ssButton   = Button(master, text="Take screenshot", command=self.run_user_iteration)
        self.saveButton = Button(self.lowerButtonsFrame, text='Save', command=self.save_image)
        self.ocrButton = Button(self.lowerButtonsFrame, text='Run OCR', command=self.update_name_entry)

        self.iframe = Frame(master, bd=2, relief=RIDGE)
        self.pathLabel = Label(self.iframe, text='Destination folder: ')
        self.pathEntry = Entry(self.iframe, textvariable=self.path, bg='white')
        self.path.set("C:\\Scripts\\Imagens")

        self.i2frame   = Frame(master, bd=2, relief=RIDGE)
        self.nameEntry = Entry(self.i2frame, textvariable=self.fileName, bg='white')
        self.nameLabel = Label(self.i2frame, text='File Name: ')
        self.cbFrame   = Frame(master, bd=1, relief=RIDGE)
        self.warningCB = Checkbutton(self.cbFrame, text="Warning", variable=self.warning, onvalue="_warning", offvalue="")
        self.errorCB   = Checkbutton(self.cbFrame, text="Error", variable=self.error, offvalue="", onvalue="_error")
        self.buttonCB  = Checkbutton(self.cbFrame, text="Button", variable=self.button, offvalue="", onvalue="_button")
        self.messageCB = Checkbutton(self.cbFrame, text="Message", variable=self.message, offvalue="", onvalue="_message")
        self.successCB = Checkbutton(self.cbFrame, text="Success", variable=self.success, offvalue="", onvalue="_success")
        self.pngRB     = Radiobutton(self.cbFrame, text=".png", variable=self.extensionVar, value=".png")
        self.jpgRB     = Radiobutton(self.cbFrame, text=".jpg", variable=self.extensionVar, value=".jpg")
        self.sufixLabel = Label(self.cbFrame, text="Add sufixes: ")

        # Layout of widgets
        self.cbFrame.pack(pady=3)
        self.ssButton.pack(pady=5)
        self.preview.pack(pady=5)
        self.iframe.pack(padx=50,fill=X)
        self.pathLabel.pack(side=LEFT, padx=32, pady=5)
        self.pathEntry.pack(padx=5, pady=5, fill=X)

        self.i2frame.pack(padx=50, fill=X)
        self.nameLabel.pack(side=LEFT, anchor=N, padx=5, pady=3)
        self.nameEntry.pack(padx=5, pady=3, fill=X)

        self.sufixLabel.grid(row=0, column=0)
        self.warningCB.grid(row=0, column=1)
        self.errorCB.grid(row=0, column=2)
        self.buttonCB.grid(row=0, column=3)
        self.messageCB.grid(row=0, column=4)
        self.successCB.grid(row=0, column=5)
        self.pngRB.grid(row=0, column=6)
        self.jpgRB.grid(row=0, column=7)

        self.lowerButtonsFrame.pack(pady=5)
        self.saveButton.grid(row=0, column=0, padx=5)
        self.ocrButton.grid(row=0, column=1, padx=5)
        

        #Logging related
        self.logWidget = ScrolledText.ScrolledText(master, state='disabled')
        self.logWidget.configure(font='TkFixedFont')
        self.logWidget.pack(pady=3, fill=X)

        file_formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-4s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        widget_formater = logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        
        text_handler = TextHandler(self.logWidget)
        text_handler.setFormatter(widget_formater)

        file_handler = logging.FileHandler('log.txt', mode='w')
        file_handler.setFormatter(file_formatter)
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(text_handler)
        logger.addHandler(file_handler)
                  
    def run_user_iteration(self):
        """
        Run basic user iteration:
        Minimize GUI, take SS, restore GUI, run OCR
        """
        logging.info("-----Started user interaction-----")
        self.minimize()
        time.sleep(0.2)
        self.update_current_image()
        self.update_preview_widget()
        self.restore()
        self.update_name_entry()
        logging.info("-----Ended user interaction-----")
        
    def update_current_image(self):
        """
        Runs minicap to save a temporary image
        Returns 0 for success
        """
        status = subprocess.call([MINICAP, "-captureregselect", "-exit", "-save", "..\\preview.png"])
        return status
    
    def update_preview_widget(self):
        """
        Updates preview image inside the GUI
        Takes screenshot using minicap through update_current_image
        and then updates tk variable previewImg
        """
        self.previewImg = ImageTk.PhotoImage(Image.open(self.pathToPreviewImg))
        self.preview.configure(image=self.previewImg)
        self.preview.image = self.previewImg
        logging.info("Updated preview widget.")
        with Image.open(self.pathToPreviewImg) as img:
            logging.info("Image size = {:d} x {:d} pixels".format(img.size[0], img.size[1]))

    def restore(self):
        """
        Restores window back to original size
        """
        self.master.deiconify()
        logging.info("Restored!")

    def minimize(self):
        """
        Minimizes window to the taskbar
        """
        self.master.iconify()
        logging.info("Minimized!")

    def update_name_entry(self):
        """
        Updates file name field using OCR string from image and checkboxes for sufixes
        If OCR fails an empty string is used
        """
        self.queue = Queue.Queue()
        ThreadedOCR(self.queue).start()
        self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            ocr_string = self.queue.get(0)
            if (ocr_string == ""):
                logging.info("OCR yielded no result.")
                logging.info("Adding only sufixes: " + " ".join([self.warning.get(), self.error.get(), self.button.get(), self.extensionVar.get()]))
                self.fileName.set(self.warning.get() + self.error.get() + self.button.get() + self.message.get() + self.extensionVar.get())
            else:
                logging.info("OCR result: " + ocr_string)
                ocr_string = ocr_string.replace(" ", "_")
                logging.info("Adding ocr_string and sufixes: " + " ".join([self.warning.get(), self.error.get(), self.button.get(), self.success.get(), self.extensionVar.get()]))
                self.fileName.set(ocr_string + self.warning.get() + self.error.get() + self.success.get()+ self.button.get() + self.message.get()  + self.extensionVar.get())
        except Queue.Empty:
            self.master.after(100, self.process_queue)

    def save_image(self):
        """
        Saves current preview image to new file using path and name from user input
        Adds '\\' to end of path inserted by user for more intuitive usage
        """
        image = Image.open(self.pathToPreviewImg)
        try:
            image.save(self.path.get() + "\\" + self.fileName.get())
            logging.info("Saved " + self.path.get() + "\\" + self.fileName.get())
        except FileNotFoundError as err:
            messagebox.showerror('File not found error:', err)
        
        image.close()
    
    def report_callback_exception(self, *args):
        err = traceback.format_exception(*args)
        messagebox.showerror('Exception: ', err)

class ThreadedOCR(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        with Image.open(resource_path('preview.png')) as img:
            processed_img = img.convert('L')
            processed_img = self.resize_img(processed_img, 2)
            processed_img = self.increase_contrast(processed_img)
            #processed_img.show()
            logging.info("Running ocr. This may take a few seconds...")
            ocr_string = pytesseract.image_to_string(processed_img)
            self.queue.put(ocr_string)
    
    def increase_contrast(self, img):
        logging.info("Increasing img contrast...")
        contrast = ImageEnhance.Contrast(img)
        return contrast.enhance(10)
    
    def resize_img(self, img, factor):
        return img.resize((img.size[0]*factor, img.size[1]*factor), Image.ANTIALIAS)


