from dcentralab_qa_infra_automation.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

"""
connect with metamask page

@Author: Efrat Cohen
@Date: 12.2022
"""

"""page locators"""
TITLE = (By.XPATH, "//*[contains(@class,'header__title')]")
NEXT_BUTTON = (By.XPATH, "//*[contains(text(),'Next')]")
CONNECT_BUTTON = (By.XPATH, "//button[contains(text(),'Connect')]")


class ConnectWithMetamaskPage(BasePage):

    def __init__(self, driver):
        """ ctor - call to BasePage ctor for initialize """
        super().__init__(driver)

    def is_page_loaded(self):
        """
        check if on current page
        :return: true if on page, otherwise return false
        """
        return self.is_element_exist(TITLE)

    def click_on_next_button(self):
        """
        click on next button
        """
        self.click(NEXT_BUTTON)

    def click_on_connect_button(self):
        """
        click on connect button
        """
        self.click(CONNECT_BUTTON)
