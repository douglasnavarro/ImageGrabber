# pylint: disable=W0612, E1120, W0614, E1101
import sys
import os
import subprocess
from tkinter import *
from tkinter.ttk import *
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
from pywinauto import application, handleprops, findwindows


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pytesseract.pytesseract.tesseract_cmd = resource_path(
    'bin\\Tesseract-OCR\\tesseract')
tessdata_dir_config = '--tessdata-dir \"' + \
    resource_path('bin\\Tesseract-OCR\\tessdata') + "\""
MINICAP = resource_path("bin\\MiniCap.exe")
window_icon = resource_path("icon.ico")


class GUI:
    def __init__(self, master):
        """
        Builds GUI and initializes logger.
        """
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
        self.preview = Label(master, image=self.previewImg)
        self.lowerButtonsFrame = Frame(master)
        self.ssButton = Button(
            master, text="Take screenshot", command=self.run_user_iteration)
        self.saveButton = Button(
            self.lowerButtonsFrame, text='Save', command=self.save_image)
        self.ocrButton = Button(self.lowerButtonsFrame,
                                text='Run OCR', command=self.update_name_entry)

        self.iframe = Frame(master, relief=GROOVE)
        self.pathLabel = Label(self.iframe, text='Destination folder: ')
        self.pathEntry = Entry(self.iframe, textvariable=self.path)

        self.i2frame = Frame(master, relief=GROOVE)
        self.nameEntry = Entry(self.i2frame, textvariable=self.fileName)
        self.nameLabel = Label(self.i2frame, text='File Name: ')
        self.cbFrame = Frame(master, relief=GROOVE)
        self.warningCB = Checkbutton(
            self.cbFrame, text="Warning", variable=self.warning, onvalue="_warning", offvalue="")
        self.errorCB = Checkbutton(
            self.cbFrame, text="Error", variable=self.error, offvalue="", onvalue="_error")
        self.buttonCB = Checkbutton(
            self.cbFrame, text="Button", variable=self.button, offvalue="", onvalue="_button")
        self.messageCB = Checkbutton(
            self.cbFrame, text="Message", variable=self.message, offvalue="", onvalue="_message")
        self.successCB = Checkbutton(
            self.cbFrame, text="Success", variable=self.success, offvalue="", onvalue="_success")
        self.pngRB = Radiobutton(
            self.cbFrame, text=".png", variable=self.extensionVar, value=".png")
        self.jpgRB = Radiobutton(
            self.cbFrame, text=".jpg", variable=self.extensionVar, value=".jpg")
        self.sufixLabel = Label(self.cbFrame, text="Add sufixes: ")

        self.focus_choices = ['']
        self.focusVar.set('')

        self.focusFrame = Frame(master, relief=GROOVE)
        self.focusLabel = Label(self.focusFrame, text="Window to focus:")
        self.focusMenu = OptionMenu(
            self.focusFrame, self.focusVar, *self.focus_choices)
        self.updateFocusButton = Button(
            self.focusFrame, text='Update', command=self.update_focus_choices)

        self.popup = Menu(master, tearoff=0)
        self.popup.add_command(label="Clear console",
                               command=self.clear_console)

        # Layout of widgets
        self.cbFrame.pack(pady=5)

        self.focusFrame.pack(pady=5)
        self.focusLabel.grid(row=0, column=0, pady=3, padx=3)
        self.focusMenu.grid(row=0, column=1, pady=5, padx=5)
        self.updateFocusButton.grid(row=0, column=2, pady=5, padx=5)

        self.ssButton.pack(pady=5)
        self.preview.pack(pady=5)
        self.iframe.pack(padx=50, fill=X)
        self.pathLabel.pack(side=LEFT, padx=32, pady=5)
        self.pathEntry.pack(padx=5, pady=5, fill=X)

        self.i2frame.pack(padx=50, fill=X)
        self.nameLabel.pack(side=LEFT, padx=52, pady=5)
        self.nameEntry.pack(padx=5, pady=5, fill=X)

        self.sufixLabel.grid(row=0, column=0, pady=2, padx=2)
        self.warningCB.grid(row=0, column=1, pady=2)
        self.errorCB.grid(row=0, column=2, pady=2)
        self.buttonCB.grid(row=0, column=3, pady=2)
        self.messageCB.grid(row=0, column=4, pady=2)
        self.successCB.grid(row=0, column=5, pady=2)
        self.pngRB.grid(row=0, column=6, pady=2, padx=2)
        self.jpgRB.grid(row=0, column=7, pady=2, padx=2)

        self.lowerButtonsFrame.pack(pady=5)
        self.saveButton.grid(row=0, column=0, padx=5)
        self.ocrButton.grid(row=0, column=1, padx=5)

        # Logging related
        self.logWidget = ScrolledText.ScrolledText(master, state='disabled')
        self.logWidget.configure(font='TkFixedFont')
        self.logWidget.bind("<Button-3>", self.do_popup)
        self.logWidget.pack(pady=3, fill=X)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)-4s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        widget_formater = logging.Formatter(
            fmt='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')

        text_handler = TextHandler(self.logWidget)
        text_handler.setLevel(logging.INFO)
        text_handler.setFormatter(widget_formater)

        file_handler = logging.FileHandler('log.txt', mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(text_handler)
        logger.addHandler(file_handler)

        logging.debug("Path to minicap: " + MINICAP)
        logging.debug("Path to tesseract.exe: " +
                      pytesseract.pytesseract.tesseract_cmd)
        logging.info("Welcome to ImageGrabber v2.2.3!")
        logging.info(
            "Check github.com/douglasnavarro/ImageGrabber for new versions.")
        logging.info("Right-click the console to clear it.\n")

        # Load persistent vars from file or set default values
        self.load_persistent_vars()

    def run_user_iteration(self):
        """
        Run basic user iteration:
        Minimize GUI, focus window if selected, take SS, restore GUI, run OCR
        """
        logging.info("------Started interaction------")

        self.minimize()
        time.sleep(0.2)

        ranFocus = False
        if self.focusVar.get() != '' and 'win' in sys.platform.lower():
            try:
                self.focus_window(self.focusVar.get())
                ranFocus = True
                time.sleep(0.2)
            except Exception as e:
                logging.exception(
                    'An error occurred while focusing selected window.')

        self.update_current_image()
        self.update_preview_widget()

        if ranFocus is True:
            try:
                self.focus_window('image grabber')
            except Exception as e:
                logging.exception(
                    'An error occurred while focusing image grabber window.')
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
        status = subprocess.call(
            [MINICAP, "-captureregselect", "-exit", "-save", "..\\preview.png"])
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
            logging.info("Image size = {:d} x {:d} pixels".format(
                img.size[0], img.size[1]))

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
                logging.info("Adding only sufixes: " + " ".join(
                    [self.warning.get(), self.error.get(), self.button.get(), self.extensionVar.get()]))
                self.fileName.set(self.warning.get() + self.error.get() +
                                  self.button.get() + self.message.get() + self.extensionVar.get())
            else:
                logging.info("OCR result: " + ocr_string)
                ocr_string = ocr_string.replace(" ", "_")
                logging.info("Adding ocr_string and sufixes: " + " ".join([self.warning.get(
                ), self.error.get(), self.button.get(), self.success.get(), self.extensionVar.get()]))
                self.fileName.set(ocr_string + self.warning.get() + self.error.get() + self.success.get(
                ) + self.button.get() + self.message.get() + self.extensionVar.get())
        except Queue.Empty:
            self.master.after(100, self.process_queue)

    def save_image(self):
        """
        Saves current preview image to new file using path and name from user input
        Adds '\\' to end of path inserted by user for more intuitive usage
        Creates directory if does not exist
        """
        image = Image.open(self.pathToPreviewImg)
        filename = self.fileName.get()
        filename = filename.replace("\n", "")
        path = self.path.get()

        if (os.path.isdir(path) is False):
            logging.info("Destination folder does not exist!")
            logging.info("Creating destination folder...")
            os.makedirs(path, exist_ok=True)
        try:
            image.save(path + "\\" + filename)
            logging.info("Saved " + path + "\\" + filename)
        except FileNotFoundError as err:
            messagebox.showerror('File not found error:', err)

    def clear_console(self):
        """
        Method called when user clicks 'clear console'        
        """
        self.logWidget.config(state='normal')
        logging.debug('Clearing log console widget!')
        self.logWidget.delete(0.0, END)
        self.logWidget.config(state='disabled')

    def do_popup(self, event):
        """
        Shows popup menu. Used on 'clear console' feature.
        """
        try:
            self.popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup.grab_release()

    def report_callback_exception(self, *args):
        """
        Handles exception by showing popup and logging it.
        Prevents application from crashing.
        """
        err = traceback.format_exception(*args)
        messagebox.showerror('Exception: ', err)
        logging.error(err)

    def store_persistent_vars(self):
        """
        Saves destination folder to text file and destroys GUI.
        Lets user read on the console that variables were stored.
        """
        logging.info("Storing persistent variables before closing...")
        with open('persistent_vars.txt', 'w') as file:
            file.write('destination_foder={}\n'.format(self.path.get()))
            logging.info('Persistent variables stored! Closing now.')
        self.master.update()
        time.sleep(1)
        self.master.destroy()

    def load_persistent_vars(self):
        """
        Loads destination folder from text file.
        """
        logging.info("Loading persistent variables if available...")
        try:
            with open('persistent_vars.txt', 'r') as file:
                dest_folder_line = file.readline()
        except FileNotFoundError:
            logging.info('No persistent variables file found.')
            self.path.set("C:\\Scripts\\Imagens")
            return

        folder_line_split = dest_folder_line.split('=')
        if len(folder_line_split) > 1:
            self.path.set(folder_line_split[1].replace('\n', ''))
        else:
            self.path.set('')

        logging.info('Persistent settings loaded. Welcome back.')

    def focus_window(self, name):
        """
        Uses pywinauto to focus window that contains 'name' in its name.
        Windows only!
        """
        app = application.Application()
        try:
            app.connect(title_re=".*%s.*" % name)
            app_dialog = app.top_window_()
            app_dialog.Minimize()
            app_dialog.Restore()
            # app_dialog.SetFocus()
            logging.info("Restored {} window".format(name))
        except:
            raise

    def list_windows(self):
        """
        Returns a list of current open windows.
        Invalid elements such as '' and None are removed.
        Windows O.S ONLY!
        """
        hwnds = findwindows.find_windows()
        names = [handleprops.text(hwnd) for hwnd in hwnds]
        while '' in names:
            names.remove('')
        while None in names:
            names.remove(None)
        logging.debug('Detected following windows: {}'.format(names))
        names.append('')
        return names

    def update_focus_choices(self):
        """
        Updates dropdown menu choices with current windows open.
        """
        menu = self.focusMenu["menu"]
        menu.delete(0, "end")
        self.focus_choices = self.list_windows()
        for string in self.focus_choices:
            menu.add_command(
                label=string, command=lambda value=string: self.focusVar.set(value))


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

        logging.info("Running ocr. This may take a few seconds...")
        ocr_string = pytesseract.image_to_string(
            processed_img, config=tessdata_dir_config)
        logging.debug("Sending ocr_string = " + ocr_string + " to queue")
        self.queue.put(ocr_string)

    def increase_contrast(self, img):
        logging.info("Increasing img contrast...")
        contrast = ImageEnhance.Contrast(img)
        return contrast.enhance(10)

    def resize_img(self, img, factor):
        logging.info("Increasing img size...")
        return img.resize((img.size[0]*factor, img.size[1]*factor), Image.ANTIALIAS)
