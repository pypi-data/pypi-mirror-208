import subprocess
import sys
import threading
from tkinter import messagebox
import customtkinter
import pkg_resources
import requests

from ConfigUtility import GetConfigSingletion
from StringUtilityCTK import GetStringSingletionCTK

class CheckForUpdateTopLevel(customtkinter.CTkToplevel):

    required = ['selenium', 'beautifulsoup4', 'webdriver_manager',
            'pandas', 'xlsxwriter', 'openpyxl', 'lxml', 'configparser', 'packaging',
            'Pillow','customtkinter',
            'IPRA']

    def __init__(self, xPos,yPos,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_obj = GetConfigSingletion()
        self.stringVar = GetStringSingletionCTK()
        self.geometry(f'+{xPos}+{yPos}')
        self.geometry("400x200")

        customtkinter.CTkFrame.rowconfigure(self,0)
        customtkinter.CTkFrame.columnconfigure(self,0,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,1,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,2,weight=1)


        self.mainLabel = customtkinter.CTkLabel(self, text='檢查中。。。 Check for update... ')
        self.mainLabel.grid(row=0, column=0, pady = 10, padx = 10,sticky="nsew")

        self.statusText = customtkinter.StringVar()
        self.statusText.set("")

        self.statusLable = customtkinter.CTkLabel(self, textvariable=self.statusText)
        self.statusLable.grid(row=1, column=0, pady = 10, padx = 10,sticky="nsew")

        # self.closeButton = customtkinter.CTkButton(self, text="啓動 START IPRA ",command=self.__closeFrame)
        # self.closeButton.grid_forget()

        self.updatePackageThread = threading.Thread(target=self.__checPackageVersion)
        self.updatePackageThread.start()

    pass

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

                self.cancel = tk.Button(self.root, text="稍後更新 Update Later",command=self.__closeFrame)
                self.cancel.pack(side=LEFT, anchor=NW, padx=10)


            # time.sleep(3)
            # self.__closeFrame()
    
    def __onUpdatePackageAndClose(self):
        threading.Thread(target=self.__updatePackage).start()

    def __updatePackage(self):
        self.closeButton.pack_forget()
        self.cancel.pack_forget()

        for packageName in self.doUpdate:
            self.statusText.set("檢查更新中: Checking for Update:       {0}".format(packageName))

            python = sys.executable
            subprocess.check_call(
                [python, '-m', 'pip', 'install', packageName, '--user','--upgrade'], stdout=subprocess.DEVNULL)
    

        result = messagebox.showinfo("更新 Update", "更新完成 Update Completed\n\n請重新啓動 Please restart IPRA")

        pass