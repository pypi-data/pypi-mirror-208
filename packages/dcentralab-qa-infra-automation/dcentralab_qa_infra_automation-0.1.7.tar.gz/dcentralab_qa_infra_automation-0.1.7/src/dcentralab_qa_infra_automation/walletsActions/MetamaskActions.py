import time

import pytest
from dcentralab_qa_infra_automation.utils.WalletsActionsInterface import WalletsActionsInterface

from dcentralab_qa_infra_automation.pages.metamaskPages.ConfirmPage import ConfirmPage
from dcentralab_qa_infra_automation.pages.metamaskPages.ImportWalletPage import ImportWalletPage
from dcentralab_qa_infra_automation.pages.metamaskPages.CongratulationsPage import CongratulationsPage
from dcentralab_qa_infra_automation.pages.metamaskPages.ConnectWithWalletPage import ConnectWithMetamaskPage
from dcentralab_qa_infra_automation.pages.metamaskPages.ImproveMetamaskPage import ImproveMetamaskPage
from dcentralab_qa_infra_automation.pages.metamaskPages.NewToMetamaskPage import NewToMetamaskPage
from dcentralab_qa_infra_automation.pages.metamaskPages.SwitchNetworkPage import SwitchNetworkPage
from dcentralab_qa_infra_automation.pages.metamaskPages.WalletConnectedHomePage import WalletConnectedHomePage
from dcentralab_qa_infra_automation.pages.metamaskPages.WelcomeToMetamaskPage import WelcomeToMetamaskPage


class MetamaskActions(WalletsActionsInterface):

    def __init__(self, driver):
        self.driver = driver

    def import_wallet(self):
        """
        import wallet process
        """
        # Open new tab
        self.driver.execute_script("window.open('');")

        # Focus on the new tab window
        self.driver.switch_to.window(self.driver.window_handles[1])

        # Open chrome extension
        self.driver.get(pytest.properties.get("metamask.connect.url"))

        # Focus on the first tab window
        self.driver.switch_to.window(self.driver.window_handles[1])

        welcomeToMetamaskPage = WelcomeToMetamaskPage(self.driver)

        # Check if metamask wallet page loaded
        assert welcomeToMetamaskPage.is_page_loaded(), "welcome to metamask page loaded"

        # Click on get started button
        welcomeToMetamaskPage.click_on_get_started()

        improveMetamaskPage = ImproveMetamaskPage(self.driver)

        # Check if improve to metamask page loaded
        assert improveMetamaskPage.is_page_loaded(), "improve metamask page loaded"

        # Click on I agree button
        improveMetamaskPage.click_on_i_agree_button()

        newToMetamaskPage = NewToMetamaskPage(self.driver)

        # Check if new to metamask page loaded
        assert newToMetamaskPage.is_page_loaded(), "new to metamask page loaded"

        # Click on import wallet
        newToMetamaskPage.click_on_import_wallet()

        importWalletPage = ImportWalletPage(self.driver)

        # Check if import wallet page loaded
        assert importWalletPage.is_page_loaded(), "import wallet page loaded"

        # Insert secret recovery phrase
        importWalletPage.insert_secret_recovery_phrase()

        # Insert password
        importWalletPage.insert_password()

        # Insert confirm password
        importWalletPage.insert_confirm_password()

        # Click on agree terms of use
        importWalletPage.agree_terms_of_use()

        # Click on import button
        importWalletPage.click_on_submit_import_button()

        congratulationsPage = CongratulationsPage(self.driver)

        # Check if congratulations page loaded
        assert congratulationsPage.is_page_loaded(), "congratulations page loaded"

        # Click on all done button
        congratulationsPage.click_on_all_done()

        walletConnectedHomePage = WalletConnectedHomePage(self.driver)

        # Check if wallet connected home page loaded
        assert walletConnectedHomePage.is_page_loaded(), "wallet connected home page loaded"

        # Focus on the new tab window
        self.driver.switch_to.window(self.driver.window_handles[0])

        time.sleep(2)

    def connect_wallet(self):
        """
        connect wallet implementation
        """
        time.sleep(3)

        # Switch focus to metamask tab
        self.driver.switch_to.window(self.driver.window_handles[1])

        # Refresh the page
        self.driver.refresh()

        connectWithMetamaskPage = ConnectWithMetamaskPage(self.driver)

        # Check if on connect with metamask page
        assert connectWithMetamaskPage.is_page_loaded(), "connect with metamask page loaded"

        # Click on next button
        connectWithMetamaskPage.click_on_next_button()

        # Click on connect button
        connectWithMetamaskPage.click_on_connect_button()

        switchNetworkPage = SwitchNetworkPage(self.driver)

        # Check if switch network page loaded
        assert switchNetworkPage.is_page_loaded(), "allow site to switch the network page loaded"

        # Click on switch network button
        switchNetworkPage.click_on_switch_network()

        walletConnectedHomePage = WalletConnectedHomePage(self.driver)

        # Check if wallet connected home page loaded
        assert walletConnectedHomePage.is_page_loaded(), "wallet connected home page loaded"

        # Switch focus to site tab
        self.driver.switch_to.window(self.driver.window_handles[0])

    def confirm(self):
        """
        confirm wallet process
        """
        time.sleep(5)

        # Switch focus to metamask tab
        self.driver.switch_to.window(self.driver.window_handles[1])

        # Refresh the page
        self.driver.refresh()

        confirmPage = ConfirmPage(self.driver)

        # Check is confirm page loaded
        assert confirmPage.is_page_loaded(), "confirm page loaded"

        # Check is confirm button exist.
        assert confirmPage.is_confirm_button_exist()

        # Click on confirm button
        confirmPage.click_on_confirm_button()

        walletConnectedHomePage = WalletConnectedHomePage(self.driver)

        # Check if wallet connected home page loaded
        assert walletConnectedHomePage.is_page_loaded(), "wallet connected home page loaded"

        # Switch focus to site tab
        self.driver.switch_to.window(self.driver.window_handles[0])
