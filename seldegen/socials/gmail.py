from typing import Optional
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from croco_selenium.decorators import handle_in_new_tab
from .google import Google
from seldegen.email import Email
from croco_selenium import ActionPerformer
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class Gmail(Email, Google):
    """
    This is a class interacting with Gmail. It also performs mail retrieving functions
    It's important to note you can't use functions from class Email if you have no permissions to use IMAP
    in your Gmail account. To be able to use those functions you need to configure IMAP access settings before using.
    """
    def __init__(
            self,
            driver: WebDriver,
            login: str,
            password: str,
            recovery_email: Optional[Email] = None
    ):
        """
        :param driver: Driver to be interacted with
        :param login: Login of associated Gmail account
        :param password: Password of associated Gmail account
        :param recovery_email: Recovery email represented as instance of Email
        """
        Google.__init__(self, driver, login, password, recovery_email)
        Email.__init__(self, login, password)
        self.__action_performer = ActionPerformer(driver)

    @handle_in_new_tab()
    def get_last_mail_in_browser(self) -> str:
        """
        Returns content of the last mail in gmail
        :return: str
        """
        driver = self.driver
        driver.get('https://mail.google.com/mail/?ui=html')
        action_performer = self.__action_performer

        confirm_xpath = '//button[@type="submit"][@class="secondary-btn"]'
        action_performer.click(_DEFAULT_TIMEOUT, confirm_xpath, ignored_exceptions=TimeoutException)

        last_mail_xpath = '(//td//span[@class="ts"]/..)[1]'
        action_performer.click(_DEFAULT_TIMEOUT, last_mail_xpath)

        mail_container = action_performer.get_element(_DEFAULT_TIMEOUT, '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody')
        html_content = mail_container.get_attribute("innerHTML")
        return html_content
