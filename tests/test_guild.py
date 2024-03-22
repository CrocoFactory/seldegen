import pytest
from typing import Callable
from selenium.webdriver.chrome.webdriver import WebDriver

from seldegen import Guild, Metamask


@pytest.fixture()
def make_guild(credentials, make_metamask, make_capmonster) -> Callable[[WebDriver, bool], Guild]:
    def _make_guild(driver: WebDriver, new_wallet: bool = False) -> Guild:
        if new_wallet:
            wallet = Metamask.sign_up(driver, 'toTheMoon123')
        else:
            wallet = make_metamask(driver)
        make_capmonster(driver)
        guild = Guild(driver, wallet)
        guild.sign_in()
        return guild

    return _make_guild


def test_sign_in(function_driver, make_guild):
    make_guild(function_driver, True)


def test_join_communities(function_driver, make_guild):
    guild = make_guild(function_driver, True)
    guild.join_communities('zksync-era')
