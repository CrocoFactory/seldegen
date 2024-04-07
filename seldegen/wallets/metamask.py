import time
from eth_account import Account
from selenium.common import TimeoutException, ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.chrome.webdriver import WebDriver
from croco_selenium.decorators import handle_pop_up, handle_in_new_tab
from typing import Literal, cast, Self, Optional
from seldegen.abc.wallet import Wallet
from croco_selenium import ActionPerformer
from seldegen.context import Context
from seldegen.types import WalletAccount

_DEFAULT_TIMEOUT = Context.default_timeout()

_SigningType = Literal['create', 'import']


class Metamask(Wallet):
    """This is a class interacting with Metamask"""

    def __init__(
            self,
            driver: WebDriver,
            password: str,
            mnemonic: str,
            extension_id: str = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
    ) -> None:
        """
        :param driver: Driver to be interacted with
        :param password: Password for Metamask wallet
        :param mnemonic: Mnemonic of Metamask's wallet
        :param extension_id: Extension's'id
        """
        extension_url = ['chrome-extension://', '/home.html']

        Account.enable_unaudited_hdwallet_features()
        account = Account.from_mnemonic(mnemonic)
        private_key = account._private_key.hex()
        public_key = account.address

        super().__init__(
            driver,
            password,
            mnemonic,
            extension_url,
            extension_id,
            public_key=public_key,
            private_key=private_key
        )

        self.__popup_closed = False

    @staticmethod
    def __agree_to_terms(driver: WebDriver, signing_type: _SigningType) -> None:
        action_performer = ActionPerformer(driver)

        checkbox_xpath = '//*[@id="onboarding__terms-checkbox"]'
        action_performer.click(_DEFAULT_TIMEOUT, checkbox_xpath)

        onboarding_xpath = f'//button[@data-testid="onboarding-{signing_type}-wallet"]'
        action_performer.click(_DEFAULT_TIMEOUT, onboarding_xpath)

        time.sleep(1)

        agree_to_terms_xpath = '//button[@data-testid="metametrics-i-agree"]'
        action_performer.click(_DEFAULT_TIMEOUT, agree_to_terms_xpath)

    def __enter_mnemonic(self) -> None:
        action_performer = self._action_performer

        mnemonic = self.mnemonic
        input_number = 0
        for word in mnemonic:
            word_xpath = f'//*[@id="import-srp__srp-word-{input_number}"]'
            action_performer.send_keys(_DEFAULT_TIMEOUT, word_xpath, word)
            input_number += 1

        import_xpath = '//button[@data-testid="import-srp-confirm"]'
        action_performer.click(_DEFAULT_TIMEOUT, import_xpath)

    @staticmethod
    def __get_mnemonic(driver: WebDriver) -> list[str]:
        action_performer = ActionPerformer(driver)

        secure_wallet_xpath = '//button[@data-testid="secure-wallet-recommended"]'
        action_performer.click(_DEFAULT_TIMEOUT, secure_wallet_xpath)

        recovery_phrase_xpath = '//button[@data-testid="recovery-phrase-reveal"]'
        action_performer.click(_DEFAULT_TIMEOUT, recovery_phrase_xpath)

        mnemonic = []
        for word_number in range(12):
            word_xpath = f'//div[@data-testid="recovery-phrase-chip-{word_number}"]'
            word = action_performer.get_element_text(_DEFAULT_TIMEOUT, word_xpath)
            mnemonic.append(word)

        continue_xpath = '//button[@data-testid="recovery-phrase-next"]'
        action_performer.click(_DEFAULT_TIMEOUT, continue_xpath)

        return mnemonic

    @staticmethod
    def __verify_mnemonic(driver: WebDriver, mnemonic: list[str]) -> None:
        action_performer = ActionPerformer(driver)

        def send_words(numbers: list[int]):
            for number in numbers:
                word = mnemonic[number]
                xpath = f'//input[@data-testid="recovery-phrase-input-{number}"]'
                action_performer.send_keys(_DEFAULT_TIMEOUT, xpath, word)

        send_words([2, 3, 7])
        time.sleep(1)
        continue_xpath = '//button[@data-testid="recovery-phrase-confirm"]'
        action_performer.click(_DEFAULT_TIMEOUT, continue_xpath)

    @staticmethod
    def __create_password(driver: WebDriver, signing_type: _SigningType, password: str) -> None:
        action_performer = ActionPerformer(driver)

        create_password_xpath = '//input[@data-testid="create-password-new"]'
        action_performer.send_keys(_DEFAULT_TIMEOUT, create_password_xpath, password)

        repeat_password_xpath = '//input[@data-testid="create-password-confirm"]'
        action_performer.send_keys(_DEFAULT_TIMEOUT, repeat_password_xpath, password)

        agree_to_terms_xpath = '//input[@data-testid="create-password-terms"]'
        action_performer.click(_DEFAULT_TIMEOUT, agree_to_terms_xpath)

        xpath = ''
        if signing_type == 'import':
            xpath = '//button[@data-testid="create-password-import"]'
        elif signing_type == 'create':
            xpath = '//button[@data-testid="create-password-wallet"]'

        action_performer.click(_DEFAULT_TIMEOUT, xpath)

    @staticmethod
    def __complete(driver: WebDriver) -> None:
        action_performer = ActionPerformer(driver)

        while True:
            try:
                onboarding_xpath = '//button[@data-testid="onboarding-complete-done"]'
                action_performer.click(_DEFAULT_TIMEOUT, onboarding_xpath)
            except (TimeoutException, ElementClickInterceptedException):
                pass
            else:
                break

        next_xpath = '//button[@data-testid="pin-extension-next"]'
        action_performer.click(_DEFAULT_TIMEOUT, next_xpath)

        continue_xpath = '//button[@data-testid="pin-extension-done"]'
        action_performer.click(_DEFAULT_TIMEOUT, continue_xpath)

    def sign_in(self) -> None:
        """
        Authorizes into the metamask
        :return:
        """
        driver = self.driver
        driver.get(self.extension_url)
        signing_type = cast(_SigningType, 'import')
        password = self.password
        self.__agree_to_terms(driver, signing_type)
        self.__enter_mnemonic()
        self.__create_password(driver, signing_type, password)
        self.__complete(driver)

    @classmethod
    def sign_up(
            cls,
            driver: WebDriver,
            password: str,
            extension_id: str = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
    ) -> Self:
        """
        Creates an instance of Metamask by the creating all-new wallet
        For more information about extension IDs go to BrowserExtension documentation
        :param driver: Driver to be interacted with
        :param password: Password for Metamask wallet
        :param extension_id: Extension's'id
        :return: Metamask
        """
        signing_type = cast(_SigningType, 'create')

        driver.get(f'chrome-extension://{extension_id}/home.html')
        cls.__agree_to_terms(driver, signing_type)
        cls.__create_password(driver, signing_type, password)
        mnemonic = cls.__get_mnemonic(driver)
        cls.__verify_mnemonic(driver, mnemonic)
        cls.__complete(driver)
        return cls(driver, password, ' '.join(mnemonic), extension_id)

    def __close_pop_up(self) -> None:
        action_performer = self._action_performer
        if not self.__popup_closed:
            action_performer.click(_DEFAULT_TIMEOUT, '//button[@data-testid="popover-close"]',
                                   ignored_exceptions=TimeoutException)
            self.__popup_closed = True

    def import_account(self, private_key: str) -> None:
        """
        Imports an account using a private key
        :param private_key: A private key of Metamask wallet
        :return: None
        """
        driver = self.driver
        driver.get(self.extension_url)
        action_performer = self._action_performer

        account = Account.from_key(private_key)
        public_key = account.address

        time.sleep(2)

        self.__close_pop_up()
        action_performer.click(_DEFAULT_TIMEOUT, '//button[@data-testid="account-menu-icon"]')
        action_performer.click(_DEFAULT_TIMEOUT, '//*[@id="popover-content"]/div/div/section/div[2]/div/div[2]/div[2]/button')
        action_performer.send_keys(_DEFAULT_TIMEOUT, '//input[@id="private-key-box"]', private_key)
        action_performer.click(_DEFAULT_TIMEOUT, '//button[@data-testid="import-account-confirm-button"]')

        self._private_key = private_key
        self._public_key = public_key
        self._accounts.append(WalletAccount(private_key=private_key, public_key=public_key))

    @handle_in_new_tab()
    def switch_network(self, network: str):
        driver = self.driver
        driver.get(self.extension_url)
        action_performer = self._action_performer

        self.__close_pop_up()

        network_menu_xpath = '//button[contains(@class, "mm-picker-network")]'
        action_performer.click(_DEFAULT_TIMEOUT, network_menu_xpath)

        toogle_xpath = '//label[contains(@class, "toggle-button")]'
        toogle_element = action_performer.get_element(_DEFAULT_TIMEOUT, toogle_xpath)
        if 'off' in toogle_element.get_attribute('class'):
            toogle_element.click()

        network_xpath = f'//div[contains(@class, "multichain-network-list-item__network-name")]//span[contains(text(), "{network}")]'
        action_performer.click(_DEFAULT_TIMEOUT, network_xpath)

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party Metamask connection
        :return: None
        """
        action_performer = self._action_performer

        try:
            password_xpath = '//*[@id="password"]'
            action_performer.send_keys(3, password_xpath, self.password)

            unlock_xpath = '//button[@data-testid="unlock-submit"]'
            action_performer.click(3, unlock_xpath)
        except TimeoutException:
            pass

        original_window = self.driver.current_window_handle
        next_xpath = '//button[@data-testid="page-container-footer-next"]'
        for _ in range(2):
            if original_window not in self.driver.current_window_handle:
                break
            action_performer.click(_DEFAULT_TIMEOUT, next_xpath)

        try:
            action_performer.click(5, next_xpath)
        except NoSuchWindowException:
            pass

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
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
        action_performer = self._action_performer

        scroll_down_xpath = '//i[@aria-label="Scroll down"]'
        action_performer.click(2, scroll_down_xpath, ignored_exceptions=TimeoutException)

        continue_xpath = '//button[@data-testid="page-container-footer-next"]'
        action_performer.click(_DEFAULT_TIMEOUT, continue_xpath)
