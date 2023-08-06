import configparser
import os

class _ConfigSingleton:
    _configInstance = None
    _defaultINIPath = "C:\IPRA\config.ini"
    _defaultDirectory = "C:\IPRA"
    _defaultLog = 'C:/IPRA/LOG/'
    _defaultReport = 'C:/IPRA/REPORT'
    _defaultResouce = 'C:/IPRA/RESOURCE/'


    def __init__(self) -> None:
        self.config_obj = configparser.ConfigParser()
        configParam = self.config_obj.read(self._defaultINIPath)

        if len(configParam) == 0:
            #no config found,write default
            self.WriteDefault()
            pass
        else:
            self.CheckAndWriteDefault()

        pass


    def IsConfigExist(self,section,key):
        if not self.config_obj.has_section(section):
            return False
        else:
            if self.config_obj.has_option(section,key):
                return True
            else:
                return False
    
    def ReadConfig(self,section,key):
        #call IsConfigExist before
        return self.config_obj[section][key]
    
    def WriteConfig(self,section,key,value):
        if not self.config_obj.has_section(section):
            self.config_obj.add_section(section)

        self.config_obj.set(section=section,option=key,value=value)

        if not os.path.exists(self._defaultINIPath):
            os.makedirs(self._defaultDirectory,0o777)

        if not os.path.exists(self._defaultResouce):
            os.makedirs(self._defaultResouce,0o777)

        with open(self._defaultINIPath, 'w') as configfile:
            self.config_obj.write(configfile)
    
    def WriteDefault(self):
        self.WriteConfig('report_path','outputpath',self._defaultReport)
        self.WriteConfig('report_path','inputpath',self._defaultReport)
        self.WriteConfig('resource_path','resourcepath',self._defaultResouce)
        self.WriteConfig('logger_path','loggerpath',self._defaultLog)
        self.WriteConfig('default_download_report','default','False')
        self.WriteConfig('language','display','zh')
        self.WriteConfig('insurer','pru_agent_cd','0')
        self.WriteConfig('insurer','pru_user_id','0')

    def CheckAndWriteDefault(self):
        if not self.IsConfigExist('report_path','outputpath'):
            self.WriteConfig('report_path','outputpath',self._defaultReport)

        if not self.IsConfigExist('report_path','inputpath'):
            self.WriteConfig('report_path','inputpath',self._defaultReport)

        if not self.IsConfigExist('resource_path','resourcepath'):
            self.WriteConfig('resourcepath','resourcepath',self._defaultResouce)

        if not self.IsConfigExist('logger_path','loggerpath'):
            self.WriteConfig('logger_path','loggerpath',self._defaultLog)

        if not self.IsConfigExist('default_download_report','default'):
            self.WriteConfig('default_download_report','default','False')

        if not self.IsConfigExist('language','display'):
            self.WriteConfig('language','display','zh')

        if not self.IsConfigExist('insurer','pru_agent_cd'):
            self.WriteConfig('insurer','pru_agent_cd','0')
            
        if not self.IsConfigExist('insurer','pru_user_id'):
            self.WriteConfig('insurer','pru_user_id','0')

def GetConfigSingletion():
    if _ConfigSingleton._configInstance is None:
        _ConfigSingleton._configInstance = _ConfigSingleton()
    return _ConfigSingleton._configInstance