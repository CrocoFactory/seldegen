import pytest
from seldegen import Google, Email


@pytest.fixture()
def recovery_email(credentials) -> Email:
    return Email(credentials['GOOGLE_RECOVERY_EMAIL'], credentials['GOOGLE_RECOVERY_EMAIL_PASSWORD'])


@pytest.fixture()
def google(session_driver, credentials, recovery_email) -> Google:
    return Google(
        session_driver,
        credentials['GOOGLE_PASSWORD'],
        credentials['GOOGLE_EMAIL'],
        recovery_email
    )


def test_sign_in(session_driver, google):
    google.sign_in()
