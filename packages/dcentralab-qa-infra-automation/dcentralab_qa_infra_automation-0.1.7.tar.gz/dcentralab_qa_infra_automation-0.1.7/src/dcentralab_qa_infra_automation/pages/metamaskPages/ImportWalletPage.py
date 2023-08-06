from dcentralab_qa_infra_automation.pages.BasePage import BasePage
from selenium.webdriver.common.by import By
import pytest

"""
import wallet page

@Author: Efrat Cohen
@Date: 12.2022
"""

"""page locators"""
TITLE = (By.XPATH, "//*[contains(@class,'first-time-flow__header')]")
SECRET_RECOVERY_PHRASE_0 = (By.ID, "import-srp__srp-word-0")
SECRET_RECOVERY_PHRASE_1 = (By.ID, "import-srp__srp-word-1")
SECRET_RECOVERY_PHRASE_2 = (By.ID, "import-srp__srp-word-2")
SECRET_RECOVERY_PHRASE_3 = (By.ID, "import-srp__srp-word-3")
SECRET_RECOVERY_PHRASE_4 = (By.ID, "import-srp__srp-word-4")
SECRET_RECOVERY_PHRASE_5 = (By.ID, "import-srp__srp-word-5")
SECRET_RECOVERY_PHRASE_6 = (By.ID, "import-srp__srp-word-6")
SECRET_RECOVERY_PHRASE_7 = (By.ID, "import-srp__srp-word-7")
SECRET_RECOVERY_PHRASE_8 = (By.ID, "import-srp__srp-word-8")
SECRET_RECOVERY_PHRASE_9 = (By.ID, "import-srp__srp-word-9")
SECRET_RECOVERY_PHRASE_10 = (By.ID, "import-srp__srp-word-10")
SECRET_RECOVERY_PHRASE_11 = (By.ID, "import-srp__srp-word-11")
PASSWORD_INPUT = (By.ID, "password")
CONFIRM_PASSWORD_INPUT = (By.ID, "confirm-password")
AGREE_TERMS_CHECKBOX = (By.ID, "create-new-vault__terms-checkbox")
SUBMIT_IMPORT_BUTTON = (By.XPATH, "//*[contains(@class,'submit-button')]")


class ImportWalletPage(BasePage):

    def __init__(self, driver):
        """ ctor - call to BasePage ctor for initialize """
        super().__init__(driver)

    def is_page_loaded(self):
        """
        check if on current page
        :return: true if on page, otherwise return false
        """
        return self.is_element_exist(TITLE)

    def insert_secret_recovery_phrase(self):
        """
        insert secret recovery phrase
        """
        self.enter_text(SECRET_RECOVERY_PHRASE_0, pytest.wallets_data.get("secret_recovery_phrase_0"))
        self.enter_text(SECRET_RECOVERY_PHRASE_1, pytest.wallets_data.get("secret_recovery_phrase_1"))
        self.enter_text(SECRET_RECOVERY_PHRASE_2, pytest.wallets_data.get("secret_recovery_phrase_2"))
        self.enter_text(SECRET_RECOVERY_PHRASE_3, pytest.wallets_data.get("secret_recovery_phrase_3"))
        self.enter_text(SECRET_RECOVERY_PHRASE_4, pytest.wallets_data.get("secret_recovery_phrase_4"))
        self.enter_text(SECRET_RECOVERY_PHRASE_5, pytest.wallets_data.get("secret_recovery_phrase_5"))
        self.enter_text(SECRET_RECOVERY_PHRASE_6, pytest.wallets_data.get("secret_recovery_phrase_6"))
        self.enter_text(SECRET_RECOVERY_PHRASE_7, pytest.wallets_data.get("secret_recovery_phrase_7"))
        self.enter_text(SECRET_RECOVERY_PHRASE_8, pytest.wallets_data.get("secret_recovery_phrase_8"))
        self.enter_text(SECRET_RECOVERY_PHRASE_9, pytest.wallets_data.get("secret_recovery_phrase_9"))
        self.enter_text(SECRET_RECOVERY_PHRASE_10, pytest.wallets_data.get("secret_recovery_phrase_10"))
        self.enter_text(SECRET_RECOVERY_PHRASE_11, pytest.wallets_data.get("secret_recovery_phrase_11"))

    def insert_password(self):
        """
        insert password
        """
        self.enter_text(PASSWORD_INPUT, pytest.wallets_data.get("password"))

    def insert_confirm_password(self):
        """
        insert confirm password
        """
        self.enter_text(CONFIRM_PASSWORD_INPUT, pytest.wallets_data.get("password"))

    def agree_terms_of_use(self):
        """
        click on agree terms of use checkbox
        """
        self.click(AGREE_TERMS_CHECKBOX)

    def click_on_submit_import_button(self):
        """
        click on import - submit the import form
        """
        self.click(SUBMIT_IMPORT_BUTTON)