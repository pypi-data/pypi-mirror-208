import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """
    The BasePage class holds all common functionality across the website.
    So, we can use those function in every page.

    @Author: Efrat Cohen
    @Date: 12.2022
    """

    def __init__(self, driver):
        """ BasePage constructor - This function is called every time a new object of the base class is created"""
        self.driver = driver
        self.timeout = pytest.properties.get("timeout")

    def is_element_exist(self, by_locator):
        """
        check if element exist
        @param: by_locator - current locator
        @return: true if on page, otherwise return false
        """
        try:
            WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator))
            return True
        except:
            # If element not found
            pytest.logger.info("element not found")
            return False

    def is_element_exist_with_custom_timeout(self, by_locator, timeout):
        """
        check if element exist
        @param: by_locator - current locator
        @return: true if on page, otherwise return false
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(by_locator))
            return True
        except:
            # If element not found
            print("element not found")
            return False

    def is_specific_element_exist(self, by_locator, index):
        """
        check if specific element of a list exist
        @param: by_locator - current locator
        @param: index - list index to check
        @return: true if on page, otherwise return false
        """
        try:
            WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_all_elements_located(by_locator))[index]
            return True
        except:
            # If element not found
            print("element not found")
            return False

    def click(self, by_locator):
        """
         Performs click on web element whose locator is passed to it
         :param by_locator - current locator to click on
        """

        pytest.logger.info("clicking on " + str(by_locator) + " button")
        WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator)).click()

    def click_on_specific_item_in_list(self, by_locator, index):
        """ Performs click on specific item in web element list whose locator is passed to it """

        pytest.logger.info("clicking on " + str(by_locator) + " button")
        WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_all_elements_located(by_locator))[index].click()

    def enter_text(self, by_locator, text):
        """ Performs text entry of the passed in text, in a web element whose locator is passed to it """

        pytest.logger.info("insert value: " + text + " into " + str(by_locator))
        return WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator)).send_keys(text)

    def upload_file(self, by_locator, file_path):
        """
        Performs choose file in input with type file, in a web element whose locator and file path are passed to it
        """
        pytest.logger.info("upload file: " + file_path + " into " + str(by_locator))
        return WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator)).send_keys(file_path)

    def get_text(self, by_locator):
        """
        Performs get text of web element whose locator is passed to it
        :param by_locator - current locator
        :return current element text
        """
        return WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator)).text

    def clear_text(self, by_locator):
        """
        Performs clear value of web element whose locator is passed to it
        :param by_locator - current locator
        """
        WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator)).clear()

    def scroll_to_element(self, by_locator):
        """
        scroll the page to specific element whose locator is passed to it
        :param by_locator - current locator
        """
        element = WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(by_locator))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)