from ipra.Logger.logger import Logger
import customtkinter
from ipra.Utility.ConfigUtility import GetConfigSingletion
from ipra.Utility.StringUtility import *
from ipra.Controller.reportThreadController import ReportThreadController
from ipra.Controller.robotThreadController import RobotThreadController
from ipra.Controller.policyCollectionController import PolicyCollectionController
from tkinter import filedialog, messagebox

from ipra.View2.runningStatusFrameCTK import RunningStatusFrameCTK

class MainApplication2():
    frame_running_state = None
    frame_instances_running_state = []
    __VERSION = "1.14.41"
    __DATE = "21-JAN-2023"
    __CHECKSUM = "14BE1B5B60213FFD"

    supportSystem = None
    button_standard = None
    button_manual = None
    button_reset = None
    button_start = None
    button_report = None
    main_app = None

    def __init__(self) -> None:

        self.__CreateWindow()
        self.logger = Logger()
        self.configParser = GetConfigSingletion()
        self.stringValue = GetStringSingletion()
        self.policyController = PolicyCollectionController()
        self.robotThreadController = RobotThreadController()
        self.reportThreadController = ReportThreadController()
        self.__CreateMainUI()
        self.app.mainloop()
        pass

    def __CreateWindow(self):
        customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        self.app = customtkinter.CTk()
        self.app.title("IPRA v{0}".format(self.__VERSION))
        self.app.geometry("800x700")

        # set grid layout 1x2
        self.app.grid_rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)


    def __CreateMainUI(self):

        self.__CreateSideMenu()
        self.__CreateHomeUI()
        self.__CreateSettingUI()
        self.__CreateAboutUI()

        # select default frame
        self.select_frame_by_name("Home")

    def __CreateSideMenu(self):
        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self.app, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)


        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="Image Example",compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.setting_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Setting",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.setting_button_event)
        self.setting_button.grid(row=2, column=0, sticky="ew")

        self.about_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="About",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.about_button_event)
        self.about_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")


    def __CreateHomeUI(self):
        self.home_frame = customtkinter.CTkFrame(self.app, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(master=self.home_frame)
        self.main_frame.pack(side="top", fill="both", expand=True)
        self.app.protocol("WM_DELETE_WINDOW", self.__closeMainFrame)
        customtkinter.CTkFrame.rowconfigure(self.main_frame,0,weight=1)
        customtkinter.CTkFrame.rowconfigure(self.main_frame,1,weight=10)
        customtkinter.CTkFrame.rowconfigure(self.main_frame,2,weight=1)
        customtkinter.CTkFrame.columnconfigure(self.main_frame,0,weight=1)
        customtkinter.CTkFrame.columnconfigure(self.main_frame,1,weight=1)
        customtkinter.CTkFrame.columnconfigure(self.main_frame,2,weight=1)

        #Open excel, work sheet etc. prepare all the policy no.
        frame_open_excel = customtkinter.CTkButton(master=self.main_frame,text=self.stringValue.importPolicy.get(),font=customtkinter.CTkFont(size=15),command=self.__openStandardFile)
        frame_open_excel.grid(row=0,column=0,columnspan=3,sticky='nsew',padx=5, pady=5)
        frame_open_excel.grid_propagate(0)

        #Display Policy no. and running status
        self.frame_running_state = customtkinter.CTkFrame(master=self.main_frame)
        self.frame_running_state.grid(row=1,column=0,columnspan=3,sticky='nsew',padx=5)
        self.frame_running_state.grid_propagate(0)
        
        #start/clean running state
        self.button_reset = customtkinter.CTkButton(master=self.main_frame,text=self.stringValue.clear.get(),command = self.__cleanFrameRunningState)
        self.button_reset.grid(row=2,column=0,sticky='nsew',padx=5, pady=5)
        self.button_reset.grid_propagate(0)

        self.button_start = customtkinter.CTkButton(master=self.main_frame,text=self.stringValue.startRobot.get(),command=self.__startRobot)
        self.button_start.grid(row=2,column=1,sticky='nsew',padx=5, pady=5)
        self.button_start.grid_propagate(0)

        self.button_reset = customtkinter.CTkButton(master=self.main_frame,text=self.stringValue.exportReport.get(),command=self.__buildReport)
        self.button_reset.grid(row=2,column=2,sticky='nsew',padx=5, pady=5)
        self.button_reset.grid_propagate(0)


    def __CreateSettingUI(self):
        # create second frame
        self.setting_frame = customtkinter.CTkFrame(self.app, corner_radius=0, fg_color="transparent")
        self.setting_frame.grid_columnconfigure(0, weight=1)
        pass


    def __CreateAboutUI(self):
        # create third frame
        self.about_frame = customtkinter.CTkFrame(self.app, corner_radius=0, fg_color="transparent")
        self.about_frame.grid_columnconfigure(0, weight=1)
        pass


    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Home" else "transparent")
        self.setting_frame.configure(fg_color=("gray75", "gray25") if name == "Setting" else "transparent")
        self.about_frame.configure(fg_color=("gray75", "gray25") if name == "About" else "transparent")

        # show selected frame
        if name == "Home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "Setting":
            self.setting_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.setting_frame.grid_forget()

        if name == "About":
            self.about_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.about_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("Home")

    def setting_button_event(self):
        self.select_frame_by_name("Setting")

    def about_button_event(self):
        self.select_frame_by_name("About")

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
        self.frame_running_state = customtkinter.CTkFrame(master=self.main_frame)
        self.frame_running_state.grid(row=1,column=0,sticky='nsew')
        self.frame_running_state.grid_propagate(0)        


    def __startRobot(self):
        self.robotThreadController.createRobotThread(self.policyController.getPolicyCollection(),self.frame_instances_running_state)

    def __buildReport(self):
        self.reportThreadController.createReportThread(self.policyController.getPolicyCollection(),self.frame_instances_running_state)

    def __closeMainFrame(self):
        #Shut down all frame and close all webdriver
        #Important to release all resources
        self.robotThreadController.destoryAllRobotThread()
        self.app.destroy()
        return

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def __openStandardFile(self):
        filePath = filedialog.askopenfilename()
        if filePath != None and filePath != '':
            readResult = self.policyController.getPolicyListFromFile(filePath)
            if readResult:
                self.__displaySearchPolicy()
            else:
                messagebox.showerror(self.stringValue.importError.get(), self.stringValue.formatError.get())
        return
    
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

main = MainApplication2()