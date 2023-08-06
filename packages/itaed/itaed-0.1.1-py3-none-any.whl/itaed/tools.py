from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

class Tools:
    @staticmethod
    def refresh_page(self): 

        driver = self.driver
        driver.refresh()  

    def take_screenshot(self, driver, consts, by, element_name, screenshot_name):
        print("element_name:", element_name)
        if (by == "class_name"):
            element = driver.find_element(By.CLASS_NAME, element_name)
            print(element.size)
        elif (by == "id"):
            element = driver.find_element(By.ID, element_name)
        total_height = element.size["height"]+1000
        driver.set_window_size(1920, total_height) # save screen shot on SCREENSHOT_PATH
        element.screenshot(consts.DATA["SCREENSHOT_PATH"] + "/" + screenshot_name + ".png")

    @staticmethod
    def define_locater(self, inspected_element):
        locater_type= inspected_element.split('=')[0]
        if locater_type == "name":
            locater_type = By.NAME
            element= inspected_element.split('=')[1]
        elif locater_type== "class name":
            locater_type = By.CLASS_NAME
            element= inspected_element.split('=')[1]
        elif locater_type == "xpath":
            locater_type = By.XPATH
            element= inspected_element.replace('xpath=','')
        elif locater_type == "id":
            locater_type = By.ID
            element= inspected_element.split('=')[1]
        elif locater_type == "css":
            locater_type = By.CSS_SELECTOR
            element= inspected_element.split('=')[1]
        else:
            locater_type = By.XPATH
            element= inspected_element.replace('xpath=','')
        return locater_type, element        
