import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from dcentralab_qa_infra_automation.drivers.HelperFunctions import addExtensionToChrome

"""
init brave browser driver

@Author: Efrat Cohen
@Date: 12.2022
"""


def addBraveToChrome():
    """
    add brave to chrome based on OS type
    :return: binary_location
    """
    binary_location = None
    # On macOS - use mac brave path
    if pytest.data_driven.get("OS") == "windows":
        binary_location = pytest.properties.get("brave.windows.path")
    # On windowsOS - use windows brave path
    elif pytest.data_driven.get("OS") == "mac":
        binary_location = pytest.properties.get("brave.mac.path")
    # If no OS injected
    else:
        pytest.logger.info("no OS type injected, brave did not add to chrome.")

    return binary_location


def initBraveDriver():
    """
    init brave driver, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    options = webdriver.ChromeOptions()
    options.binary_location = addBraveToChrome()

    chrome_service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=options)
    return driver


def initBraveDriverWithExtension():
    """
    init brave driver with CRX extension, using ChromeDriverManager for chromeDriver installation
    :return: driver - driver instance
    """
    options = webdriver.ChromeOptions()
    options.binary_location = addBraveToChrome()
    options.add_extension(addExtensionToChrome())
    chrome_service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=options)
    return driver
