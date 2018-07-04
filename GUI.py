# pylint: disable=W0612, E1120, W0614, E1101
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
from pywinauto import application
from pywinauto.findwindows import WindowAmbiguousError, WindowNotFoundError

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pytesseract.pytesseract.tesseract_cmd = resource_path('bin\\Tesseract-OCR\\tesseract')
tessdata_dir_config = '--tessdata-dir \"' + resource_path('bin\\Tesseract-OCR\\tessdata') + "\""
MINICAP = resource_path("bin\\MiniCap.exe")
window_icon = resource_path("icon.ico")

def focus_window(name):
    app = application.Application()
    try:
        app.connect(title_re=".*%s.*" % name)
        app_dialog = app.top_window_()
        app_dialog.Minimize()
        app_dialog.Restore()
        #app_dialog.SetFocus()
        logging.info("Restored {} window".format(name))
    except WindowNotFoundError:
        logging.info(" {} window not found.".format(name))
        pass
    except WindowAmbiguousError:
        logging.info("There are too many '{}' windows found.".format(name))
        pass


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Quick image grabber")
        self.master.report_callback_exception = self.report_callback_exception
        self.master.protocol("WM_DELETE_WINDOW", self.store_persistent_vars)
        self.master.iconbitmap(window_icon)

        # we need these attributes to build file name based on checkboxes and radiobutton
        self.warning = StringVar()
        self.error = StringVar()
        self.button = StringVar()
        self.message = StringVar()
        self.success = StringVar()
        self.extensionVar = StringVar()
        self.focusVar = StringVar()
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

        self.i2frame    = Frame(master, bd=2, relief=RIDGE)
        self.nameEntry  = Entry(self.i2frame, textvariable=self.fileName, bg='white')
        self.nameLabel  = Label(self.i2frame, text='File Name: ')
        self.cbFrame    = Frame(master, bd=1, relief=RIDGE)
        self.warningCB  = Checkbutton(self.cbFrame, text="Warning", variable=self.warning, onvalue="_warning", offvalue="")
        self.errorCB    = Checkbutton(self.cbFrame, text="Error", variable=self.error, offvalue="", onvalue="_error")
        self.buttonCB   = Checkbutton(self.cbFrame, text="Button", variable=self.button, offvalue="", onvalue="_button")
        self.messageCB  = Checkbutton(self.cbFrame, text="Message", variable=self.message, offvalue="", onvalue="_message")
        self.successCB  = Checkbutton(self.cbFrame, text="Success", variable=self.success, offvalue="", onvalue="_success")
        self.pngRB      = Radiobutton(self.cbFrame, text=".png", variable=self.extensionVar, value=".png")
        self.jpgRB      = Radiobutton(self.cbFrame, text=".jpg", variable=self.extensionVar, value=".jpg")
        self.focusLabel = Label(self.cbFrame, text="Window to focus:")
        self.focusEntry = Entry(self.cbFrame, textvariable=self.focusVar, bg='white') 
        self.sufixLabel = Label(self.cbFrame, text="Add sufixes: ")

        self.popup = Menu(master, tearoff=0)
        self.popup.add_command(label="Clear console", command=self.clear_console)

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
        self.focusLabel.grid(row=1, column=3)
        self.focusEntry.grid(row=1, column=4)

        self.lowerButtonsFrame.pack(pady=5)
        self.saveButton.grid(row=0, column=0, padx=5)
        self.ocrButton.grid(row=0, column=1, padx=5)
        

        #Logging related
        self.logWidget = ScrolledText.ScrolledText(master, state='disabled')
        self.logWidget.configure(font='TkFixedFont')
        self.logWidget.bind("<Button-3>", self.do_popup)
        self.logWidget.pack(pady=3, fill=X)

        file_formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-4s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        widget_formater = logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        
        text_handler = TextHandler(self.logWidget)
        text_handler.setFormatter(widget_formater)

        file_handler = logging.FileHandler('log.txt', mode='a')
        file_handler.setFormatter(file_formatter)
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(text_handler)
        logger.addHandler(file_handler)

        logging.debug("Path to minicap: " + MINICAP)
        logging.debug("Path to tesseract.exe: " + pytesseract.pytesseract.tesseract_cmd)
        logging.info("Welcome to ImageGrabber v2.2.0!")
        logging.info("Check github.com/douglasnavarro/ImageGrabber for new versions.\n")
        logging.info("Right-click the console to clear it.")

        #Load persistent vars from file or set default values
        self.load_persistent_vars()
                  
    def run_user_iteration(self):
        """
        Run basic user iteration:
        Minimize GUI, take SS, restore GUI, run OCR
        """
        logging.info("------Started interaction------")

        if 'win' in sys.platform and self.focusVar.get() != '':
            self.minimize_win32()
            time.sleep(0.2)
            focus_window(self.focusVar.get())
        elif 'win' not in sys.platform and self.focusVar.get() != '':
            logging.info("Window focusing feature is available only for Windows OS. Proceding with non-native minimize.")
            self.minimize()
        else:
            self.minimize()
        time.sleep(0.2)
        
        self.update_current_image()
        self.update_preview_widget()

        if 'win' in sys.platform:
            focus_window('image grabber')
        else:
            self.restore()
        
        logging.info("------Finished interaction------")
        self.update_name_entry()
        self.logWidget.delete('0', END)
        
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
        filename = self.fileName.get()
        filename = filename.replace("\n", "")
        path = self.path.get()
        
        if (os.path.isdir(path) is False):
            logging.info("Destination folder does not exist!")
            logging.info("Creating destination folder...")
            os.mkdir(path)
        try:
            image.save(path + "\\" + filename)
            logging.info("Saved " + path + "\\" + filename)
        except FileNotFoundError as err:
            messagebox.showerror('File not found error:', err)
    
    def clear_console(self):
        self.logWidget.config(state='normal')
        logging.debug('Clearing log console widget!')
        self.logWidget.delete(0.0, END)
        self.logWidget.config(state='disabled')

    def do_popup(self, event):
        try:
            self.popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup.grab_release()

    def report_callback_exception(self, *args):
        err = traceback.format_exception(*args)
        messagebox.showerror('Exception: ', err)
        logging.error(err)

    def minimize_win32(self):
        app = application.Application()
        try:
            app.connect(title_re=".*%s.*" % "image grabber")
            app_dialog = app.top_window_()
            app_dialog.Minimize()
            logging.info("Minimized image grabber.")
        except WindowNotFoundError:
            logging.info("Image grabber window not found. Could not minimize.")
            pass
        except WindowAmbiguousError:
            logging.info("There are too many 'image grabber' windows found. Could not minimize.")
            pass

    def store_persistent_vars(self):
        logging.info("Storing persistent variables before closing...")
        with open('persistent_vars.txt', 'w') as file:
            file.write('destination_foder={}\n'.format(self.path.get()))
            file.write('window_to_focus={}\n'.format(self.focusVar.get()))
            logging.info('Persistent variables stored! Closing now.')
        self.master.update()
        time.sleep(1)
        self.master.destroy()

    def load_persistent_vars(self):
        logging.info("Loading persistent variables if available...")
        try:
            with open('persistent_vars.txt', 'r') as file:
                dest_folder_line = file.readline()
                window_to_focus_line = file.readline()
        except FileNotFoundError:
            logging.info('No persistent variables file found.')
            self.path.set("C:\\Scripts\\Imagens")
            return
        
        folder_line_split = dest_folder_line.split('=')
        if len(folder_line_split) > 1:
            self.path.set(folder_line_split[1].replace('\n',''))
        else:
            self.path.set('')
        
        focus_line_split = window_to_focus_line.split('=')
        if len(focus_line_split) > 1:
            self.focusVar.set(focus_line_split[1].replace('\n',''))
        else:
            self.focusVar.set('')
        
        logging.info('Persistent settings loaded. Welcome back.')
        

class ThreadedOCR(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        img = Image.open(resource_path('preview.png'))

        logging.info("Pre-processing img for better OCR:")
        processed_img = img.convert('L')
        processed_img = self.resize_img(processed_img, 2)
        processed_img = self.increase_contrast(processed_img)
        
        if(logging.getLogger().isEnabledFor(logging.DEBUG)):
            processed_img.show()
        
        logging.info("Running ocr. This may take a few seconds...")
        ocr_string = pytesseract.image_to_string(processed_img, config=tessdata_dir_config)
        logging.debug("Sending ocr_string = " + ocr_string + " to queue")
        self.queue.put(ocr_string)
    
    def increase_contrast(self, img):
        logging.info("Increasing img contrast...")
        contrast = ImageEnhance.Contrast(img)
        return contrast.enhance(10)
    
    def resize_img(self, img, factor):
        logging.info("Increasing img size...")
        return img.resize((img.size[0]*factor, img.size[1]*factor), Image.ANTIALIAS)