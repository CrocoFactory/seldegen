import re
import time
import pyotp
import pyperclip
from typing import Optional
from selenium.common import TimeoutException, NoSuchWindowException
from seldegen.email import Email
from seldegen.abc import BaseAccount
from croco_selenium.decorators import handle_pop_up, handle_in_new_tab
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.exceptions import InvalidCodeError, InvalidCredentialsError
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()


class Twitter(BaseAccount):
    """This is a class interacting with Twitter"""

    def __init__(
            self,
            driver: WebDriver,
            password: str,
            email: Email,
            auth_token: Optional[str] = None,
            two_fa_key: Optional[str] = None
    ):
        """
        The fast way to sign in into a Twitter account is specifying authentication token
        :param driver: Driver to be interacted with
        :param password: Password of a Discord's account
        :param email: Instance of the Email created from Twitter's credentials
        :param auth_token: Authentication token
        :param two_fa_key: 2FA Secret key
        """
        url = 'https://twitter.com/'
        super().__init__(driver, url, password, email)
        self.__token = auth_token
        self.__two_fa_key = two_fa_key
        self.__nickname = None
        self.__profile_url = None

    @property
    def token(self) -> str | None:
        """
        Returns authentication token
        :return: str
        """
        return self.__token

    @property
    def two_fa_key(self) -> str | None:
        """
        Returns 2FA authentication secret
        :return: str
        """
        return self.__two_fa_key

    @property
    def nickname(self) -> str | None:
        """
        Returns the nickname of the account
        :return: str
        """
        return self.__nickname

    @property
    def profile_url(self) -> str | None:
        """
        Returns the profile URL of the account
        :return: str
        """
        return self.__profile_url

    def __sign_in_with_token(self):
        driver = self.driver
        action_performer = self._action_performer

        driver.get(self.url)
        action_performer.get_element(_DEFAULT_TIMEOUT, '//body')
        action_performer.add_cookies({
            'name': 'auth_token',
            'value': f'{self.token}',
            'domain': "twitter.com"
        })

        driver.refresh()

        time.sleep(5)

    def __set_nickname_and_url(self):
        action_performer = self._action_performer

        profile_xpath = '//a[@data-testid="AppTabBar_Profile_Link"]'
        profile_url = self.__profile_url = action_performer.get_element_attribute(_DEFAULT_TIMEOUT, profile_xpath, 'href')
        self.__nickname = profile_url.split("/")[-1]

    def sign_in(self) -> None:
        """
        Authorizes into the Twitter
        :return: None
        """
        driver = self.driver
        login = self.login
        password = self.password
        
        action_performer = self._action_performer

        login_input_xpath = "//input[@name='text']"
        if self.token:
            self.__sign_in_with_token()
            try:
                action_performer.get_element(5, login_input_xpath)
            except TimeoutException:
                pass
            else:
                raise InvalidCredentialsError({'auth_token': self.token}, 'Twitter')
        else:
            driver.get('https://twitter.com/i/flow/login')

            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, login_input_xpath, login)

            continue_button_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[' \
                                    '2]/div/div/div/div[6]'

            action_performer.click(_DEFAULT_TIMEOUT, continue_button_xpath)

            password_input_xpath = "//input[@name='password']"
            action_performer.silent_send_keys(_DEFAULT_TIMEOUT, password_input_xpath, password)

            continue_button_xpath = '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[' \
                                    '2]/div/div[1]/div/div/div'
            action_performer.click(_DEFAULT_TIMEOUT, continue_button_xpath)

            try:
                code_input_xpath = '//input[@name="text"]'
                action_performer.get_element(5, code_input_xpath)
            except TimeoutException:
                pass
            else:
                code = self.__get_verifying_code()

                action_performer.silent_send_keys(_DEFAULT_TIMEOUT, code_input_xpath, code)

                submit_button_xpath = '//div[@data-testid="ocfEnterTextNextButton"]'
                action_performer.click(_DEFAULT_TIMEOUT, submit_button_xpath)
                time.sleep(8)

        try:
            is_my_number_xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div/div[2]/div[1]/div/span/span'
            action_performer.click(7, is_my_number_xpath)
        except TimeoutException:
            pass

        self.__set_nickname_and_url()

        try:
            accept_cookie_xpath = '/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div[2]/div[1]/div'
            action_performer.click(2, accept_cookie_xpath)
        except TimeoutException:
            pass

    def __get_verifying_code(self) -> str:
        if key := self.two_fa_key:
            totp = pyotp.TOTP(key, interval=30)
            code = totp.now()
        else:
            time.sleep(5)
            body = self.email.get_mails_by_sender('info@x.com')[-1]
            pattern = r'\b\d{6}\b'
            code = re.search(pattern, body)[0]

        if not code:
            raise InvalidCodeError(code)

        try:
            int(code)
        except ValueError:
            raise InvalidCodeError(code)

        return code

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect(
            self,
            *,
            handles: Optional[list[str]] = None
    ) -> None:
        """
        Performs the third-party Twitter connection
        :return: None
        """
        action_performer = self._action_performer
        action_performer.click(_DEFAULT_TIMEOUT, '//div[@data-testid="OAuth_Consent_Button"]')

    @handle_pop_up(timeout=_DEFAULT_TIMEOUT)
    def connect_v1(self) -> None:
        """
        Performs enabling Twitter V1 API
        :return: None
        """
        action_performer = self._action_performer
        action_performer.click(_DEFAULT_TIMEOUT, '//input[@id="allow"]')

    def post_suggested(self) -> None:
        """
        Posts suggested tweet via pop-up
        :return: None
        """
        action_performer = self._action_performer
        driver = self.driver

        original_window = driver.current_window_handle
        action_performer.switch_to_another_window(_DEFAULT_TIMEOUT)

        tweet_xpath = '//div[@data-testid="tweetButton"]'
        action_performer.click(_DEFAULT_TIMEOUT, tweet_xpath)

        try:
            driver.close()
        except NoSuchWindowException:
            pass

        driver.switch_to.window(original_window)

    @handle_in_new_tab
    def __get_last_tweet(self, url: str) -> str:
        action_performer = self._action_performer
        driver = self.driver

        driver.get(url)

        tweet_xpath = "//article[@data-testid='tweet']"
        tweet_element = action_performer.get_element(_DEFAULT_TIMEOUT, tweet_xpath)
        driver.execute_script("arguments[0].scrollIntoView();", tweet_element)

        share_xpath = "//article[@data-testid='tweet']//div[@role='group']//div[6]"

        action_performer.click(_DEFAULT_TIMEOUT, share_xpath)

        copy_link_xpath = "//div[@data-testid='Dropdown']//div[@role='menuitem'][1]"
        action_performer.click(_DEFAULT_TIMEOUT, copy_link_xpath)

        link = pyperclip.paste().split('?')[0]

        return link

    def get_last_tweet_of(self, nickname: str) -> str:
        """
        Returns the last tweet of the given account
        :param nickname: the nickname of the account
        :return: str
        """
        if '@' in nickname:
            nickname = nickname.split('@')[1]

        url = f'https://twitter.com/{nickname}'
        return self.__get_last_tweet(url)

    def get_last_tweet(self) -> str:
        """
        Returns the last tweet of the current account
        :return: str
        """
        return self.__get_last_tweet(self.profile_url)

    def like_tweet(self, tweet_url: str) -> None:
        """
        Like a tweet by the given url
        :param tweet_url: the url of the tweet
        :return: None
        """
        driver = self.driver
        action_performer = self._action_performer

        driver.get(tweet_url)
        like_xpath = "//article[@data-testid='tweet'][@tabindex='-1']//div[@data-testid='like']"
        action_performer.click(_DEFAULT_TIMEOUT, like_xpath)

    def retweet(self, tweet_url: str) -> None:
        """
        Retweet a tweet by the given url
        :param tweet_url: the url of the tweet
        :return: None
        """
        driver = self.driver
        action_performer = self._action_performer

        driver.get(tweet_url)
        retweet_xpath = "//article[@data-testid='tweet'][@tabindex='-1']//div[@data-testid='retweet']"
        action_performer.click(_DEFAULT_TIMEOUT, retweet_xpath)

        repost_xpath = "//div[@data-testid='Dropdown']//div[@role='menuitem'][1]"
        action_performer.click(_DEFAULT_TIMEOUT, repost_xpath)

    def follow(self, nickname: str) -> None:
        """
        Follow an account by the given nickname
        :param nickname: the nickname of the account
        :return: None
        """
        if '@' in nickname:
            nickname = nickname.split('@')[1]

        action_performer = self._action_performer
        driver = self.driver

        url = f'https://twitter.com/{nickname}'
        driver.get(url)
        follow_xpath = "//div[@data-testid='placementTracking']//div[contains(@data-testid, '-follow')]"
        action_performer.click(_DEFAULT_TIMEOUT, follow_xpath)
