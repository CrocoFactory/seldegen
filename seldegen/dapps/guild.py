import os
import time
from seldegen.abc.dapp import DApp
from selenium.common import TimeoutException
from seldegen.exceptions import InvalidSocialError
from seldegen.socials.discord import Discord
from seldegen.socials.google import Google
from seldegen.abc.wallet import Wallet
from seldegen.socials.twitter import Twitter
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.context import Context

_DEFAULT_TIMEOUT = Context.default_timeout()

GuildSocial = Discord | Google | Twitter


class Guild(DApp):
    def __init__(self, driver: WebDriver, wallet: Wallet):
        url = 'https://guild.xyz/'
        super().__init__(driver, url, wallet)
        self.__communities = []

    def communities(self) -> list[str]:
        return self.__communities.copy()

    def sign_in(self) -> None:
        driver = self.driver
        wallet = self.wallet
        action_performer = self._action_performer

        driver.get(self.url)

        connect_xpath = '//button[@data-test="connect-wallet-button"]'
        action_performer.click(_DEFAULT_TIMEOUT, connect_xpath)

        metamask_xpath = "//div[contains(@class, 'chakra-modal__body')]//button[2]"
        action_performer.click(_DEFAULT_TIMEOUT, metamask_xpath)

        wallet.connect()

        self.__verify_wallet()
        time.sleep(3)

    def __verify_wallet(self) -> None:
        wallet = self.wallet

        verify_xpath = "//button[@data-test='verify-address-button']"
        action_performer = self._action_performer

        action_performer.click(_DEFAULT_TIMEOUT, verify_xpath)
        time.sleep(20)

        wallet.confirm()

    def join_communities(
            self,
            communities: list[str] | str
    ) -> None:
        driver = self.driver
        action_performer = self._action_performer
        if isinstance(communities, str):
            communities = [communities]

        join_xpath = '//span[normalize-space()="Join Guild to get roles"]'
        check_access_xpath = '//span[normalize-space()="Check access to join"]'
        for community in communities:
            community_url = os.path.join(self.url, community)
            driver.get(community_url)
            action_performer.click(_DEFAULT_TIMEOUT, join_xpath)
            action_performer.click(_DEFAULT_TIMEOUT, check_access_xpath)
            time.sleep(12)
            self.__communities.append(community)

    def connect_accounts(self, accounts: list[GuildSocial]) -> None:
        """DON'T USE THIS FUNCTION"""
        driver = self.driver
        action_performer = self._action_performer

        our_guild_url = os.path.join(self.url, 'our-guild')
        driver.get(our_guild_url)

        join_xpath = '//span[normalize-space()="Join Guild to get roles"]'
        action_performer.click(_DEFAULT_TIMEOUT, join_xpath)

        for account in accounts:
            if isinstance(account, Discord):
                xpath = '//*[contains(@id, "chakra-modal--body")]/div[2]/div[5]/button'
            elif isinstance(account, Google):
                xpath = '//*[contains(@id, "chakra-modal--body")]/div[2]/div[4]/button'
            elif isinstance(account, Twitter):
                xpath = '//*[contains(@id, "chakra-modal--body")]/div[2]/div[7]/button'
                v1_xpath = '//*[contains(@id, "chakra-modal--body")]/div[2]/div[8]/button'
                action_performer.click(_DEFAULT_TIMEOUT, v1_xpath)
                account.connect_v1()
            else:
                raise InvalidSocialError(account, 'Guild')

            action_performer.click(_DEFAULT_TIMEOUT, xpath)
            account.connect()

        check_access_xpath = '//span[normalize-space()="Check access to join"]'
        while True:
            try:
                action_performer.click(_DEFAULT_TIMEOUT, check_access_xpath)
            except TimeoutException:
                pass
            else:
                break
        time.sleep(7)
