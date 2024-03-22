from faker import Faker
from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen import Wallet, DApp


class Lens(DApp):
    def __init__(
            self,
            driver: WebDriver,
            wallet: Wallet
    ):
        url = 'https://www.lens.xyz/mint'
        super().__init__(driver, url, wallet)

    def sign_in(self) -> None:
        driver = self.driver
        action_performer = self._action_performer
        wallet = self.wallet
        timeout = 15

        driver.get(self.url)

        connect_xpath = '//li//button[@data-variant]'
        action_performer.click(timeout, connect_xpath)

        metamask_xpath = '//div[@role="dialog"]//button[@type="button"]//span[text()="MetaMask"]/..'
        handles = driver.window_handles
        action_performer.click(timeout, metamask_xpath)

        wallet.connect(handles=handles)

    def mint_nickname(
            self,
            nickname: Optional[str] = None
    ) -> None:
        driver = self.driver
        action_performer = self._action_performer
        wallet = self.wallet
        timeout = 15

        if not nickname:
            fake = Faker()
            number = fake.date().replace('-', '')[:5]
            nickname = f'{fake.user_name()}{number}'

        nickname_input_xpath = '//input[@type="search"]'
        action_performer.silent_send_keys(timeout, nickname_input_xpath, nickname)

        confirm_xpath = '//input[@type="search"]/../../../..//button[@data-variant]'
        action_performer.click(timeout, confirm_xpath)

        pay_with_crypto_xpath = '//button[@role="tab"][@aria-selected="false"]'
        action_performer.click(timeout, pay_with_crypto_xpath)

        mint_xpath = '//div[@role="tabpanel"][not (@hidden)]//button[@data-variant]'
        handles = driver.window_handles

        action_performer.click(timeout, mint_xpath)
        wallet.confirm(handles=handles)
        
