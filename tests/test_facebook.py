import json
import pytest
from typing import Callable
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen import Facebook, Email


@pytest.fixture
def make_facebook(credentials) -> Callable[[WebDriver], Facebook]:
    def _make_facebook(driver: WebDriver) -> Facebook:
        email = Email(credentials['FACEBOOK_EMAIL'], credentials['FACEBOOK_EMAIL_PASSWORD'])
        cookies = json.loads(credentials.get('FACEBOOK_COOKIES'))
        facebook = Facebook(
            driver,
            credentials['FACEBOOK_PASSWORD'],
            email,
            credentials.get('FACEBOOK_AUTH_SECRET'),
            cookies
        )
        facebook.sign_in()
        return facebook
    return _make_facebook


def test_sign_in(make_facebook, function_driver):
    make_facebook(function_driver)
