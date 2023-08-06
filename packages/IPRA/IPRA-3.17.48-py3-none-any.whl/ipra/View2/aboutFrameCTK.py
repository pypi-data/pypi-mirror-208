import subprocess
import sys
import threading
import customtkinter
import pkg_resources
import requests
from ipra.Utility.StringUtilityCTK import GetStringSingletionCTK
from ipra.Utility.ConfigUtility import GetConfigSingletion
from ipra.Controller.policyCollectionController import PolicyCollectionController


class AboutFrame(customtkinter.CTkFrame):
    __VERSION = pkg_resources.require("ipra")[0].version
    __DATE = "18-May-2023"
    __CHECKSUM = "434CB5763271834B"
    required = ['selenium', 'beautifulsoup4', 'webdriver_manager',
        'pandas', 'xlsxwriter', 'openpyxl', 'lxml', 'configparser', 'packaging',
        'Pillow','customtkinter',"EmailNotice",
        'IPRA',]
    
    __isCheckingUpdate = False

    
    def __init__(self,app):
        super().__init__(master=app,corner_radius=0,fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        customtkinter.CTkFrame.rowconfigure(self,0,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,1,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,2,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,3,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,4,weight=10)
        customtkinter.CTkFrame.rowconfigure(self,5,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,0,weight=1,uniform="fred")
        customtkinter.CTkFrame.columnconfigure(self,1,weight=1,uniform="fred")

        self.FONT = customtkinter.CTkFont(size=15,weight='bold')
        self.configParser = GetConfigSingletion()
        self.stringValue = GetStringSingletionCTK()
        self.stringValue.SetString()

        self.version = customtkinter.CTkLabel(self, text= self.stringValue.versionString.get().format(self.__VERSION), font=self.FONT)
        self.version.grid(row=0, column=0, padx=20, pady = (10,0), sticky="nw")

        self.date = customtkinter.CTkLabel(self, text= self.stringValue.releaseDate.get().format(self.__DATE), font=self.FONT)
        self.date.grid(row=1, column=0, padx=20, sticky="nw")

        self.checksum = customtkinter.CTkLabel(self, text= self.stringValue.checksum.get().format(self.__CHECKSUM), font=self.FONT)
        self.checksum.grid(row=2, column=0, padx=20, sticky="nw")

        self.supportSystem = customtkinter.CTkLabel(self, text= self.stringValue.supportSystem.get(), font=self.FONT)
        self.supportSystem.grid(row=3, column=0, padx=20, sticky="nw")

        self.textbox = customtkinter.CTkTextbox(self, width=200,font=self.FONT)
        self.textbox.grid(row=4, column=0, padx=20, pady=(0,10),sticky="nsw")

        for entry in PolicyCollectionController().getPolicyCollection():
            self.textbox.insert('end', entry[0]+'\n')
        self.textbox.configure(state='disabled')

        self.checkForUpdate = customtkinter.CTkButton(self,height=50,text=self.stringValue.checkForUpdate.get(),command=self.__ProcessUpdate,font=self.FONT)
        self.checkForUpdate.grid(row=5, column=0, sticky='ew',padx=20, pady=20)

        self.updateStatus = customtkinter.StringVar()

        self.updateStatusLabel = customtkinter.CTkLabel(self, textvariable=self.updateStatus, font=self.FONT)
        self.updateStatusLabel.grid(row=5, column=1, padx=20,pady=20,sticky="nsw")
        pass


    def __ProcessUpdate(self):
        threading.Thread(target=self.__UpdatePackage).start()


    def __UpdatePackage(self):
        if self.__isCheckingUpdate == False:
            self.__isCheckingUpdate = True
            self.updateStatus.set("")
            isUpdateApplied = False

            for packageName in self.required:

                self.updateStatus.set(self.stringValue.checkPackage.get().format(packageName))

                try:
                    version = pkg_resources.get_distribution(packageName)

                    response = requests.get("https://pypi.org/pypi/{0}/json".format(packageName))

                    verionDetails = response.json()

                    if version.version != verionDetails['info']['version']:
                        isUpdateApplied = True
                        # python = sys.executable
                        # subprocess.check_call(
                        #     [python, '-m', 'pip', 'install', packageName, '--user','--upgrade'], stdout=subprocess.DEVNULL)


                except pkg_resources.DistributionNotFound as ex:
                    isUpdateApplied = True
                    # python = sys.executable
                    # subprocess.check_call([python, '-m', 'pip', 'install', packageName, '--user','--upgrade'], stdout=subprocess.DEVNULL)

                # python = sys.executable
                # subprocess.check_call(
                #     [python, '-m', 'pip', 'install', packageName, '--user'], stdout=subprocess.DEVNULL)
                # python = sys.executable
                # subprocess.check_call(
                #     [python, '-m', 'pip', 'install', packageName, '--user','--upgrade'], stdout=subprocess.DEVNULL)
            else:
                if isUpdateApplied:
                    self.updateStatus.set(self.stringValue.updateCompleted.get())
                else:
                    self.updateStatus.set(self.stringValue.noUpdate.get())
            
            self.__isCheckingUpdate = False
        else:
            return