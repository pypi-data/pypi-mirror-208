import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.constants import NW, TOP,LEFT
import pkg_resources
import requests
class UpdateProcessDialog():

    required = ['selenium', 'beautifulsoup4', 'webdriver_manager',
                'pandas', 'xlsxwriter', 'openpyxl', 'lxml', 'configparser', 'packaging',
                'Pillow','customtkinter',"EmailNotice",
                'IPRA']

    doUpdate = []

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IPRA Update Process")

        # sets the geometry of toplevel
        self.root.geometry("400x200")

        mainLabel = tk.Label(self.root, text='檢查中。。。 Check for update... ')
        mainLabel.pack(side=TOP, anchor=NW, padx=10, pady=10)

        # New Line
        emptyLable = tk.Label(self.root, text='')
        emptyLable.pack()

        self.statusText = tk.StringVar()
        self.statusText.set("")

        statusLable = tk.Label(self.root, textvariable=self.statusText)
        statusLable.pack(side=TOP, anchor=NW, padx=10)

        # New Line
        emptyLable = tk.Label(self.root, text='')
        emptyLable.pack()

        self.closeButton = tk.Button(self.root, text="啓動 START IPRA ",command=self.__closeFrame)
        self.closeButton.pack_forget()


        self.updatePackageThread = threading.Thread(target=self.__checPackageVersion)
        self.updatePackageThread.start()
        #self.__getCurrentPackageVersion()
        self.root.mainloop()
        
    def __closeFrame(self):
        # Shut down all frame and close all webdriver
        # Important to release all resources
        self.root.destroy()
        from ipra.View2.main import Main
        Main()

    def __checPackageVersion(self):

        self.doUpdate = []

        for packageName in self.required:

            self.statusText.set("檢查更新中: Checking for Update:       {0}".format(packageName))

            try:
                version = pkg_resources.get_distribution(packageName)

                response = requests.get("https://pypi.org/pypi/{0}/json".format(packageName))

                verionDetails = response.json()

                if version.version != verionDetails['info']['version']:
                    self.doUpdate.append(packageName)

            except pkg_resources.DistributionNotFound as ex:
                python = sys.executable
                subprocess.check_call([python, '-m', 'pip', 'install', packageName, '--user'], stdout=subprocess.DEVNULL)

            # python = sys.executable
            # subprocess.check_call(
            #     [python, '-m', 'pip', 'install', packageName, '--user'], stdout=subprocess.DEVNULL)
            # python = sys.executable
            # subprocess.check_call(
            #     [python, '-m', 'pip', 'install', packageName, '--user','--upgrade'], stdout=subprocess.DEVNULL)
        else:
            if len(self.doUpdate) == 0:
                self.statusText.set("没有可用的更新 There are no updates available")
                self.closeButton.pack(side=TOP, anchor=NW, padx=10)
            else:
                self.statusText.set("有可用的更新 Updates Available")
                self.closeButton.config(text='現在更新 Update Now',command=self.__onUpdatePackageAndClose)
                self.closeButton.pack(side=LEFT, anchor=NW, padx=10)

                # self.cancel = tk.Button(self.root, text="稍後更新 Update Later",command=self.__closeFrame)
                # self.cancel.pack(side=LEFT, anchor=NW, padx=10)


            # time.sleep(3)
            # self.__closeFrame()
    
    def __onUpdatePackageAndClose(self):
        self.root.after(50,self.__updatePackage)

    def __updatePackage(self):
        self.closeButton.pack_forget()
        #self.cancel.pack_forget()

        for packageName in self.doUpdate:
            self.statusText.set("檢查更新中: Checking for Update:       {0}".format(packageName))

            python = sys.executable
            subprocess.check_call([python, '-m', 'pip', 'install', packageName, '--user','--upgrade'], stdout=subprocess.DEVNULL)
    

        result = messagebox.showinfo("更新 Update", "更新完成 Update Completed\n\n請重新啓動 Please restart IPRA")

        self.root.destroy()
    
        pass