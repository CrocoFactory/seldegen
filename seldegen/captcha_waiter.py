import time
from croco_selenium import ActionPerformer
from enum import Enum
from datetime import datetime
from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from seldegen.context import Context
from typing import Optional

__all__ = [
    'ElementType',
    'CaptchaWaiter',
    'CaptchaType'
]


class ElementType(Enum):
    FRAME = 'frame'
    BOX = 'box'
    INVISIBLE = 'invisible'


class CaptchaType(Enum):
    H_CAPTCHA = 'h_captcha'
    RE_CAPTCHA = 're_captcha'


_DEFAULT_TIMEOUT = Context.default_timeout()


class CaptchaWaiter:
    """This is a class waiting for solving of different types of captcha"""

    @classmethod
    def wait_for_solving(
            cls,
            driver: WebDriver,
            captcha_type: CaptchaType,
            deadline: Optional[int] = None,
            element_type: ElementType = ElementType.FRAME
    ) -> None:
        """
        Performs waiting for captcha. If you want to limit waiting for captcha time, you can specify a deadline
        Same captcha type in the different sites may be provided as various HTML elements, for this reason you can
        specify element_type.

        :param driver: Driver to be interacted with
        :param captcha_type: Type of captcha. Can take in captcha types such as hCaptcha, reCaptcha
        :param deadline: Waiting deadline in seconds
        :param element_type: Type of captcha element. Can take in ElementType.FRAME, ElementType.BOX
        :return:
        """
        match captcha_type:
            case CaptchaType.H_CAPTCHA:
                cls.wait_for_h_captcha(driver, deadline)
            case CaptchaType.RE_CAPTCHA:
                cls.wait_for_re_captcha(driver, deadline, element_type)

    @staticmethod
    def __wait_by_checkbox(driver: WebDriver, checkbox_xpath: str, deadline: Optional[int] = None):
        action_performer = ActionPerformer(driver)        

        if not deadline:
            try:
                while action_performer.get_element_attribute(
                    _DEFAULT_TIMEOUT,
                    checkbox_xpath,
                    "aria-checked",
                    StaleElementReferenceException
                ) != 'true':
                    pass
            except TimeoutException:
                pass
        else:
            start_time = datetime.now()

            while True:
                current_time = datetime.now()
                time_range = (current_time - start_time).total_seconds()
                if time_range >= deadline:
                    raise TimeoutException

                if action_performer.get_element_attribute(
                        _DEFAULT_TIMEOUT,
                        checkbox_xpath,
                        "aria-checked"
                ) == 'true':
                    break

    @classmethod
    def wait_for_h_captcha(cls, driver: WebDriver, deadline: Optional[int] = None) -> None:
        """
        Performs waiting for hCaptcha. If you want to limit waiting for captcha time, you can specify a deadline
        Same captcha type in the different sites may be provided as various HTML elements, for this reason you can
        specify element_type.

        :param driver: Driver to be interacted with
        :param deadline: Waiting deadline in seconds
        :return: None
        """
        action_performer = ActionPerformer(driver)

        frame_xpath = '//iframe[@data-hcaptcha-widget-id]'
        action_performer.switch_to_frame(_DEFAULT_TIMEOUT, frame_xpath)

        checkbox_xpath = '//div[@id="checkbox"]'

        cls.__wait_by_checkbox(driver, checkbox_xpath, deadline)

        action_performer.switch_to_parent_frame()

    @classmethod
    def wait_for_re_captcha(
            cls,
            driver: WebDriver,
            deadline: Optional[int] = None,
            element_type: ElementType = ElementType.FRAME
    ) -> None:
        """
        Performs waiting for hCaptcha. If you want to limit waiting for captcha time, you can specify a deadline
        Same captcha type in the different sites may be provided as various HTML elements, for this reason you can
        specify element_type.
        :param driver: Driver to be interacted with
        :param deadline: Waiting deadline in seconds
        :param element_type: Type of captcha element. Can take in ElementType.FRAME, ElementType.BOX
        :return: None
        """
        match element_type:
            case ElementType.FRAME:
                cls.__handle_frame_re_captcha(driver, deadline)
            case ElementType.BOX:
                cls.__handle_box_re_captcha(driver, deadline)

    @classmethod
    def __handle_frame_re_captcha(cls, driver: WebDriver, deadline: Optional[int] = None) -> None:
        action_performer = ActionPerformer(driver)

        frame_xpath = '//iframe[@title="reCAPTCHA"]'
        action_performer.switch_to_frame(_DEFAULT_TIMEOUT, frame_xpath)

        checkbox_xpath = '//*[@id="recaptcha-anchor"]'

        cls.__wait_by_checkbox(driver, checkbox_xpath, deadline)

        action_performer.switch_to_parent_frame()

        time.sleep(1)

    @classmethod
    def __handle_box_re_captcha(cls, driver: WebDriver, deadline: Optional[int] = None) -> None:
        checkbox_xpath = '//span[contains(@class, "recaptcha-checkbox")]'

        cls.__wait_by_checkbox(driver, checkbox_xpath, deadline)
        time.sleep(1)
        