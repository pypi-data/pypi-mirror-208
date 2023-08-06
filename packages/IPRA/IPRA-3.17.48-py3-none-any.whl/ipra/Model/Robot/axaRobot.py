from selenium.webdriver.common.keys import Keys
from ipra.Model.Robot.baseRobot import BaseRobot
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import xlsxwriter
import threading
from genericpath import exists

class AxaRobot(BaseRobot):

    def __init__(self, policyList, frame, reportPath,inputPath,downloadReport):
        super().__init__(policyList, frame, reportPath,inputPath,downloadReport)
        self.logger.writeLogString('AXA-INIT','ROBOT INIT')
        self.maxPolicyListSize = len(policyList)
        self.workbook = xlsxwriter.Workbook(self.reportPath+'AXA_report.xlsx')

        self.worksheet = self.workbook.add_worksheet(name="Details")
        self.worksheet.write(0, 0, "Policy No.")

        self.ownerSheet = self.workbook.add_worksheet(name="Owner")
        self.ownerSheet.write(0, 0, "Policy No.")

        self.benefitSheet = self.workbook.add_worksheet(name="Benefit")
        self.benefitSheet.write(0, 0, "Policy No.")

        self.planSheet = self.workbook.add_worksheet(name="Plan")
        self.planSheet.write(0, 0, "Policy No.")

        self.logger.writeLogString('AXA-INIT','maxPolicyListSize:'+str(self.maxPolicyListSize))

    def waitingLoginComplete(self):
        self.logger.writeLogString('AXA-LOGIN','START LOGIN')
        self.browser.get("https://www.axa.com.hk/zh/login#?Tab$login-tab=consultant-login")
        self.browser.find_element(By.XPATH,"/html/body/div/div/div[2]/div[3]/div/div/div[1]/div[2]/div[3]/div/div/div/div[2]/div/div[5]/div/div/button").click()
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])
        self.frame.setStatusLableText(self.stringValue.waitingLogin.get())

        while not self.isLogin and not self.isStopped:
            try:
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/div[3]/div[4]/div/div[1]/div/div[1]")))
                while True:
                    try:
                        self.browser.find_element(By.XPATH,"/html/body/div[3]/div[1]/div/div/div/div[3]/div[4]/div/div[1]/div/div[1]")
                        time.sleep(0.1)
                        break
                    except:
                        time.sleep(0.3)
                self.isLogin=True  
            except:
                time.sleep(3)
        else:
            time.sleep(3)

        if self.isLogin:
            self.frame.setStatusLableText(self.stringValue.loginSuccess.get())
            self.logger.writeLogString('AXA-LOGIN','LOGIN COMPLETED')

    def scrapPolicy(self):
        for policy in self.policyList:
            if self.isStopped:
                return
            
            self.frame.setStatusLableText(self.stringValue.processing.get().format(str(policy)))
            self.logger.writeLogString('AXA','PROCESSING:'+str(policy))
            while True:
                    try:
                        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/div[3]/div[4]/div/div[1]/div/div[1]")))
                        self.browser.find_element(By.XPATH,"/html/body/div[3]/div[1]/div/div/div/div[3]/div[4]/div/div[1]/div/div[1]").click()
                        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/div[3]/div[4]/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/input")))
                        input = self.browser.find_element(By.XPATH,"/html/body/div[3]/div[1]/div/div/div/div[3]/div[4]/div/div[1]/div/div[2]/div/div/div/div/div[1]/div/input")
                        input.clear()
                        input.send_keys(str(policy))
                        time.sleep(2)
                        input.send_keys(Keys.ENTER)
                        break
                    except:
                        time.sleep(0.3)
            try:
                WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.LINK_TEXT, str(policy))))
                while True:
                    try:
                        self.browser.find_element(By.LINK_TEXT,str(policy)).click()
                        break
                    except:
                        time.sleep(0.1)

                WebDriverWait(self.browser, 3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[3]/div/div/div/div/div[3]/div/div/div[2]/div/div/ul/li[2]/a/span[2]")))
                while True:
                    try:
                        self.browser.find_element(By.XPATH,"/html/body/div[3]/div[3]/div/div/div/div/div[3]/div/div/div[2]/div/div/ul/li[2]/a/span[2]").click()
                        break
                    except:
                        time.sleep(0.1)
                time.sleep(2)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(self.reportPath+policy+"_details.txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()

                WebDriverWait(self.browser, 3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[3]/div/div/div/div/div[3]/div/div/div[2]/div/div/ul/li[4]/a/span[2]")))
                while True:
                    try:
                        self.browser.find_element(By.XPATH,"/html/body/div[3]/div[3]/div/div/div/div/div[3]/div/div/div[2]/div/div/ul/li[4]/a/span[2]").click()
                        break
                    except:
                        time.sleep(0.1)

                time.sleep(2)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(self.reportPath+policy+"_benefit.txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                

                WebDriverWait(self.browser, 3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[3]/div/div/div/div/div[3]/div/div/div[2]/div/div/ul/li[5]/a/span[2]")))
                while True:
                    try:
                        self.browser.find_element(By.XPATH,"/html/body/div[3]/div[3]/div/div/div/div/div[3]/div/div/div[2]/div/div/ul/li[5]/a/span[2]").click()
                        break
                    except:
                        time.sleep(0.1)
                time.sleep(2)
                soup = BeautifulSoup(self.browser.page_source, 'lxml')
                file1 = open(self.reportPath+policy+"_plan.txt","a",encoding="utf-8")#append mode 
                file1.write(soup.prettify()) 
                file1.close()
                
                # self.downloadPolicyReport(str(policy))
                #self.browser.back()

            except Exception as ex:
                self.frame.setStatusLableText(self.stringValue.processException.get().format(str(policy),str(ex)))
                self.logger.writeLogString('AXA',str(policy)+" throws Exception:" + str(ex))
                self.frame.setListItemColor(str(policy),self.STATUS_EXCEPTION)
            finally:
                self.frame.setStatusLableText(self.stringValue.processCompleted.get().format(str(policy)))
                self.logger.writeLogString('AXA',str(policy)+" COMPLETED")
                self.frame.setStatusProgresValueByValue(1)

                self.buildReportQueue.append(policy)
                self.buildHeaderQueue.append(policy)
                self.frame.setListItemColor(str(policy),self.STATUS_SCRAP_COMPLETE)

    def buildReport(self):
        self.buildReportThread = threading.Thread(target = self.__buildReport)
        self.buildReportThread.start()
        self.buildReportHeaderFullFlow()
        pass

    def buildReportOnly(self):
        self.buildReportThread = threading.Thread(target = self.__buildReportOnly)
        self.buildReportThread.start()
        self.buildReportHeaderHalfFlow()
        pass

    def buildReportHeaderFullFlow(self):
        self.buildHeaderThread = threading.Thread(target = self.__buildReportHeaderFullFlow)
        self.buildHeaderThread.start()
        pass
    
    def buildReportHeaderHalfFlow(self):
        self.buildHeaderThread = threading.Thread(target = self.__buildReportHeaderHalfFlow)
        self.buildHeaderThread.start()
        pass
 
    def downloadPolicyReport(self, policy):
        if not self.downloadReport:
            return
        
        try:
            self.browser.find_element(By.XPATH,"/html/body/div/div[2]/table/tbody/tr/td[2]/div[1]/div[1]/div[2]/a").click()
            self.browser.switch_to.window(self.browser.window_handles[2])
            self.browser.find_element(By.XPATH,"/html/body/div/div[1]/div[1]/ul/li[2]/a").click()
            
            #Selenium no build-in check download complete listerner, check by file exist in path
            reportFullPath = self.reportPath+"{0} _ AXA iPro Office.pdf".format(policy)
            while exists(reportFullPath) == False:
                time.sleep(1)
            
            self.browser.find_element(By.XPATH,"/html/body/div/div[1]/div[1]/ul/li[1]/a").click()
            self.browser.switch_to.window(self.browser.window_handles[1])
        except Exception as ex:
            pass
        
    def __buildReportHeaderFullFlow(self):
        self.logger.writeLogString('AXA-HEADER','START BUILD HEADER FULLFLOW')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildHeaderQueue:
                self.logger.writeLogString('AXA-HEADER','POLICY NO.:{0}'.format(str(policy)))
                if self.isStopped:
                    return
                try:
                    
                    file = open(self.reportPath+policy+"_details.txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    #find the body first
                    soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')
                    
                    soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','2 js-tab tabs__content active uiTab')

                    soup_data = soup_section.find_all('div',attrs={'class':'ui-widget'})

                    soup_data1 = soup_data[0]

                    soup_data1 = soup_data1.find('div',attrs={'class':'test-id__section-content slds-section__content section__content'}) 

                    for col_num, strong_tag in enumerate(soup_data1.find_all('span',attrs={'class':'test-id__field-label'})):
                        self.worksheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                    
                    #Owner and Insured
                    soup_data2 = soup_data[1]
                    soup_data2 = soup_data2.find('div',attrs={'class':'slds-is-relative'})
                    for col_num, strong_tag in enumerate(soup_data2.find_all('span',attrs={'class':'slds-form-element__label'})):
                        self.ownerSheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                    try:
                        file = open(self.reportPath+policy+"_benefit.txt",encoding="utf-8")#append mode 
                        #Full Html src
                        soup_all_src = BeautifulSoup(file.read(), 'lxml')
                        file.close()

                        #find the body first
                        soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')
                        
                        soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','bad40 js-tab tabs__content active uiTab')
                        
                        soup_data2 = soup_section.find('div',attrs={'class':'slds-is-relative'})

                        for col_num, strong_tag in enumerate(soup_data2.find_all('span',attrs={'class':'slds-form-element__label'})):
                            self.benefitSheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    except:
                        pass


                    file = open(self.reportPath+policy+"_plan.txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    #find the body first
                    soup_table = soup_all_src.find('table')

                    soup_header = soup_table.find('thead')

                    for col_num, strong_tag in enumerate(soup_header.find_all('span',attrs={'class':'slds-truncate'})):
                        self.planSheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        policy_iteration = self.maxPolicyListSize + 1

                    self.logger.writeLogString('AXA-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                    break
                except FileNotFoundError as ex:
                    self.logger.writeLogString('AXA-HEADER','FILE NOT FOUND')
                except Exception as ex:
                    self.logger.writeLogString('AXA-HEADER','EXCEPTION:'+str(ex))
                finally:
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildHeaderQueue:
                        self.buildHeaderQueue.remove(policy)
            else:
                time.sleep(1)

    def __buildReportHeaderHalfFlow(self):
        self.logger.writeLogString('AXA-HEADER','START BUILD HEADER HALFFLOW')
        for policy in self.policyList:
            self.logger.writeLogString('AXA-HEADER','POLICY NO.:{0}'.format(str(policy)))
            if self.isStopped:
                return
            try:
                file = open(self.inputPath+policy+"_details.txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()

                #find the body first
                soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')
                
                soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','2 js-tab tabs__content active uiTab')

                soup_data = soup_section.find_all('div',attrs={'class':'ui-widget'})

                soup_data1 = soup_data[0]

                soup_data1 = soup_data1.find('div',attrs={'class':'test-id__section-content slds-section__content section__content'}) 

                for col_num, strong_tag in enumerate(soup_data1.find_all('span',attrs={'class':'test-id__field-label'})):
                    self.worksheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                
                #Owner and Insured
                soup_data2 = soup_data[1]
                soup_data2 = soup_data2.find('div',attrs={'class':'slds-is-relative'})
                for col_num, strong_tag in enumerate(soup_data2.find_all('span',attrs={'class':'slds-form-element__label'})):
                    self.ownerSheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                try:
                    file = open(self.inputPath+policy+"_benefit.txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    #find the body first
                    soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')
                    
                    soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','bad40 js-tab tabs__content active uiTab')
                    
                    soup_data2 = soup_section.find('div',attrs={'class':'slds-is-relative'})

                    for col_num, strong_tag in enumerate(soup_data2.find_all('span',attrs={'class':'slds-form-element__label'})):
                        self.benefitSheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                except:
                    pass



                file = open(self.inputPath+policy+"_plan.txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()

                #find the body first
                soup_table = soup_all_src.find('table')

                soup_header = soup_table.find('thead')

                for col_num, strong_tag in enumerate(soup_header.find_all('span',attrs={'class':'slds-truncate'})):
                    self.planSheet.write(0, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                #No error when building the header,break all loop and then stop this thread
                self.logger.writeLogString('AXA-HEADER','BUILD HEADER COMPLETED, BREAK LOOP')
                break
            except FileNotFoundError as ex:
                self.logger.writeLogString('AXA-HEADER','FILE NOT FOUND')
            except Exception as ex:
                self.logger.writeLogString('AXA-HEADER','EXCEPTION:'+str(ex))
 
    def __buildReport(self):
        self.logger.writeLogString('AXA-CONTENT','START BUILD REPORT')
        policy_iteration = 0
        while policy_iteration < self.maxPolicyListSize:
            for policy in self.buildReportQueue:
                if self.isStopped:
                    return
                self.frame.setStatusLableText(self.stringValue.buildReport.get().format(str(policy),""))
                self.logger.writeLogString('AXA-CONTENT','POLICY NO.:{0}'.format(str(policy)))
                try:
                    self.worksheet.write(policy_iteration+1,0,str(policy))
                    self.ownerSheet.write(policy_iteration+1,0,str(policy))
                    self.benefitSheet.write(policy_iteration+1,0,str(policy))
                    self.planSheet.write(policy_iteration+1,0,str(policy))
                    file = open(self.reportPath+policy+"_details.txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')

                    soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','2 js-tab tabs__content active uiTab')

                    soup_data = soup_section.find_all('div',attrs={'class':'ui-widget'})

                    soup_data1 = soup_data[0]

                    soup_data1 = soup_data1.find('div',attrs={'class':'test-id__section-content slds-section__content section__content'}) 

                                    
                    for col_num,strong_tag in enumerate(soup_data1.find_all('span',attrs={'class':'test-id__field-value slds-form-element__static slds-grow is-read-only'})):
                        self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                    #Owner and Insured
                    soup_data2 = soup_data[1]

                    soup_data2 = soup_data2.find('div',attrs={'class':'slds-is-relative'})
                    for col_num, strong_tag in enumerate(soup_data2.find_all('div',attrs={'class':'slds-form-element__control'})):
                        self.ownerSheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))


                    try:
                        file = open(self.reportPath+policy+"_benefit.txt",encoding="utf-8")#append mode 
                        #Full Html src
                        soup_all_src = BeautifulSoup(file.read(), 'lxml')
                        file.close()

                        #find the body first
                        soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')
                        
                        soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','bad40 js-tab tabs__content active uiTab')
                        
                        soup_data2 = soup_section.find('div',attrs={'class':'slds-is-relative'})

                        for col_num, strong_tag in enumerate(soup_data2.find_all('div',attrs={'class':'slds-form-element__control'})):
                            self.benefitSheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                    except:
                        pass

                    
                    file = open(self.reportPath+policy+"_plan.txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    #find the body first
                    soup_table = soup_all_src.find('table')

                    soup_header = soup_table.find('tbody')

                    for col_num, strong_tag in enumerate(soup_header.find_all('div',attrs={'class':'slds-truncate'})):
                        self.planSheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                        
                except FileNotFoundError:
                    self.worksheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                    self.frame.setStatusLableText(self.stringValue.buildReport.get().format(str(policy),"not found"))
                    self.logger.writeLogString('AXA-CONTENT','FILE NOT FOUND')
                    self.frame.setListItemColor(str(policy),self.STATUS_EXCEPTION)
                except Exception as ex:
                    self.worksheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!")
                    self.frame.setStatusLableText(self.stringValue.buildReport.get().format(str(policy),"failed"))
                    self.logger.writeLogString('AXA-CONTENT','EXCEPTION:'+str(ex))
                    self.frame.setListItemColor(str(policy),self.STATUS_EXCEPTION)
                finally:
                    self.frame.setStatusProgresValueByValue(1)
                    policy_iteration = policy_iteration + 1
                    if policy in self.buildReportQueue:
                        self.buildReportQueue.remove(policy)
                    self.frame.setListItemColor(str(policy),self.STATUS_REPORT_COMPLETE)
            else:
                time.sleep(1)
                        
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText(self.stringValue.completed.get())
        self.logger.writeLogString('AXA-CONTENT','COMPLETED BUILD REPORT')

    def __buildReportOnly(self):
        self.logger.writeLogString('AXA-CONTENT','START BUILD REPORT OFFLINE MODE')
        for policy_iteration,policy in enumerate(self.policyList):
            if self.isStopped:
                return
            self.frame.setStatusLableText(self.stringValue.buildReport.get().format(str(policy),""))
            self.logger.writeLogString('AXA-CONTENT','POLICY NO.:{0}'.format(str(policy)))
            try:
                self.worksheet.write(policy_iteration+1,0,str(policy))
                self.ownerSheet.write(policy_iteration+1,0,str(policy))
                self.benefitSheet.write(policy_iteration+1,0,str(policy))
                self.planSheet.write(policy_iteration+1,0,str(policy))
                file = open(self.inputPath+policy+"_details.txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()

                soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')

                soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','2 js-tab tabs__content active uiTab')

                soup_data = soup_section.find_all('div',attrs={'class':'ui-widget'})

                soup_data1 = soup_data[0]

                soup_data1 = soup_data1.find('div',attrs={'class':'test-id__section-content slds-section__content section__content'}) 

                                
                for col_num,strong_tag in enumerate(soup_data1.find_all('span',attrs={'class':'test-id__field-value slds-form-element__static slds-grow is-read-only'})):
                    self.worksheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                #Owner and Insured
                soup_data2 = soup_data[1]

                soup_data2 = soup_data2.find('div',attrs={'class':'slds-is-relative'})
                for col_num, strong_tag in enumerate(soup_data2.find_all('div',attrs={'class':'slds-form-element__control'})):
                    self.ownerSheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))

                try:
                    file = open(self.inputPath+policy+"_benefit.txt",encoding="utf-8")#append mode 
                    #Full Html src
                    soup_all_src = BeautifulSoup(file.read(), 'lxml')
                    file.close()

                    #find the body first
                    soup_pdBody = self.SearchByHtmlTagClassValue(soup_all_src,'div','js-tabset uiTabset--base uiTabset--default uiTabset forceCommunityTabset')
                    
                    soup_section = self.SearchByHtmlTagClassValue(soup_pdBody,'section','bad40 js-tab tabs__content active uiTab')
                    
                    soup_data2 = soup_section.find('div',attrs={'class':'slds-is-relative'})

                    for col_num, strong_tag in enumerate(soup_data2.find_all('div',attrs={'class':'slds-form-element__control'})):
                        self.benefitSheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))
                except:
                    pass

                
                file = open(self.inputPath+policy+"_plan.txt",encoding="utf-8")#append mode 
                #Full Html src
                soup_all_src = BeautifulSoup(file.read(), 'lxml')
                file.close()

                #find the body first
                soup_table = soup_all_src.find('table')

                soup_header = soup_table.find('tbody')

                for col_num, strong_tag in enumerate(soup_header.find_all('div',attrs={'class':'slds-truncate'})):
                    self.planSheet.write(policy_iteration+1, col_num+1, strong_tag.text.strip().replace('\t','').replace('\n','').replace(u'\xa0', u' '))


            except FileNotFoundError:
                self.worksheet.write(policy_iteration+1,1,str(policy)+" not found in this A/C, please check other A/C")
                self.frame.setStatusLableText(self.stringValue.buildReport.get().format(str(policy),"not found"))
                self.logger.writeLogString('AXA-CONTENT','FILE NOT FOUND')
                self.frame.setListItemColor(str(policy),self.STATUS_EXCEPTION)
            except Exception as ex:
                self.worksheet.write(policy_iteration+1,1,"System Error ! Please contact IT Support!")
                self.frame.setStatusLableText(self.stringValue.buildReport.get().format(str(policy),"failed"))
                self.logger.writeLogString('AXA-CONTENT','EXCEPTION:'+str(ex))
                self.frame.setListItemColor(str(policy),self.STATUS_EXCEPTION)
            finally:
                self.frame.setStatusProgresValueByValue(2)
                self.frame.setListItemColor(str(policy),self.STATUS_REPORT_COMPLETE)
        
        self.buildHeaderThread.join()
        self.workbook.close()
        self.frame.setStatusLableText(self.stringValue.completed.get())
        self.logger.writeLogString('AXA-CONTENT','COMPLETED BUILD REPORT OFFLINE MODE')


        
