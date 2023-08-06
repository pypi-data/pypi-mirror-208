
from behave import *
import itaed
import sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


class ExceptionCheck:
    def driver_wait_exception(self, driver, consts, condition, element_script, timeout):
        try:
            print("Check element: " + str(element_script) + " timeout: " + str(consts.DATA[timeout]) + " condition: " + str(condition))
            WebDriverWait(driver, timeout=consts.DATA[timeout]).until(condition)

        except TimeoutException as ex:
            print("Condition" + str(condition) + "Element is not found " + str(element_script) + " timeout:" + str(consts.DATA[timeout]))
            sys.exit(1)