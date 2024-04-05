import time
import pytest
from seldegen import Metamask


@pytest.fixture()
def metamask(session_driver):
    return Metamask.sign_up(session_driver, 'toTheMoon123')


def test_sign_up(function_driver):
    assert Metamask.sign_up(function_driver, 'toTheMoon123')


def test_sign_in(function_driver, credentials):
    metamask = Metamask(function_driver, 'toTheMoon123', credentials['TEST_MNEMONIC'])
    metamask.sign_in()


def test_import_account(metamask, credentials):
    metamask.import_account(credentials['TEST_PRIVATE_KEY'])
    time.sleep(120)

    
def test_switch_network(metamask):
    network = 'Linea'
    metamask.switch_network(network)
