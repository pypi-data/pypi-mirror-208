from dcentralab_qa_infra_automation.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

"""
congratulations page

@Author: Efrat Cohen
@Date: 12.2022
"""

"""page locators"""
TITLE = (By.XPATH, "//*[contains(@class,'first-time-flow__header')]")
ALL_DONE_BUTTON = (By.XPATH, "//*[contains(@class,'first-time-flow__button')]")


class CongratulationsPage(BasePage):

    def __init__(self, driver):
        """ ctor - call to BasePage ctor for initialize """
        super().__init__(driver)

    def is_page_loaded(self):
        """
        check if on current page
        :return: true if on page, otherwise return false
        """
        return self.is_element_exist(TITLE)

    def click_on_all_done(self):
        """
        click on all done button
        """
        self.click(ALL_DONE_BUTTON)
