
from behave import *
import itaed
import sys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from itaed.tools import Tools


class Select:
    @staticmethod
    def select_by_index(self, driver, elements, index):
        locater, element = Tools.define_locater(self, elements)
        select = Select(driver.find_element(locater, element))
        selected_element=select.select_by_index(index)
        return selected_element 

    @staticmethod
    def select_by_visible_text(self, driver, elements, text):
        locater, element = Tools.define_locater(self, elements)
        select = Select(driver.find_element(locater, element))
        selected_element=select.select_by_visible_text(text)
        return selected_element 
