import re
import time
from typing import Optional

from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from croco_selenium.decorators import handle_pop_up
from croco_selenium import ActionPerformer
from seldegen.abc.base_account import BaseAccount
from seldegen.email import Email
from functools import singledispatchmethod
from seldegen.context import Context
from .gmail import Gmail
from seldegen.types import Cookies
from ..exceptions import InvalidCookiesError

_DEFAULT_TIMEOUT = Context.default_timeout()


class GitHub(BaseAccount):
    """This is a class interacting with GitHub"""
    def __init__(
            self,
            driver: WebDriver,
            password: str,
            email: Email,
            cookies: Optional[Cookies] = None
    ):
        """
        :param driver: Driver to be interacted with
        :param password: Password of a GitHub's account
        :param email: Instance of the Email created from GitHub's credentials
        """
        url = 'https://github.com'
        super().__init__(driver, url, password, email)
        self.__action_performer = ActionPerformer(driver)
        self.__cookies = cookies

    @property
    def cookies(self) -> Cookies | None:
        return self.__cookies

    def sign_in(self, ignore_cookie_error: bool = False) -> None:
        """
        Authorizes into the GitHub
        :return: None
        """
        driver = self.driver
        driver.get('https://github.com/login')
        action_performer = self.__action_performer
        cookies = self.cookies

        email_xpath = '//input[@id="login_field"]'
        password_xpath = '//input[@id="password"]'
        if cookies:
            self._add_cookies(cookies, ignore_cookie_error)

            try:
                action_performer.get_element(5, password_xpath)
            except TimeoutException:
                pass
            else:
                raise InvalidCookiesError(cookies, 'GitHub')
        else:
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, email_xpath, self.email.login)
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, password_xpath, self.password)

            action_performer.click(_DEFAULT_TIMEOUT, '//input[@type="submit"]')

            code_input_xpath = '//input[@type="text"]'
            try:
                action_performer.get_element(_DEFAULT_TIMEOUT, code_input_xpath)
            except TimeoutException:
                pass
            else:
                time.sleep(5)
                code = self.__parse_code(self.email)

                action_performer.silent_send_keys(_DEFAULT_TIMEOUT, code_input_xpath, code)

        time.sleep(3)

    @singledispatchmethod
    def __parse_code(self, email) -> str:
        raise NotImplementedError("Parsing isn't implemented for this email type")

    @__parse_code.register(Gmail)
    def __parse_gmail(self, email: Gmail) -> str:
        with email as gmail:
            mail_content = gmail.get_last_mail_in_browser()
            pattern = r"Verification code: (\d+)"
            code = re.search(pattern, mail_content).group(1)
        return code

    @__parse_code.register(Email)
    def __parse_email(self, email: Email) -> str:
        mail_content = email.get_last_mail()
        pattern = r"Verification code: (\d+)"
        code = re.search(pattern, mail_content).group(1)
        return code

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party GitHUb connection
        :return: None
        """
        action_performer = self.__action_performer

        action_performer.click(_DEFAULT_TIMEOUT, '//button[@data-octo-click="oauth_application_authorization"]')
        time.sleep(2)
