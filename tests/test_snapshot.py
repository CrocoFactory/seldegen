import pytest
from typing import Callable
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.dapps.snapshot import Snapshot


@pytest.fixture
def make_snapshot(make_metamask) -> Callable[[WebDriver], Snapshot]:
    def _make_snapshot(driver: WebDriver) -> Snapshot:
        metamask = make_metamask(driver)
        snapshot = Snapshot(driver, metamask)
        snapshot.sign_in()
        return snapshot
    return _make_snapshot


def test_sign_in(make_snapshot, function_driver):
    make_snapshot(function_driver)


def test_vote(make_snapshot, function_driver):
    snapshot = make_snapshot(function_driver)
    function_driver.get('https://snapshot.org/#/timeline?feed=all')

    last_proposal_xpath = "//a[@class='cursor-pointer']"
    proposal_url = snapshot._action_performer.get_element_attribute(15, last_proposal_xpath, 'href')
    snapshot.vote(proposal_url)
