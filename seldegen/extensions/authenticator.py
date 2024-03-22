import time
from croco_selenium import handle_in_new_tab, ActionPerformer
from seldegen.types import AuthenticationAccount
from seldegen.abc.browser_extension import BrowserExtension
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class Authenticator(BrowserExtension):
    """
    This is a browser extension receiving authentication codes by 2FA secret keys.
    https://chrome.google.com/webstore/detail/authenticator/bhghoamapcdpbohphigoooaddinpkbai

    Usage
    ----------
        facebook_account = ...
        authenticator = Authenticator(driver)
        authenticator.sign_in()
        auth_account = authenticator.add_account(facebook_account.auth_key, 'facebook1')

        facebook_email = Email(facebook_account.email.login, facebook_account.email.password)
        facebook = Facebook(driver, facebook_account.password, facebook_email, auth_account, authenticator)
    """
    def __init__(self, driver: WebDriver, extension_id='cgjkoiocbgmhaicgbgpeomlaffbaheil'):
        """
        :param driver: Driver to be interacted with
        :param extension_id: Extension's'id
        """
        extension_url = ['chrome-extension://', '/view/popup.html']
        super().__init__(driver, extension_url, extension_id)

        self.__accounts = []
        self.__account_number = 0
        self.__clear_data_url = ['chrome-extension://', '/view/options.html']
        self.__action_performer = ActionPerformer(driver)

    @property
    def accounts(self) -> list[AuthenticationAccount]:
        """
        Returns a list of accounts stored in the extension
        :return: list[AuthenticationAccount]
        """
        return self.__accounts

    @property
    def account_number(self) -> int:
        """
        Returns a number of accounts stored in the extension
        :return: int
        """
        return self.__account_number

    @property
    def clear_data_url(self) -> str:
        """
        Returns the URL where accounts' data is to be cleared
        :return: str
        """
        return self._get_full_url(self.__clear_data_url)

    def __clear_data(self) -> None:
        driver = self.driver
        action_performer = self.__action_performer

        driver.get(self.clear_data_url)

        checkbox_xpath = '//*[@id="checkbox"]'
        action_performer.click(_DEFAULT_TIMEOUT, checkbox_xpath)

        time.sleep(1)

        clear_data_xpath = '/html/body/div/button"]'
        action_performer.click(_DEFAULT_TIMEOUT, clear_data_xpath)

        self.__accounts = []
        self.__account_number = 0

        driver.get(self.extension_url)

    def add_account(self, secret_key: str) -> AuthenticationAccount:
        """
        Returns and creates an instance of account receiving codes corresponding to 2FA secret key
        :param secret_key: 2FA secret key
        :type secret_key: str
        :return: AuthenticationAccount

        Usage
        ----------
            auth_account = authenticator.add_account(facebook_account.auth_key, 'facebook1')

            facebook_email = Email(facebook_account.email.login, facebook_account.email.password)
            facebook = Facebook(driver, facebook_account.password, facebook_email, auth_account, authenticator)
        """
        action_performer = self.__action_performer

        edit_xpath = '//*[@id="i-edit"]'
        action_performer.click(_DEFAULT_TIMEOUT, edit_xpath)

        plus_xpath = '//*[@id="i-plus"]'
        action_performer.click(_DEFAULT_TIMEOUT, plus_xpath)

        add_xpath = '//*[@id="infoContent"]/button[2]'
        action_performer.click(_DEFAULT_TIMEOUT, add_xpath)

        secret_key_input = '//*[@id="infoContent"]/div[2]/input'
        action_performer.send_keys(_DEFAULT_TIMEOUT, secret_key_input, secret_key)

        confirm_xpath = '//*[@id="infoContent"]/button'
        action_performer.click(_DEFAULT_TIMEOUT, confirm_xpath)

        account = AuthenticationAccount(self.account_number, secret_key)
        self.__accounts.append(account)
        self.__account_number += 1
        return account

    @handle_in_new_tab()
    def get_code(self, account: AuthenticationAccount) -> str:
        """
        Returns a code corresponding to authenticator accounts
        :param account: Authenticator's account receiving corresponding code
        :return: str
        """
        driver = self.driver
        action_performer = self.__action_performer

        driver.get(self.extension_url)

        code_field_xpath = '//*[contains(@class, "code")]'
        code_fields = action_performer.get_elements(_DEFAULT_TIMEOUT, code_field_xpath)

        code_field = code_fields[account.id]

        code = code_field.text
        return code

    def sign_in(self) -> None:
        """
        Opens the extension's page
        :return: None
        """
        driver = self.driver
        driver.get(self.extension_url)
