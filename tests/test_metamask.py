import time
import pytest
from eth_account import Account
from seldegen import Metamask


@pytest.fixture()
def metamask(session_driver):
    return Metamask.sign_up(session_driver, 'toTheMoon123')


def test_sign_up(function_driver):
    assert Metamask.sign_up(function_driver, 'toTheMoon123')


def test_sign_in(function_driver, credentials):
    Account.enable_unaudited_hdwallet_features()
    _, mnemonic = Account.create_with_mnemonic()
    metamask = Metamask(function_driver, 'toTheMoon123', mnemonic)
    metamask.sign_in()


def test_import_account(metamask, credentials):
    metamask.import_account(credentials['TEST_PRIVATE_KEY'])
    time.sleep(120)

    
def test_switch_network(metamask):
    network = 'Linea'
    metamask.switch_network(network)
