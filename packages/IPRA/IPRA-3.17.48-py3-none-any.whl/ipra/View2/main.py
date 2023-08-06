import customtkinter
from ipra.Utility.StringUtilityCTK import GetStringSingletionCTK
from ipra.Utility.ConfigUtility import GetConfigSingletion

from ipra.Logger.logger import Logger
from ipra.View2.aboutFrameCTK import AboutFrame
from ipra.View2.editSettingFrameCTK import EditSettingFrame
from ipra.View2.policyRobotFrame import PolicyRobotFrame
from ipra.View2.sliderMenu import SliderMenu
from era.View.main_view import MainView as EmailSystem
import pkg_resources  # part of setuptools

class Main():
    __VERSION = pkg_resources.require("ipra")[0].version

    app =  None
    logger = None
    configParser = None
    stringValue = None
    sliderMenu = None
    policyRobot = None
    setting = None
    about = None
    

    def __init__(self):
        customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        self.app = customtkinter.CTk()
        self.app.title("IPRA v{0}".format(self.__VERSION))
        self.app.geometry("1200x1000")
        self.app.protocol("WM_DELETE_WINDOW", self.__closeMainFrame)
        # set grid layout 1x2
        self.app.grid_rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(1, weight=1)
        
        self.configParser = GetConfigSingletion()
        self.logger = Logger()
        self.stringValue = GetStringSingletionCTK()


        self.sliderMenu = SliderMenu(self.app,self.select_frame_by_name)
        self.policyRobotFrame = PolicyRobotFrame(self.app)
        self.aboutFrame = AboutFrame(self.app)
        self.editSettingFrame = EditSettingFrame(self.app)
        self.emailSystemFrame = EmailSystem(self.app)
        
        self.select_frame_by_name("Home")

        self.app.mainloop()
        pass
    
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def select_frame_by_name(self, name):
        # show selected frame
        if name == "Home":
            self.policyRobotFrame.grid(row=0, column=1, sticky="nsew")
        else:
            self.policyRobotFrame.grid_forget()
        
        
        if name == "Setting":
            self.editSettingFrame.grid(row=0, column=1, sticky="nsew")
        else:
            self.editSettingFrame.grid_forget()
        

        if name == "About":
            self.aboutFrame.grid(row=0, column=1, sticky="nsew")
        else:
            self.aboutFrame.grid_forget()


        if name == "Email":
            self.emailSystemFrame.grid(row=0, column=1, sticky="nsew")
        else:
            self.emailSystemFrame.grid_forget()

        
    
    def __closeMainFrame(self):
        #Shut down all frame and close all webdriver
        #Important to release all resources
        self.policyRobotFrame.robotThreadController.destoryAllRobotThread()
        self.app.destroy()