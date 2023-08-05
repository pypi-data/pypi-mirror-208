import os
from ethproto.wrappers import get_provider


def get_contracts_path():
    return os.path.abspath(os.path.dirname(__file__))


def register_contract_path(provider=None):
    if provider is None:
        provider = get_provider()
    my_contract_path = get_contracts_path()
    if my_contract_path not in provider.contracts_path:
        provider.contracts_path.append(my_contract_path)
