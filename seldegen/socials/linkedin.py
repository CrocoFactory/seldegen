import time
from typing import Optional
from selenium.common import TimeoutException, UnableToSetCookieException
from selenium.webdriver.chrome.webdriver import WebDriver
from croco_selenium.decorators import handle_pop_up
from seldegen.abc.base_account import BaseAccount
from seldegen.email import Email
from seldegen.exceptions import InvalidCookiesError
from seldegen.types import Cookies
from croco_selenium import ActionPerformer
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class LinkedIn(BaseAccount):
    """This is a class interacting with LinkedIn"""
    def __init__(
            self,
            driver: WebDriver,
            password: str,
            email: Email,
            cookies: Optional[Cookies] = None,
            two_fa_key: Optional[str] = None
    ):
        """
        The fast way to sign in into a LinkedIn account is specifying cookies
        :param driver: Driver to be interacted with
        :param password: Password of a LinkedIn's account
        :param email: Instance of the Email created from LinkedIn's credentials
        :param cookies: List of cookies
        """
        url = 'https://linkedin.com'
        super().__init__(driver, url, password, email)
        self.__cookies = cookies
        self.__action_performer = ActionPerformer(driver)
        self.__two_key = two_fa_key

    @property
    def cookies(self) -> Cookies | None:
        """
        Returns list of cookies
        :return:
        """
        return self.__cookies

    @property
    def two_fa_key(self) -> str | None:
        return self.__two_key

    def sign_in(self, ignore_cookie_error: bool = False) -> None:
        """
        Authorizes into the LinkedIn
        :return: None
        """
        driver = self.driver
        driver.get('https://www.linkedin.com/')
        cookies = self.cookies
        action_performer = self.__action_performer

        time.sleep(3)
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")

        email_input_xpath = '//input[@id="session_key"]'
        password_xpath = '//input[@id="session_password"]'
        if cookies:
            self._add_cookies(cookies, ignore_cookie_error)
            try:
                action_performer.get_element(5, password_xpath)
            except TimeoutException:
                pass
            else:
                raise InvalidCookiesError(cookies, 'LinkedIn')
        else:
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, email_input_xpath, self.login)
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, password_xpath, self.password)

            submit_xpath = '//button[@type="submit"]'
            action_performer.click(_DEFAULT_TIMEOUT, submit_xpath)
            time.sleep(1)

            if 'unexpected_error' in driver.current_url:
                action_performer.silent_send_keys(_DEFAULT_TIMEOUT, '//input[@id="username"]', self.login)
                action_performer.silent_send_keys(_DEFAULT_TIMEOUT, '//input[@id="password"]', self.password)
                action_performer.click(_DEFAULT_TIMEOUT, '//button[@type="submit"]')
        time.sleep(10)

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party LinkedIn connection
        :return: None
        """
        action_performer = self.__action_performer

        action_performer.silent_send_keys(_DEFAULT_TIMEOUT, '//input[@id="username"]', self.login)

        action_performer.silent_send_keys(_DEFAULT_TIMEOUT, '//input[@id="password"]', self.password)
        action_performer.click(_DEFAULT_TIMEOUT, '//button[@type="submit"]')

        time.sleep(3)

        submit_xpath = '//button[@id="oauth__auth-form__submit-btn"]'
        action_performer.click(_DEFAULT_TIMEOUT, submit_xpath, ignored_exceptions=TimeoutException)

        time.sleep(3)
