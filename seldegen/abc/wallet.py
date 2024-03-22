from typing import Self, Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from abc import abstractmethod
from .base_account import BaseAccount
from .browser_extension import BrowserExtension
from seldegen.exceptions import InvalidMnemonicError
from seldegen.types import WalletAccount


class Wallet(BaseAccount, BrowserExtension):
    """This is an abstract class whose inheritors interact with digital wallets"""

    def __init__(
            self,
            driver: WebDriver,
            password: str,
            mnemonic: str,
            extension_url: list[str],
            extension_id: str,
            private_key: Optional[str] = None,
            public_key: Optional[str] = None
    ) -> None:
        """
        For more information about extension IDs go to BrowserExtension documentation

        :param driver: Driver to be interacted with
        :param password: Password for wallet
        :param mnemonic: Mnemonic of wallet
        :param extension_url: Parts of extension's url provided as ['chrome-extension://', main_page_url].
        :param extension_id: Extension's'id
        """
        url = extension_url.copy()
        url.insert(1, extension_id)
        url = ''.join(url)
        BaseAccount.__init__(self, driver, url, password, login=mnemonic)
        BrowserExtension.__init__(self, driver, extension_url, extension_id)
        mnemonic_split = mnemonic.split()

        if len(mnemonic_split) != 12:
            raise InvalidMnemonicError(mnemonic_split)

        self.__mnemonic = mnemonic.split()
        self._public_key = public_key
        self._private_key = private_key

        self.__base_private_key = private_key
        self.__base_public_key = public_key
        self._accounts = [WalletAccount(private_key=private_key, public_key=public_key)]

    @property
    def mnemonic(self) -> list[str]:
        """
        Returns wallet's mnemonic
        :return: list[str]
        """
        return self.__mnemonic

    @property
    def public_key(self) -> str:
        """
        Returns current account`s public key
        :return: str | None
        """
        return self._public_key

    @property
    def private_key(self) -> str:
        """
        Returns current account's private key
        :return: str | None
        """
        return self._private_key

    @property
    def base_private_key(self) -> str:
        """
        Returns base wallet's private key. Base private key - is key related to wallet's mnemonic
        :return:
        """
        return self.__base_private_key

    @property
    def base_public_key(self) -> str:
        """
        Returns base wallet's public key. Base public key - is key related to wallet's mnemonic
        :return:
        """
        return self.__base_public_key

    @property
    def accounts(self) -> list[WalletAccount]:
        """
        Returns all accounts` private keys'
        :return: str | None
        """
        return self._accounts.copy()

    @abstractmethod
    def sign_in(self) -> None:
        """
        Authorizes into the wallet
        :return: None
        """
        pass

    @abstractmethod
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party wallet connection
        :return: None
        """
        pass

    @classmethod
    @abstractmethod
    def sign_up(
            cls,
            driver: WebDriver,
            password: str,
            extension_id: str
    ) -> Self:
        """
        For more information about extension IDs go to BrowserExtension documentation

        Creates an instance of digital wallet by the creating all-new wallet
        :param driver: Driver to be interacted with
        :param password: Password for wallet
        :param extension_id: Extension's'id
        :return: Wallet
        """
        pass

    @abstractmethod
    def confirm(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs confirming operation. Confirming operations appear in such actions as minting NFT, snapshot voting and
        other. Most of the time, you need to use it after function connect()
        :return: None
        """
        pass
