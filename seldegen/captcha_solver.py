from typing import ClassVar
from selenium.webdriver.chrome.webdriver import WebDriver
from twocaptcha import TwoCaptcha
from seldegen.types import CaptchaType


class CaptchaSolver:
    api_key: ClassVar[str] = None
    __solver: ClassVar[TwoCaptcha] = None

    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        cls.api_key = api_key
        cls.__solver = TwoCaptcha(api_key)

    @classmethod
    def solve_recaptcha(
            cls,
            driver: WebDriver,
            site_key: str,
            url: str
    ) -> None:
        solver = cls.__solver
        code = solver.recaptcha(site_key, url)['code']

        driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{code}'")

    @classmethod
    def solve(
            cls,
            driver: WebDriver,
            site_key: str,
            url: str,
            captcha_type: CaptchaType
    ) -> None:
        match captcha_type.lower():
            case 'recaptcha':
                cls.solve_recaptcha(driver, site_key, url)
