from abc import ABC, abstractmethod
from croco_selenium import ActionPerformer
from selenium.common import UnableToSetCookieException
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.email import Email
from typing import Optional
from seldegen.types import Cookies


class BaseAccount(ABC):
    """This is an abstract class whose inheritors interact with socials"""
    def __init__(
            self,
            driver: WebDriver,
            url: str,
            password: str,
            email: Optional[Email] = None,
            login: Optional[str] = None
    ):
        """
        :param driver: Driver to be interacted with
        :param url: URL of a social's logging page
        :param password: Password of a social's account
        :param email: Instance of the Email created from account's credentials
        :param login: Login of a social's account. Most of the time, an email address or username
        are used as the login
        """
        self.__driver = driver
        self.__url = url
        self.__login = email.login if email else login
        self.__password = password
        self.__email = email
        self._action_performer = ActionPerformer(driver)

    def __enter__(self):
        self.sign_in()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sign_out()

    @property
    def driver(self) -> WebDriver:
        """
        Returns a driver to be interacted with
        :return: WebDriver
        """
        return self.__driver

    @property
    def url(self) -> str:
        """
        Returns URL of the social's logging page
        :return: str
        """
        return self.__url

    @property
    def login(self) -> str | None:
        """
        Returns a login of the current social's account.
        Most of the time, an email address or username are used as the login
        :return: str
        """
        return self.__login

    @property
    def password(self) -> str:
        """
        Returns a password of the current social's account
        :return: str
        """
        return self.__password

    @property
    def email(self) -> Email | None:
        """
        Returns an instance of the account's Email

        :return: Email
        """
        return self.__email

    @abstractmethod
    def sign_in(self) -> None:
        """
        Authorizes into the account or opens its main page
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
        Performs the third-party account connection
        :param handles: List of window handles just before opening popup. Ensuring, that pop up will be
                        handled successfully.
        :return: None
        """
        pass

    def _add_cookies(
            self,
            cookies: Cookies,
            ignore_cookie_error: bool = False
    ):
        driver = self.driver
        action_performer = self._action_performer
        if ignore_cookie_error:
            for cookie in cookies:
                try:
                    action_performer.add_cookies(cookie)
                except (UnableToSetCookieException, AssertionError):
                    pass
        else:
            action_performer.add_cookies(cookies)

        driver.refresh()

    def sign_out(self) -> None:
        """
        Logs out from the account
        :return: None
        """
        driver = self.driver
        driver.get(self.url)
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.refresh()
