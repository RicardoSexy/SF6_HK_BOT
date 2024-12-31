import pickle, time, logging
from pydantic import BaseModel, DirectoryPath
from selenium import webdriver
import config as c
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

def main():
    options = webdriver.ChromeOptions() 
    preferences = {
                    "profile.default_content_settings.popups": 0,
                    "directory_upgrade": True,
                }
    options.add_argument("--incognito")
    options.add_experimental_option('prefs', preferences)
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.streetfighter.com/6/buckler/zh-hant/auth/loginep?redirect_url=/profile/1023683514')
    
    config = Config(user=c.config().user, pw=c.config().pw, path=c.bot_config().path)
    
    autodownload(driver, config).run()

class Config(BaseModel):
    user: str
    pw: str
    path: DirectoryPath

class autodownload:
    def __init__(self, driver: webdriver.Chrome, config: Config) -> None:
        self.driver = driver
        self.user = config.user
        self.pw = config.pw
        self.path = config.path
        
    def information(self):
        try:
            cookie_accept = self.driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
            cookie_accept.click()
            
            country_select = Select(self.driver.find_element(By.ID, 'country'))
            country_select.select_by_value("HK")
            
            year_select = Select(self.driver.find_element(By.ID, 'birthYear'))
            year_select.select_by_value("2000")
            
            month_select = Select(self.driver.find_element(By.ID, 'birthMonth'))
            month_select.select_by_value("1")
            
            day_select = Select(self.driver.find_element(By.ID, 'birthDay'))
            day_select.select_by_value("1")
            
            submit = self.driver.find_element(By.NAME, 'submit')
            submit.click()
        except Exception as e:
            logging.error(f'ERROR information: {e}')
    
    def login(self):
        try:
            login = self.driver.find_element(By.NAME, 'email')
            login.send_keys(self.user)
            
            password = self.driver.find_element(By.NAME, 'password')
            password.send_keys(self.pw)
            password.send_keys(Keys.ENTER)
        except Exception as e:
            logging.error(f'ERROR login: {e}')
        
    def cookies(self):
        try:
            cookie_accept = self.driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
            cookie_accept.click()
            time.sleep(2)
            pickle.dump(self.driver.get_cookies() , open(f"{self.path}/data/cookies.pkl","wb"))
            logging.info(f'Cookies.pkl download success. Path:{self.path}/data/cookies.pkl')
        except Exception as e:
            logging.error(f'ERROR cookies: {e}')
        
    def run(self):
        
        self.information()
        time.sleep(2)
        self.login()
        time.sleep(10)
        self.cookies()