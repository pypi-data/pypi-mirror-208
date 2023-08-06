import customtkinter
import pkg_resources
from ipra.Utility.StringUtilityCTK import GetStringSingletionCTK
from ipra.Utility.ConfigUtility import GetConfigSingletion
from PIL import Image
from pkg_resources import resource_stream

class SliderMenu(customtkinter.CTkFrame):
    def __init__(self,app,selectFrameCallback):
        super().__init__(master=app,corner_radius=0)

        self.FONT = customtkinter.CTkFont(size=17)
        self.configParser = GetConfigSingletion()
        self.stringValue = GetStringSingletionCTK()
        self.stringValue.SetString()
        self.callback = selectFrameCallback
        
        # create navigation frame
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

        self.home_image = customtkinter.CTkImage(light_image=Image.open(resource_stream('ipra', 'Assets/reports-icon.png')),
                                            dark_image=Image.open(resource_stream('ipra', 'Assets/reports-icon.png')), size=(35, 35))

        self.setting_image = customtkinter.CTkImage(light_image=Image.open(resource_stream('ipra', 'Assets/setting-icon.png')),
                                            dark_image=Image.open(resource_stream('ipra', 'Assets/setting-icon.png')), size=(35, 35))

        self.about_image = customtkinter.CTkImage(light_image=Image.open(resource_stream('ipra', 'Assets/about-icon.png')),
                                            dark_image=Image.open(resource_stream('ipra', 'Assets/about-icon.png')), size=(35, 35))
        
        self.email_image = customtkinter.CTkImage(light_image=Image.open(resource_stream('ipra', 'Assets/email-icon.png')),
                                            dark_image=Image.open(resource_stream('ipra', 'Assets/email-icon.png')), size=(35, 35))


        self.navigation_frame_label = customtkinter.CTkLabel(self, text=self.GetPackageVersion(),compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=self.stringValue.sliderMenuRobot.get(),
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.home_button_event,font=self.FONT,image=self.home_image)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.email_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=self.stringValue.emailSystem.get(),
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.email_button_event,font=self.FONT,image=self.email_image)
        self.email_button.grid(row=2, column=0, sticky="ew")

        self.setting_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=self.stringValue.setting.get(),
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.setting_button_event,font=self.FONT,image=self.setting_image)
        self.setting_button.grid(row=5, column=0, sticky="ew")

        self.about_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=self.stringValue.about.get(),
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.about_button_event,font=self.FONT,image=self.about_image)
        self.about_button.grid(row=6, column=0, sticky="ew")


        
        self.home_button.configure(fg_color=("gray75", "gray25"))
        pass

    def home_button_event(self):
        self.home_button.configure(fg_color=("gray75", "gray25"))
        self.setting_button.configure(fg_color="transparent")
        self.about_button.configure(fg_color="transparent")
        self.callback("Home")

    def setting_button_event(self):
        self.home_button.configure(fg_color="transparent")
        self.setting_button.configure(fg_color=("gray75", "gray25"))
        self.about_button.configure(fg_color="transparent")
        self.callback("Setting")

    def about_button_event(self):
        self.home_button.configure(fg_color="transparent")
        self.setting_button.configure(fg_color="transparent")
        self.about_button.configure(fg_color=("gray75", "gray25"))
        self.callback("About")

    def email_button_event(self):
        self.home_button.configure(fg_color="transparent")
        self.setting_button.configure(fg_color="transparent")
        self.about_button.configure(fg_color=("gray75", "gray25"))
        self.callback("Email")


    def GetPackageVersion(self):
        versionString = "IPRA  "+pkg_resources.require("ipra")[0].version

        try:
            version = pkg_resources.get_distribution("EmailNotice")
            versionString += "\n" + "EMail " + version.version
        except pkg_resources.DistributionNotFound as ex:
            pass


        return versionString
    