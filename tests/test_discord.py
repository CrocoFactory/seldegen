import pytest
from seldegen import Discord, Email


@pytest.fixture()
def email(credentials) -> Email:
    return Email(credentials['DISCORD_EMAIL'], credentials['DISCORD_EMAIL_PASSWORD'])


@pytest.fixture()
def discord(function_driver, email, credentials) -> Discord:
    return Discord(
        function_driver,
        credentials['DISCORD_PASSWORD'],
        email,
        credentials['DISCORD_AUTH_TOKEN']
    )


@pytest.mark.parametrize("method", ['standard', 'token'])
def test_sign_in(function_driver, discord, email, method, credentials, make_capmonster):
    make_capmonster(function_driver)
    if method == 'standard':
        discord = Discord(
            function_driver,
            credentials['DISCORD_PASSWORD'],
            email,
        )

    discord.sign_in()
