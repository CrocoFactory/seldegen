import re
from abc import ABC, abstractmethod
from selenium.webdriver.chrome.webdriver import WebDriver


class BrowserExtension(ABC):
    def __init__(self, driver: WebDriver, extension_url: list[str], extension_id: str):
        """
        This is an abstract class whose inheritors interact with browser extensions

        It's important to note how to pass extension_url and extension_id.
        Every extension url exists in chrome-extension://{EXTENSION_ID}{MAIN_PAGE_URL} format
        To get this url you need to open the extension's popup and check its page source, there you find URL of this
        popup.

        For instance, take the following link:
        chrome-extension://cgjkoiocbgmhaicgbgpeomlaffbaheil/view/popup.html

        And turn it into this
        class Authenticator(BrowserExtension):
            extension_url = ['chrome-extension://', '/view/popup.html']
            extension_id = 'cgjkoiocbgmhaicgbgpeomlaffbaheil'
            super().__init__(driver, extension_url, extension_id)

        Most of the extension have different extension IDs, depending on the browser you use. Default IDs of
        built-in extensions are provided for using in Chrome.

        :param driver: Driver to be interacted with
        :param extension_url: Parts of extension's url provided as ['chrome-extension://', main_page_url].
        :param extension_id: Extension's'id
        """
        self.__driver = driver
        self.__extension_url = extension_url
        self.__extension_id = extension_id

    @property
    def driver(self) -> WebDriver:
        """
        Returns a driver to be interacted with
        :return: WebDriver
        """
        return self.__driver

    @property
    def extension_url(self) -> str:
        """
        Returns the popup's URL according to the specified extension_id
        :return: str
        """
        full_url = self.__extension_url.copy()
        full_url.insert(1, self.__extension_id)
        return ''.join(full_url)

    @property
    def extension_id(self) -> str:
        """
        Returns an extension id

        Most of the extension have different extension IDs, depending on the browser you use. Default IDs of
        built-in extensions are provided for using in AdsPower. Even though AdsPower's SunBrowser is Chrome-based,
        it has different extension IDs from Google Chrome. If you don't use AdsPower API to get and interact with its
        driver, you need to change the ID of specific extension on your own.
        :return: str
        """
        return self.__extension_id

    @extension_id.setter
    def extension_id(self, value: str) -> None:
        if len(value) == 32 and not bool(re.search(r'\d', value)):
            self.__extension_id = value

    def _get_full_url(self, url: list[str]) -> str:
        full_url = url.copy()
        full_url.insert(1, self.__extension_id)
        return ''.join(full_url)

    @abstractmethod
    def sign_in(self) -> None:
        """
        Authorizes into the extension or opens its main page
        :return:
        """
        raise NotImplementedError("Authorization is not implemented for this class.")
