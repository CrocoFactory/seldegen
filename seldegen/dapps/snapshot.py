import time
from typing import Optional
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.abc.wallet import Wallet
from seldegen.abc.dapp import DApp
from seldegen.exceptions import NoVotingPowerError
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class Snapshot(DApp):
    """This is a class interacting with https://snapshot.org"""
    def __init__(self, driver: WebDriver, wallet: Wallet):
        """
        :param driver: Driver to be interacted with
        :param wallet: Instance of wallet-based class
        """
        url = 'https://snapshot.org/#/'
        super().__init__(driver, url, wallet)

    def sign_in(self) -> None:
        """
        Authorizes into the Snapshot
        :return: None
        """
        driver = self.driver
        wallet = self.wallet
        driver.get(self.url)
        action_performer = self._action_performer

        connect_xpath = '//button[@data-testid="button-connect-wallet"]'
        action_performer.click(_DEFAULT_TIMEOUT, connect_xpath)

        metamask_xpath = "//button[@data-testid='button-connnect-wallet-injected']"
        action_performer.click(_DEFAULT_TIMEOUT, metamask_xpath)
        wallet.connect()

    def vote(self, poll_url: str, choice: Optional[int] = None) -> None:
        """
        Vote in the poll
        :param poll_url: URL of the poll
        :param choice: Number of vote's choice
        :return: None
        """
        driver = self.driver
        wallet = self.wallet
        action_performer = self._action_performer

        driver.get(poll_url)

        if not choice:
            choice_xpath = "//button[contains(@data-testid, 'sc-choice-button')]"
        else:
            choice_xpath = f"//button[@data-testid='sc-choice-button-{choice}')"

        action_performer.click(_DEFAULT_TIMEOUT, choice_xpath)

        vote_button_xpath = "//button[@data-testid='proposal-vote-button']"
        action_performer.click(_DEFAULT_TIMEOUT, vote_button_xpath)

        confirm_xpath = "//button[@data-testid='confirm-vote-button']"
        confirm_button = action_performer.get_element(_DEFAULT_TIMEOUT, confirm_xpath)
        time.sleep(3)

        disabled = confirm_button.get_attribute('disabled')
        if not disabled:
            confirm_button.click()
        else:
            raise NoVotingPowerError(poll_url)

        wallet.confirm()

        close_modal_xpath = '//button[@data-testid="post-vote-modal-close"]'
        action_performer.click(_DEFAULT_TIMEOUT, close_modal_xpath, ignored_exceptions=TimeoutException)
