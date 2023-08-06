from dcentralab_qa_infra_automation.drivers.HelperFunctions import addExtensionToChrome
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pytest

"""
init chrome driver, using ChromeDriverManager for chromeDriver installation

@Author: Efrat Cohen
@Date: 11.2022
"""


def initChromeDriver():
    """
    init chrome driver, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    pytest.logger.info("chrome driver type injected, initialize chrome browser")
    chrome_service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service)
    return driver


def initChromeDriverWithExtension():
    """
    init chrome driver with CRX extension, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    options = webdriver.ChromeOptions()
    options.add_extension(addExtensionToChrome())
    chrome_service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=options)
    return driver
