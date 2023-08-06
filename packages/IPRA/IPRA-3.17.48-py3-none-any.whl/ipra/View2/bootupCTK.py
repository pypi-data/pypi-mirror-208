import time
import customtkinter
import threading
from tkinter.constants import LEFT, NW, TOP
import sys
import subprocess
import pkg_resources

from ipra.View2.main import Main

class BootupCTK():

    required = ['selenium', 'beautifulsoup4', 'webdriver_manager',
                'pandas', 'xlsxwriter', 'openpyxl', 'lxml', 'configparser', 'packaging',
                'Pillow','customtkinter','IPRA']

    currentVersion = []

    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.title("IPRA Update Process")

        # sets the geometry of toplevel
        self.root.geometry("400x200")

        mainLabel = customtkinter.CTkLabel(self.root, text='Check for update...')
        mainLabel.pack(side=TOP, anchor=NW, padx=10, pady=10)

        # New Line
        emptyLable = customtkinter.CTkLabel(self.root, text='')
        emptyLable.pack()

        self.statusText = customtkinter.StringVar()
        self.statusText.set("")

        statusLable = customtkinter.CTkLabel(self.root, textvariable=self.statusText)
        statusLable.pack(side=TOP, anchor=NW, padx=10)

        # New Line
        emptyLable = customtkinter.CTkLabel(self.root, text='')
        emptyLable.pack()

        self.closeButton = customtkinter.CTkButton(self.root, text="START IPRA",command=self.__closeFrame)
        self.closeButton.pack_forget()


        self.updatePackageThread = threading.Thread(target=self.__updatePackage)
        self.updatePackageThread.start()
        #self.__getCurrentPackageVersion()

        self.root.mainloop()

    def __closeFrame(self):
        # Shut down all frame and close all webdriver
        # Important to release all resources
        self.root.quit()
        self.ipra = Main()

    def __getCurrentPackageVersion(self):
        for packageName in self.required:
            self.currentVersion.append(
                pkg_resources.get_distribution(packageName).version)
        return

    def __updatePackage(self):
        for packageName in self.required:
            pass
            # self.statusText.set("Checking for Update: {0}".format(packageName))
            # python = sys.executable
            # subprocess.check_call(
            #     [python, '-m', 'pip', 'install', packageName], stdout=subprocess.DEVNULL)
            # python = sys.executable
            # subprocess.check_call(
            #     [python, '-m', 'pip', 'install', packageName, '--upgrade'], stdout=subprocess.DEVNULL)
        else:
            self.statusText.set("Update Completed! Starting IPRA...")
            self.closeButton.pack(side=TOP, anchor=NW, padx=10)
            # time.sleep(3)
            # self.__closeFrame()
            
updateDialog = BootupCTK()
