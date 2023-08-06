import customtkinter
from ipra.Utility.ConfigUtility import GetConfigSingletion
from ipra.Utility.StringUtilityCTK import *
from tkinter import filedialog, messagebox
from ipra.Controller.reportThreadController import ReportThreadController
from ipra.Controller.robotThreadController import RobotThreadController
from ipra.Controller.policyCollectionController import PolicyCollectionController
from ipra.View2.runningStatusFrameCTK import RunningStatusFrameCTK

class PolicyRobotFrame(customtkinter.CTkFrame):
    def __init__(self,app):
        super().__init__(master=app,corner_radius=0, fg_color="transparent")
        self.FONT = customtkinter.CTkFont(size=17,weight="bold")
        self.frame_instances_running_state = []
        self.configParser = GetConfigSingletion()
        self.stringValue = GetStringSingletionCTK()
        self.stringValue.SetString()
        self.policyController = PolicyCollectionController()
        self.robotThreadController = RobotThreadController()
        self.reportThreadController = ReportThreadController()

        self.grid_columnconfigure(0, weight=1)
        customtkinter.CTkFrame.rowconfigure(self,0,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,1,weight=10)
        customtkinter.CTkFrame.rowconfigure(self,2,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,0,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,1,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,2,weight=1)

        #Open excel, work sheet etc. prepare all the policy no.
        self.frame_open_excel = customtkinter.CTkButton(master=self,text=self.stringValue.importPolicy.get(),font=self.FONT,command=self.__openStandardFile)
        self.frame_open_excel.grid(row=0,column=0,columnspan=3,sticky='nsew',padx=5, pady=5)
        self.frame_open_excel.grid_propagate(0)

        #Display Policy no. and running status
        self.frame_running_state = customtkinter.CTkFrame(master=self)
        self.frame_running_state.grid(row=1,column=0,columnspan=3,sticky='nsew',padx=5)
        self.frame_running_state.grid_propagate(0)
        
        #start/clean running state
        self.button_reset = customtkinter.CTkButton(master=self,text=self.stringValue.clear.get(),command = self.__cleanFrameRunningState,font=self.FONT)
        self.button_reset.grid(row=2,column=0,sticky='nsew',padx=5, pady=5)
        self.button_reset.grid_propagate(0)

        self.button_start = customtkinter.CTkButton(master=self,text=self.stringValue.startRobot.get(),command=self.__startRobot,font=self.FONT)
        self.button_start.grid(row=2,column=1,sticky='nsew',padx=5, pady=5)
        self.button_start.grid_propagate(0)

        self.button_reset = customtkinter.CTkButton(master=self,text=self.stringValue.exportReport.get(),command=self.__buildReport,font=self.FONT)
        self.button_reset.grid(row=2,column=2,sticky='nsew',padx=5, pady=5)
        self.button_reset.grid_propagate(0)

        pass

    def __openStandardFile(self):
        filePath = filedialog.askopenfilename()
        if filePath != None and filePath != '':
            readResult = self.policyController.getPolicyListFromFile(filePath)
            if readResult:
                self.__displaySearchPolicy()
            else:
                messagebox.showerror(self.stringValue.importError.get(), self.stringValue.formatError.get())
        return

    def __startRobot(self):
        self.robotThreadController.createRobotThread(self.policyController.getPolicyCollection(),self.frame_instances_running_state)

    def __buildReport(self):
        self.reportThreadController.createReportThread(self.policyController.getPolicyCollection(),self.frame_instances_running_state)
    
    def __cleanFrameRunningState(self):
        #Clean and reset
        
        for frame in self.frame_instances_running_state:
            if frame != None:
                frame.destroy()
        #self.frame_running_state.destory()
        self.__resetFrameRunningState()
        self.frame_instances_running_state = []
        self.policyController.cleanAllPolicy()

    def __resetFrameRunningState(self):
        self.frame_running_state = customtkinter.CTkFrame(master=self)
        self.frame_running_state.grid(row=1,column=0,columnspan=3,sticky='nsew',padx=5)
        self.frame_running_state.grid_propagate(0)

    def __displaySearchPolicy(self):
        column_idx = 0
        self.frame_running_state.rowconfigure(0,weight=10)
        for company in self.policyController.getPolicyCollection():
            if(len(company)>1):
                self.frame_running_state.columnconfigure(column_idx,weight=1)
                frameTemp = RunningStatusFrameCTK(self.frame_running_state,column_idx,company)
                column_idx = column_idx + 1
                self.frame_instances_running_state.append(frameTemp)
            else:
                self.frame_instances_running_state.append(None)