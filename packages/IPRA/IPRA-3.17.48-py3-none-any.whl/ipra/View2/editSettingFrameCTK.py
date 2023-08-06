import customtkinter
from ipra.Logger.logger import Logger
from tkinter.constants import DISABLED
from ipra.Utility.StringUtilityCTK import GetStringSingletionCTK
from ipra.Utility.tkinterUtility import *
from ipra.Utility.ConfigUtility import GetConfigSingletion


class EditSettingFrame(customtkinter.CTkFrame):
    def __init__(self,app):
        super().__init__(master=app,corner_radius=0,fg_color="transparent")
        self.FONT = customtkinter.CTkFont(size=15,weight='bold')
        self.logger = Logger()
        self.config_obj = GetConfigSingletion()
        self.stringVar = GetStringSingletionCTK()
        self.stringVar.SetString()


        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(5,weight=1)
        self.grid_columnconfigure(3,weight=1)

        self.logPathLable = customtkinter.CTkLabel(self, text=self.stringVar.logPath.get(), 
                                              font=self.FONT,anchor="w")
        self.logPathLable.grid(row=0, column=0, padx=20, pady=20,sticky="ew")

        self.logPath = customtkinter.StringVar(self,value=self.config_obj.ReadConfig('logger_path','loggerpath'))
        self.logPathTextField = customtkinter.CTkEntry(self,font=("Arial", 15),width=300,textvariable=self.logPath,state=DISABLED)
        self.logPathTextField.grid(row=0, column=1, sticky='nwse',padx=5,pady=5)

        self.setlogPathButton = customtkinter.CTkButton(self,text=self.stringVar.selectPath.get(),command=self.__selectLogDirectory,font=self.FONT)
        self.setlogPathButton.grid(row=0, column=2, sticky='nsew',padx=5, pady=5)


        self.outputPathLable = customtkinter.CTkLabel(self, text=self.stringVar.outputPath.get(), 
                                              font=self.FONT,anchor="w")
        self.outputPathLable.grid(row=1, column=0, padx=20, pady=20,sticky="ew")

        self.outputPath = customtkinter.StringVar(self,value=self.config_obj.ReadConfig('report_path','outputPath'))
        self.outputPathTextField = customtkinter.CTkEntry(self,font=("Arial", 15),width=300,textvariable=self.outputPath,state=DISABLED)
        self.outputPathTextField.grid(row=1, column=1, sticky='nwse',padx=5,pady=5)

        self.setOutputPathButton = customtkinter.CTkButton(self,text=self.stringVar.selectPath.get(),command=self.__selectOutPutDirectory,font=self.FONT)
        self.setOutputPathButton.grid(row=1, column=2, sticky='nsew',padx=5, pady=5)

        self.inputPathLable = customtkinter.CTkLabel(self, text=self.stringVar.inputPath.get(), 
                                              font=self.FONT,anchor="w")
        self.inputPathLable.grid(row=2, column=0, padx=20, pady=20,sticky="ew")

        self.inputPath = customtkinter.StringVar(self,value='')
        self.inputPathTextField = customtkinter.CTkEntry(self,font=("Arial", 15),width=300,textvariable=self.inputPath,state=DISABLED)
        self.inputPathTextField.grid(row=2, column=1, sticky='nwse',padx=5,pady=5)

        self.setInputPathButton = customtkinter.CTkButton(self,text=self.stringVar.selectPath.get(),command=self.__selectInputPutDirectory,font=self.FONT)
        self.setInputPathButton.grid(row=2, column=2, sticky='nsew',padx=5, pady=5)


        #radio Button section for Language selection
        self.languageSelect = customtkinter.IntVar()
        if self.config_obj.ReadConfig('language','display') == 'zh':
            self.languageSelect.set(1)
        else:
            self.languageSelect.set(2)
        
        self.R1 = customtkinter.CTkRadioButton(self, text=self.stringVar.zhHK.get(), variable=self.languageSelect, value=1,font=self.FONT)
        self.R1.grid(column=0,row=3,sticky='nsew',padx=20,pady=20)
        self.R2 = customtkinter.CTkRadioButton(self, text=self.stringVar.english.get(), variable=self.languageSelect, value=2,font=self.FONT)
        self.R2.grid(column=1,row=3,sticky='nsew',padx=20,pady=20)
        #radio Button section for Language selection
        self.languageUpdateLabel = customtkinter.CTkLabel(self, text=self.stringVar.languageUpdate.get(), font=customtkinter.CTkFont(size=13),anchor="w")
        self.languageUpdateLabel.grid(row=4, columnspan = 2 , column=0, padx=20, sticky="ew")







        self.returnButton = customtkinter.CTkButton(self,height=50,text=self.stringVar.saveAndReturn.get(),command=self.__confirmReturn,font=self.FONT)
        self.returnButton.grid(row=6, column=0, sticky='ew',padx=20, pady=20)


    def __selectLogDirectory(self):
        path = selectPath()
        if path == '':
            return
        else:
            self.logPath.set(path+'/')
            self.logger.setLogPath(self.logPath.get())
        return
    
    def __selectOutPutDirectory(self):
        path = selectPath()
        if path == '':
            return
        else:
            self.outputPath.set(path)
        return

    def __selectInputPutDirectory(self):
        path = selectPath()
        if path == '':
            return
        else:
            self.inputPath.set(path+'/')
        return
    
    def __confirmReturn(self):
        self.config_obj.WriteConfig('report_path','outputPath',self.outputPath.get())
        self.config_obj.WriteConfig('report_path','inputPath',self.inputPath.get())
        self.config_obj.WriteConfig('logger_path','loggerpath',self.logPath.get())
        
        if self.languageSelect.get() == 1:
            self.config_obj.WriteConfig('language','display','zh')
        else:
            self.config_obj.WriteConfig('language','display','en')
        
        return