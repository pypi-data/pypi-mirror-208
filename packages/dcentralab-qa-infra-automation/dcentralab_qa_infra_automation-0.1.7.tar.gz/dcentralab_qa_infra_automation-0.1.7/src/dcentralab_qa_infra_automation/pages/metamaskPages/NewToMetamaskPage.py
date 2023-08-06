from dcentralab_qa_infra_automation.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

"""
new to metamask page

@Author: Efrat Cohen
@Date: 12.2022
"""

"""page locators"""
TITLE = (By.XPATH, "//*[contains(@class,'select-action__body-header')]")
IMPORT_WALLET_BUTTON = (By.XPATH, "//*[contains(text(),'Import wallet')]")


class NewToMetamaskPage(BasePage):

    def __init__(self, driver):
        """ ctor - call to BasePage ctor for initialize """
        super().__init__(driver)

    def is_page_loaded(self):
        """
        check if on current page
        :return: true if on page, otherwise return false
        """
        return self.is_element_exist(TITLE)

    def click_on_import_wallet(self):
        """
        click on import wallet
        """
        self.click(IMPORT_WALLET_BUTTON)
