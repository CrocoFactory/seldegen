import base64
import json
import time

import pytest
from typing import Callable
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen import GitHub, Email


@pytest.fixture
def make_github(credentials) -> Callable[[WebDriver], GitHub]:
    def _make_github(driver: WebDriver) -> GitHub:
        email = Email(credentials['GITHUB_EMAIL'], credentials['GITHUB_EMAIL_PASSWORD'])
        base_cookies = base64.b64decode(credentials['GITHUB_COOKIES']).decode('utf-8')
        cookies = json.loads(base_cookies) if base_cookies else None
        github = GitHub(
            driver,
            credentials['GITHUB_PASSWORD'],
            email,
            cookies
        )
        github.sign_in(True)
        return github
    return _make_github


def test_sign_in(make_github, function_driver):
    make_github(function_driver)
    time.sleep(30)
