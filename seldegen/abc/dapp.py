from abc import ABC
from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from .base_account import BaseAccount
from .wallet import Wallet
from seldegen.email import Email


class DApp(BaseAccount, ABC):
    """This is an abstract class whose inheritors interact with decentralized apps, based on wallets"""
    def __init__(
            self,
            driver: WebDriver,
            url: str,
            wallet: Wallet,
            email: Optional[Email] = None
    ):
        """
        :param driver: Driver to be interacted with
        :param url: URL of a social's logging page
        :param wallet: Instance of wallet-based class
        :param email: Instance of the Email created from account's credentials
        """
        super().__init__(driver, url, wallet.password, email)
        self.__wallet = wallet

    @property
    def wallet(self) -> Wallet:
        """
        Returns an instance of the wallet-based class
        :return: Metamask
        """
        return self.__wallet

    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party wallet-based account connection
        :return:
        """
        self.wallet.confirm()
