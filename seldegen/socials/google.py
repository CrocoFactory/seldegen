import re
import time
from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from croco_selenium.decorators import handle_pop_up, handle_in_new_tab
from seldegen.abc.base_account import BaseAccount
from seldegen.email import Email
from croco_selenium import ActionPerformer
from seldegen.context import Context


_DEFAULT_TIMEOUT = Context.default_timeout()


class Google(BaseAccount):
    """This is class interacting with Google"""
    def __init__(
            self,
            driver: WebDriver,
            gmail: str,
            password: str,
            recovery_email: Optional[Email] = None
    ):
        """
        :param driver: Driver to be interacted with
        :param gmail: Login of associated Gmail account
        :param password: Password of associated Gmail account
        :param recovery_email: Recovery email represented as instance of Email
        """
        url = 'https://myaccount.google.com/'
        email = Email(gmail, password, 'imap.gmail.com')
        super().__init__(driver, url, password, email)
        self.__action_performer = ActionPerformer(driver)
        self.__recovery_email = recovery_email

    @handle_in_new_tab()
    def __enter__(self):
        self.sign_in()
        return self

    @handle_in_new_tab()
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sign_out()

    @property
    def recovery_email(self) -> Email:
        return self.__recovery_email

    def sign_in(self) -> None:
        """
        Authorizes into the Google
        :return: None
        """
        driver = self.driver
        login = self.login
        password = self.password
        action_performer = self.__action_performer

        driver.get('https://www.google.com/account/about/')

        start_button_xpath = "(//div[contains(@class, 'h-c-header__cta')]//a)[2]"
        action_performer.click(_DEFAULT_TIMEOUT, start_button_xpath)

        email_xpath = '//input[@type="email"]'
        action_performer.silent_send_keys(_DEFAULT_TIMEOUT, email_xpath, login)

        continue_button_xpath = '//div[@id="identifierNext"]'
        action_performer.click(_DEFAULT_TIMEOUT, continue_button_xpath)

        password_input_xpath = '//input[@type="password"]'
        action_performer.silent_send_keys(_DEFAULT_TIMEOUT, password_input_xpath, password)

        continue_button_xpath = '//div[@id="passwordNext"]'
        action_performer.click(_DEFAULT_TIMEOUT, continue_button_xpath)

        try:
            get_code_xpath = '(//div[@data-action="selectchallenge"])[1]'
            action_performer.click(5, get_code_xpath)
        except TimeoutException:
            pass
        else:
            input_xpath = '//input[@type="tel"]'
            time.sleep(7)
            mail = self.recovery_email.get_last_mail()
            pattern = r'\b\d{6}\b'
            code = re.findall(pattern, re.findall(pattern, mail)[0])[0]

            action_performer.send_keys(_DEFAULT_TIMEOUT, input_xpath, code)

            continue_button_xpath = '//div[@id="idvpreregisteredemailNext"]'
            action_performer.click(_DEFAULT_TIMEOUT, continue_button_xpath)

        time.sleep(3)

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None: 
        """
        Performs the third-party Google connection
        :return: None
        """
        action_performer = self.__action_performer
        action_performer.click(_DEFAULT_TIMEOUT, '//div[@data-identifier]/..')

        time.sleep(5)

    def sign_out(self) -> None:
        """
        Logs out from the Google
        :return: None
        """
        super().sign_out()
        driver = self.driver
        driver.get('https://www.google.com/account/about/')
        action_performer = self.__action_performer

        start_button_xpath = '/html/body/header/div[1]/div[5]/ul/li[2]/a'
        action_performer.click(_DEFAULT_TIMEOUT, start_button_xpath)

        removing_mode_xpath = '//*[@id="view_container"]/div/div/div[2]/div/div[' \
                              '1]/div/form/span/section/div/div/div/div/ul/li[3]/div'
        action_performer.click(_DEFAULT_TIMEOUT, removing_mode_xpath)

        remove_account_xpath = '//*[@id="view_container"]/div/div/div[2]/div/div[' \
                               '1]/div/form/span/section/div/div/div/div[1]/ul/li[1]/div/div[2]'
        action_performer.click(_DEFAULT_TIMEOUT, remove_account_xpath)

        submit_button_xpath = '//*[@id="yDmH0d"]/div[4]/div/div[2]/div[3]/div[1]'

        try:
            action_performer.click(_DEFAULT_TIMEOUT, submit_button_xpath)
        except TimeoutException:
            submit_button_xpath = '//*[@id="yDmH0d"]/div[5]/div/div[2]/div[3]/div[1]'
            action_performer.click(_DEFAULT_TIMEOUT, submit_button_xpath)

        time.sleep(4)
