import os
from typing import Callable
import pytest
from croco_selenium import ActionPerformer
from dotenv import dotenv_values
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from adspower import AdsPower
from seldegen import Capmonster, Metamask, Twitter, Email, Discord

PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))
EXTENSION_PATHS = os.path.join(PACKAGE_PATH, 'extensions')

METAMASK_PATH = os.path.join(EXTENSION_PATHS, 'metamask.crx')
CAPMONSTER_PATH = os.path.join(EXTENSION_PATHS, 'capmonster.crx')
TEST_BROWSER = dotenv_values(".env")['TEST_BROWSER']


def _get_driver() -> WebDriver | AdsPower:
    if TEST_BROWSER == 'adspower' or not TEST_BROWSER:
        group_id = AdsPower.query_group(group_name='test')['group_id']
        adspower = AdsPower.create_profile(group_id=group_id)
        adspower.update_user_agent(
            'Mozilla/5.0 (Linux; Android 10; SM-A750FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36 OPR/61.1.3076.56625')
        adspower.get_driver()
        adspower.close_tabs()
        return adspower
    elif TEST_BROWSER == 'chrome':
        options = Options()
        options.add_extension(METAMASK_PATH)
        options.add_extension(CAPMONSTER_PATH)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--start-maximized")
        driver = WebDriver(options=options)
        driver.get('https://google.com')
        ActionPerformer(driver).close_tabs()
        return driver
    else:
        raise ValueError("Unsupported browser for test")


@pytest.fixture(scope="session")
def session_driver() -> WebDriver:
    profile_or_driver = _get_driver()
    # CaptchaSolver.set_api_key(dotenv_values(".env")['TWOCAPTCHA_API_KEY'])

    if TEST_BROWSER == 'adspower' or not TEST_BROWSER:
        driver = profile_or_driver.driver

        yield driver
        profile_or_driver.quit()
    else:
        yield profile_or_driver

    profile_or_driver.quit()


@pytest.fixture(scope="function")
def function_driver(credentials) -> WebDriver:
    profile_or_driver = _get_driver()
    # CaptchaSolver.set_api_key(dotenv_values(".env")['TWOCAPTCHA_API_KEY'])

    if TEST_BROWSER == 'adspower' or not TEST_BROWSER:
        driver = profile_or_driver.driver
        yield driver
    else:
        yield profile_or_driver

    profile_or_driver.quit()


@pytest.fixture(scope="session")
def credentials() -> dict[str, str]:
    return dotenv_values(".env")


@pytest.fixture(scope="function")
def make_capmonster(credentials) -> Callable[[WebDriver], Capmonster]:
    def _make_capmonster(driver: WebDriver) -> Capmonster:
        capmonster = Capmonster(driver, credentials['CAPMONSTER_API_KEY'])
        capmonster.sign_in()
        return capmonster

    return _make_capmonster


@pytest.fixture(scope="function")
def make_metamask(credentials) -> Callable[[WebDriver], Metamask]:
    def _make_wallet(driver: WebDriver) -> Metamask:
        metamask = Metamask(driver, 'ToTheMoon123', credentials['TEST_MNEMONIC'])
        metamask.sign_in()
        return metamask

    return _make_wallet


@pytest.fixture(scope="function")
def make_twitter(credentials) -> Callable[[WebDriver], Twitter]:
    def _make_twitter(driver: WebDriver) -> Twitter:
        email = Email(credentials['TWITTER_EMAIL'], credentials['TWITTER_EMAIL_PASSWORD'])
        twitter = Twitter(driver, credentials['TWITTER_PASSWORD'], email, credentials.get('TWITTER_AUTH_TOKEN'),
                          credentials.get('TWITTER_AUTH_SECRET'))
        twitter.sign_in()
        return twitter

    return _make_twitter


@pytest.fixture(scope="function")
def make_discord(credentials) -> Callable[[WebDriver], Discord]:
    def _make_discord(driver: WebDriver) -> Discord:
        email = Email(credentials['DISCORD_EMAIL'], credentials['DISCORD_EMAIL_PASSWORD'])
        discord = Discord(driver, credentials['DISCORD_EMAIL_PASSWORD'], email, credentials.get('DISCORD_AUTH_TOKEN'))
        discord.sign_in()
        return discord
    return _make_discord
