import tkinter as tk
import customtkinter
from ipra.Utility.StringUtility import GetStringSingletion
from ipra.Utility.ConfigUtility import GetConfigSingletion

class RunningStatusFrameCTK(customtkinter.CTkFrame):
    STATUS_EXCEPTION = 0
    STATUS_SCRAP_COMPLETE = 1
    STATUS_REPORT_COMPLETE = 2

    
    def __init__(self,masterFrame,col_idx,company):
        super().__init__(masterFrame)
        self.currentCompnany = company
        self.FONT = customtkinter.CTkFont(size=15)
        
        self.grid_propagate(0)
        self.grid(row=0,column=col_idx,sticky='nwes',padx=5, pady=5)
        #row 0 = list box, row 1 = running status
        customtkinter.CTkFrame.rowconfigure(self,0,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,1,weight=15)
        customtkinter.CTkFrame.rowconfigure(self,2,weight=1)
        customtkinter.CTkFrame.rowconfigure(self,3,weight=1)
        customtkinter.CTkFrame.columnconfigure(self,0,weight=1)
        
        #create check box 
        self.defaultCheck = False

        self.stringDisplay = GetStringSingletion()
        try:
            self.config_obj = GetConfigSingletion()
            defaultValue = self.config_obj.ReadConfig('default_download_report',company[0])
            if defaultValue == 'True':
                self.defaultCheck = True
        except Exception as e:
            self.defaultCheck = False
            
            
        self.chkValue = customtkinter.BooleanVar() 
        self.chkValue.set(self.defaultCheck)
        self.chkText = self.stringDisplay.downloadReport.get().format(self.stringDisplay.CompanyFullName(company[0]),font=self.FONT)
        self.chkbox = customtkinter.CTkCheckBox(self, text=self.chkText, variable=self.chkValue ,font=self.FONT) 
        self.chkbox.grid(column=0,row=0,columnspan=2,sticky='we')
        self.chkbox.grid_propagate(False)

        #create list box
        self.listbox = tk.Listbox(self,listvariable=tk.StringVar(value=company),font=self.FONT)
        self.listbox.grid(column=0,row=1,sticky='nwes')

        # link a scrollbar to a list
        scrollbar = customtkinter.CTkScrollbar(
            self,
            orientation='vertical',
            command=self.listbox.yview
        )

        self.listbox['yscrollcommand'] = scrollbar.set

        scrollbar.grid(
            column=1,
            row=1,
            sticky='ns')
        
        #create Progress bar
        self.progressBar = customtkinter.CTkProgressBar(
            self,
            orientation='horizontal',
            mode='determinate',
        )
        # place the progressbar
        self.progressBar.grid(column=0, row=2, columnspan=2, padx=5,pady=5,sticky='we')
        self.progressBar.grid_propagate(False)
        self.progressBar.set(0)

        self.progressValue = 0
        self.policyList = company
        self.policyStatus = [-1] * len(company)

        self.statusLable = customtkinter.CTkLabel(self,text=self.stringDisplay.waitingExe.get(),font=self.FONT)
        self.statusLable.grid(column=0,row=3,columnspan=2,sticky='nwes')
        self.statusLable.grid_propagate(False)

    def setStatusLableText(self,textStringVar):
        self.statusLable.after(10,self.statusLable.configure(text=textStringVar))

    def setStatusProgresValueByValue(self,value):
        # -1 for company name
        self.progressValue = self.progressValue + ( value/ ( (len(self.policyList) - 1) * 2 ) )
        self.progressBar.set(self.progressValue)
        
    def resetProgress(self):
        self.progressBar.set(0)
        self.setStatusLableText(self.stringDisplay.waitingExe.get())
    
    def getDownloadReportIndicator(self):
        return self.chkValue.get()
        
    def setListItemColor(self,policy,status):
        index = self.policyList.index(policy)
        if not self.policyStatus[index] == self.STATUS_EXCEPTION:
            self.policyStatus[index] = status
            if status == self.STATUS_EXCEPTION:
                self.listbox.itemconfig(index, {'bg':'red','fg':'white'})
            elif status == self.STATUS_SCRAP_COMPLETE:
                self.listbox.itemconfig(index, {'bg':'lightblue'})
            else:
                self.listbox.itemconfig(index, {'bg':'lightgreen'})
            pass
        else:
            pass
    
    def setListItemCursor(self,policy):
        index = self.policyList.index(policy)
        self.listbox.selection_set(index)
        pass

    def updateLangauge(self):
        self.chkbox.after(10,
        self.chkbox.config(text=self.stringDisplay.downloadReport.get().format(self.stringDisplay.CompanyFullName(self.currentCompnany[0]))))
    
