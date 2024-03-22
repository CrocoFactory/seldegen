from dataclasses import dataclass
from typing import Literal


@dataclass
class AuthenticationAccount:
    id: int
    secret_key: str


CaptchaType = Literal["reCAPTCHA", "hCAPTCHA"]

Cookies = list[dict[str, str | bool | int]]


@dataclass
class WalletAccount:
    private_key: str
    public_key: str
