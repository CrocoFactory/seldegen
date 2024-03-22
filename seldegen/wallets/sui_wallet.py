import time
from typing import Self, Optional
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from croco_selenium import click, send_keys, get_element_text, get_element, get_element_attribute
from croco_selenium import handle_pop_up
from seldegen.abc.wallet import Wallet
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class SuiWallet(Wallet):
    """This is a class interacting with SuiWallet"""

    def __init__(
            self,
            driver: WebDriver,
            password: str,
            mnemonic: str,
            extension_id='opcgpfmipidbgpenhmajoajpbobppdil'
    ) -> None:
        """
        :param driver: Driver to be interacted with
        :param password: Password for SuiWallet account
        :param mnemonic: Mnemonic of Sui Wallet account
        :param extension_id: Extension's'id
        """
        extension_url = ['chrome-extension://', '/ui.html']
        super().__init__(driver, password, mnemonic, extension_url, extension_id)
        self.__public_key = None

    @property
    def public_key(self) -> str | None:
        """Public key of account"""
        return self.__public_key

    def sign_in(self) -> None:
        """
        Authorizes into the Sui Wallet
        :return:
        """
        driver = self.driver
        driver.get(self.extension_url)

        options_xpath = '//*[@id="root"]/div/div[1]/div[4]/a'
        click(driver, _DEFAULT_TIMEOUT, options_xpath)

        import_xpath = '//*[@id="overlay-portal-container"]/div/div[2]/div/section[2]/a[1]'
        click(driver, _DEFAULT_TIMEOUT, import_xpath)

        self.__verify_mnemnonic(driver, self.mnemonic)
        self.__create_password(driver, self.password)
        try:
            dismiss_xpath = '//*[@id="overlay-portal-container"]/div/button'
            click(driver, 10, dismiss_xpath)
        except TimeoutException:
            pass

        time.sleep(1)

        self.__public_key = self.__get_public_key(driver)

    @staticmethod
    def __get_public_key(driver: WebDriver) -> str:
        coin_page_xpath = '//a[@data-testid="nav-tokens"]'
        click(driver, _DEFAULT_TIMEOUT, coin_page_xpath)

        explorer_xpath = '/html/body/div[1]/div/div[1]/div/div/main/div/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[2]/div/a'
        href = get_element_attribute(driver, _DEFAULT_TIMEOUT, explorer_xpath, 'href')
        driver.get(href)

        return get_element_text(driver, _DEFAULT_TIMEOUT, '//h3')

    @staticmethod
    def __create_password(driver: WebDriver, password: str) -> None:
        password_input_xpath = '//*[@id="root"]/div/div[1]/div[3]/form/div[1]/label/div[2]/input'
        send_keys(driver, _DEFAULT_TIMEOUT, password_input_xpath, password)

        repeat_password_input_xpath = '//*[@id="root"]/div/div[1]/div[3]/form/div[2]/label/div[2]/input'
        send_keys(driver, _DEFAULT_TIMEOUT, repeat_password_input_xpath, password)

        agree_to_terms_xpath = '//*[@id="acceptedTos"]'
        click(driver, _DEFAULT_TIMEOUT, agree_to_terms_xpath)

        continue_xpath = '//*[@id="root"]/div/div[1]/div[3]/form/div[5]/div[2]/button[2]'
        click(driver, _DEFAULT_TIMEOUT, continue_xpath)
        time.sleep(5)

    @staticmethod
    def __get_mnemonic(driver: WebDriver) -> list[str]:
        reveal_mnemonic_xpath = '//*[@id="root"]/div/div[1]/div[3]/div/div[3]/div[2]/div[2]/button'
        click(driver, _DEFAULT_TIMEOUT, reveal_mnemonic_xpath)

        mnemonic = []
        for word_number in range(1, 13):
            word_xpath = f'//*[@id="root"]/div/div[1]/div[3]/div/div[3]/div[1]/div[1]/div/span[{word_number}]'
            word = get_element_text(driver, 60, word_xpath)
            mnemonic.append(word)

        agree_input_xpath = '//*[@id="root"]/div/div[1]/div[3]/div/div[7]/label'
        click(driver, _DEFAULT_TIMEOUT, agree_input_xpath)

        continue_button_xpath = '//*[@id="root"]/div/div[1]/div[3]/a'
        click(driver, _DEFAULT_TIMEOUT, continue_button_xpath)
        return mnemonic

    @staticmethod
    def __verify_mnemnonic(driver: WebDriver, mnemonic: list[str]) -> None:
        for word_number in range(12):
            word_xpath = f'//*[@id="recoveryPhrase.{word_number}"]'
            send_keys(driver, 60, word_xpath, mnemonic[word_number])

        click(driver, _DEFAULT_TIMEOUT, '//*[@id="root"]/div/div[1]/div[3]/form/div[2]/div/button[2]')

    @classmethod
    def sign_up(
            cls,
            driver: WebDriver,
            password: str,
            extension_id: str = 'opcgpfmipidbgpenhmajoajpbobppdil'
    ) -> Self:
        """
        Creates an instance of SuiWallet by the creating all-new wallet
        :param driver: Driver to be interacted with
        :param password: Password for SuiWallet account
        :param extension_id: Extension's'id
        :return: SuiWallet
        """
        driver.get(f'chrome-extension://{extension_id}/ui.html')

        options_xpath = '//*[@id="root"]/div/div[1]/div[4]/a'
        click(driver, _DEFAULT_TIMEOUT, options_xpath)

        create_wallet_xpath = '//*[@id="overlay-portal-container"]/div/div[2]/div/section[1]/a'
        click(driver, 10, create_wallet_xpath)

        cls.__create_password(driver, password)

        mnemonic = cls.__get_mnemonic(driver)

        try:
            dismiss_xpath = '//*[@id="overlay-portal-container"]/div/button'
            click(driver, 10, dismiss_xpath)
        except TimeoutException:
            pass

        wallet = cls(driver, password, ' '.join(mnemonic))
        wallet.SuiWallet__public_key = cls.__get_public_key(driver)
        return wallet

    def __approve(self) -> None:
        driver = self.driver

        approve_button_xpath = '/html/body/div[1]/div/div[1]/div/div/main/div/div[2]/div/button[2]'
        approve_button = get_element(driver, 60, approve_button_xpath)

        try:
            unlock_xpath = '//*[@id="root"]/div/div[1]/div/div/main/div/div[1]/div[2]/div/div[2]/div[2]/div/div[3]/div/div/button'
            click(driver, 5, unlock_xpath)
        except TimeoutException:
            pass
        else:
            password_input_xpath = '//input[@type="password"]'
            send_keys(driver, 5, password_input_xpath, self.password)

            unlock_button_xpath = '/html/body/div[5]/div[2]/div/div/button[2]'
            click(driver, 5, unlock_button_xpath)

            select_all_xpath = '//*[@id="root"]/div/div[1]/div/div/main/div/div[1]/div[2]/div/div/button'
            click(driver, 5, select_all_xpath)

        approve_button.click()

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party SuiWallet connection
        :return: None
        """
        self.__approve()

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def confirm(self) -> None:
        """
        Performs confirming operation. Confirming operations appear in such actions as minting NFT, snapshot voting and
        other. Most of the time, you need to use it after function connect()
        :return: None
        """
        self.__approve()
