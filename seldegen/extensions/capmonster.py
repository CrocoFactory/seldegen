import time
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.abc.browser_extension import BrowserExtension
from croco_selenium import ActionPerformer
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class Capmonster(BrowserExtension):
    """
    This is a browser extension solves many kinds of captcha automatically
    https://chrome.google.com/webstore/detail/capmonster-cloud-%E2%80%94-automa/pabjfbciaedomjjfelfafejkppknjleh
    """
    def __init__(
            self,
            driver: WebDriver,
            api_key: str,
            extension_id='pabjfbciaedomjjfelfafejkppknjleh'
    ):
        """
        :param driver: Driver to be interacted with
        :param api_key: API key from Capmonster
        :param extension_id: Extension's'id
        """
        extension_url = ['chrome-extension://', '/popup.html']
        super().__init__(driver, extension_url, extension_id)
        self.__api_key = api_key
        self.__action_performer = ActionPerformer(driver)

    @property
    def api_key(self) -> str:
        """
        Returns API key from Capmonster
        :return: str
        """
        return self.__api_key

    def sign_in(self) -> None:
        """
        Opens extension and enters API Key
        :return: None
        """
        driver = self.driver
        action_performer = self.__action_performer

        driver.get(self.extension_url)

        enable_extension_xpath = '//button[@role="switch"]'
        enable_extension = action_performer.get_element(_DEFAULT_TIMEOUT, enable_extension_xpath)

        if enable_extension.get_attribute("aria-checked") == 'false':
            enable_extension.click()

        api_key_xpath = '//input[@placeholder="Enter API key"]'
        api_key_input = action_performer.get_element(_DEFAULT_TIMEOUT, api_key_xpath)

        if api_key_input.get_attribute("value") != self.api_key:
            api_key_input.clear()
            time.sleep(1)
            api_key_input.send_keys(self.api_key)

            submit_button = '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[2]/button'
            action_performer.click(_DEFAULT_TIMEOUT, submit_button)
    