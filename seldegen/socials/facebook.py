import pyotp
import time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, UnableToSetCookieException
from croco_selenium.decorators import handle_pop_up
from croco_selenium import ActionPerformer
from seldegen.abc.base_account import BaseAccount
from seldegen.email import Email
from typing import Optional
from seldegen.types import Cookies
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class Facebook(BaseAccount):
    """This is a class interacting with Facebook"""
    def __init__(
            self,
            driver: WebDriver,
            password: str,
            email: Email,
            two_fa_key: Optional[str] = None,
            cookies: Optional[Cookies] = None
    ):
        """
        The fast way to sign in into a Facebook account is specifying cookies
        :param driver: Driver to be interacted with
        :param password: Password of a Facebook's account
        :param email: Instance of the Email created from Facebook's credentials
        :param two_fa_key: 2FA Secret key
        """
        url = 'https://facebook.com'
        super().__init__(driver, url, password, email)
        self.__two_fa_key = two_fa_key
        self.__action_performer = ActionPerformer(driver)
        self.__cookies = cookies

    @property
    def two_fa_key(self) -> str | None:
        """
        Returns 2FA authentication secret
        :return: str
        """
        return self.__two_fa_key

    def sign_in(self, ignore_cookie_error: bool = False) -> None:
        """
        Authorizes into the Facebook
        :return: None
        """
        driver = self.driver
        login = self.login
        password = self.password
        action_performer = self.__action_performer

        driver.get('https://www.facebook.com/login')

        cookie_accept_xpath = '/html/body/div[3]/div[2]/div/div/div/div/div[4]/button[2]'
        action_performer.click(5, cookie_accept_xpath, ignored_exceptions=TimeoutException)

        if cookies := self.__cookies:
            self._add_cookies(cookies, ignore_cookie_error)
        else:
            login_input_xpath = "//input[@id='email']"
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, login_input_xpath, login)

            password_input_xpath = "//input[@id='pass']"
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, password_input_xpath, password)

            continue_button_xpath = "//button[@id='loginbutton']"
            action_performer.click(_DEFAULT_TIMEOUT, continue_button_xpath)

            if self.two_fa_key:
                self.__authenticate()

        time.sleep(7)

    def __authenticate(self) -> None:
        action_performer = self.__action_performer

        code_input_xpath = "//input[@id='approvals_code']"

        totp = pyotp.TOTP(self.two_fa_key, interval=30)

        two_factor_code = totp.now()

        action_performer.silent_send_keys(_DEFAULT_TIMEOUT, code_input_xpath, two_factor_code)

        action_performer.click(_DEFAULT_TIMEOUT, "//button[@id='checkpointSubmitButton']")
        action_performer.click(_DEFAULT_TIMEOUT, "//input[@value='dont_save']")
        action_performer.click(_DEFAULT_TIMEOUT, "//button[@id='checkpointSubmitButton']")

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party Facebook connection
        :return: None
        """
        action_performer = self.__action_performer

        body = action_performer.get_element(_DEFAULT_TIMEOUT, '//body')
        time.sleep(6)
        try:
            complete_button_xpath = '//div[@role="button" and @aria-label and not(@aria-disabled="true") and not(@aria-hidden="true")]'
            button = body.find_elements(By.XPATH, complete_button_xpath)[-2]
            button.click()
        except TimeoutException:
            try:
                complete_button_xpath = '/html/body/div[1]/div/div/div/div/div/div/div/div[1]/div[3]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div[1]/div/div/div/div/div/div[1]'
                button = action_performer.get_elements(_DEFAULT_TIMEOUT, complete_button_xpath)[-2]
                button.click()
            except TimeoutException:
                pass
