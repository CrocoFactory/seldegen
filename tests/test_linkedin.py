import pytest
import base64
import json
from seldegen import LinkedIn, Email


@pytest.fixture()
def email(credentials) -> Email:
    return Email(credentials['LINKEDIN_EMAIL'], credentials['LINKEDIN_EMAIL_PASSWORD'])


@pytest.fixture()
def linkedin(function_driver, email, credentials) -> LinkedIn:
    cookies = json.loads(base64.b64decode(credentials['LINKEDIN_COOKIES']).decode('utf-8'))
    return LinkedIn(
        function_driver,
        credentials['LINKEDIN_PASSWORD'],
        email,
        cookies
    )


@pytest.mark.parametrize("method", ['standard', 'cookies'])
def test_sign_in(function_driver, linkedin, email, method, make_capmonster, credentials):
    make_capmonster(function_driver)
    if method == 'standard':
        linkedin = LinkedIn(
            function_driver,
            credentials['LINKEDIN_PASSWORD'],
            email,
        )

    linkedin.sign_in()
