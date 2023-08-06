from dcentralab_qa_infra_automation.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

"""
welcome to metamask page

@Author: Efrat Cohen
@Date: 12.2022
"""

"""page locators"""
TITLE = (By.XPATH, "//*[contains(text(),'Welcome to MetaMask')]")
GET_STARTED_BUTTON = (By.XPATH, "//*[contains(text(),'Get started')]")
CONNECT_WALLET_POPUP = (By.XPATH, "//*[contains(@class,'permissions-connect-header__title')]")


class WelcomeToMetamaskPage(BasePage):

    def __init__(self, driver):
        """ ctor - call to BasePage ctor for initialize """
        super().__init__(driver)

    def is_page_loaded(self):
        """
        check if on current page
        :return: true if on page, otherwise return false
        """
        return self.is_element_exist(TITLE)

    def click_on_get_started(self):
        """
        click on get started button
        """
        self.click(GET_STARTED_BUTTON)