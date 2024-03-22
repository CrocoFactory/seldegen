import time
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from croco_selenium import handle_pop_up, ActionPerformer
from seldegen.abc.base_account import BaseAccount
from seldegen.email import Email
from seldegen.context import Context
from seldegen.captcha_waiter import CaptchaWaiter, CaptchaType
from typing import Optional
from seldegen.exceptions import InvalidCredentialsError

_DEFAULT_TIMEOUT = Context.default_timeout()


class Discord(BaseAccount):
    """This is a class interacting with Discord"""
    def __init__(self, driver: WebDriver, password: str, email: Email, token: Optional[str] = None):
        """
        The fast way to sign in into a Discord account is specifying authentication token
        :param driver: Driver to be interacted with
        :param password: Password of a Discord's account
        :param email: Instance of the Email created from Discord's credentials
        :param token: Authentication token
        """
        url = 'https://discord.com'
        super().__init__(driver, url, password, email)
        self.__token = token
        self.__action_performer = ActionPerformer(driver)

    @property
    def token(self) -> str | None:
        """
        Returns authentication token
        :return: str
        """
        return self.__token

    def __enter_credentials(self) -> None:
        action_performer = self.__action_performer

        action_performer.silent_send_keys(5, '//input[@name="email"]', self.login)
        action_performer.silent_send_keys(5, '//input[@name="password"]', self.password)
        action_performer.click(5, '//button[@type="submit"]')

    def __sign_in_with_token(self) -> None:
        driver = self.driver
        action_performer = self.__action_performer 

        driver.get('https://discord.com')
        action_performer.get_element(_DEFAULT_TIMEOUT, '//body')

        js = """function login() {
                               setInterval(() => {
                                 let i = `"%s"`
                                 document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = i
                               }, 50);
                               setTimeout(() => {
                                 location.reload();
                               }, 2500);
                            }
                            login()
                            """ % self.token
        driver.execute_script(js)
        driver.refresh()
        attribute = action_performer.get_element_attribute(_DEFAULT_TIMEOUT, '//a[@data-track="login"]', 'data-track-nav')
        if attribute == 'login':
            raise InvalidCredentialsError({'auth_token': self.token}, 'Discord')

    def sign_in(self) -> None:
        """
        Authorizes into the Discord. If you have no an authentication token or don't pass it and log in from a
        different proxy than the last time you logged in, you need to use Capmonster or another captcha-solving tool.
        :return: None
        """
        driver = self.driver
        action_performer = self.__action_performer

        if self.token:
            self.__sign_in_with_token()
            return

        driver.get('https://discord.com/login')
        self.__enter_credentials()

        try:
            CaptchaWaiter.wait_for_solving(driver, CaptchaType.H_CAPTCHA, 30)
        except TimeoutException:
            pass

        verifying_urls = self.email.search_content(r'https:\/\/click\.discord\.com\/ls\/click\?upn=[^\s/$.?#].[^\s]*')
        if verifying_urls is not None:
            verifying_url = verifying_urls[-2]
            driver.get(verifying_url)

            submit_button_xpath = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div/div/section/div[2]/button'
            action_performer.click(_DEFAULT_TIMEOUT, submit_button_xpath)

            try:
                self.__enter_credentials()
            except TimeoutException:
                pass

        time.sleep(5)

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party Discord connection
        :return: None
        """
        action_performer = self.__action_performer

        connect_button_xpath = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div/div/div/div/div[2]/button[2]'
        action_performer.click(_DEFAULT_TIMEOUT, connect_button_xpath)
