from typing import Any
from seldegen.types import Cookies


class InvalidMnemonicError(ValueError):
    """Raised when a length of provided mnemonic is invalid"""

    def __init__(self, mnemonic: list[str]):
        super().__init__(f"Mnemonic is invalid. Mnemonic has to have length equals to 12. "
                         f"Your mnemonic is: {mnemonic}.")


class InvalidCodeError(ValueError):
    """Raised when a verifying code is invalid"""

    def __init__(self, code: Any):
        super().__init__(f"Provided code is invalid. Code - {code}")


class InvalidSocialError(ValueError):
    """Raised when provided social is not supported for connecting"""

    def __init__(self, social: Any, connector: Any):
        super().__init__(f"Provided social {social} is not valid for connecting to {connector}")


class NoVotingPowerError(PermissionError):
    """Raised when wallet has no voting power for a proposal"""

    def __init__(self, proposal_url: str):
        super().__init__(f"Wallet has no voting power for proposal {proposal_url}")


class InvalidCredentialsError(ValueError):
    """Raised when provided invalid credentials"""
    
    def __init__(self, credentials: dict, social: str):
        super().__init__(f'Invalid credentials provided to social {social}. Credentials: {credentials}')


class InvalidCookiesError(InvalidCredentialsError):
    """Raised when provided invalid cookies"""

    def __init__(self, cookies: Cookies, social: str):
        cookies = {'cookies': cookies}
        super().__init__(cookies, social)
