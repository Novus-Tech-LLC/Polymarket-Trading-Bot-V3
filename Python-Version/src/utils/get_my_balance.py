"""
Get USDC balance for a given address
"""
from web3 import Web3
from ..config.env import ENV

RPC_URL = ENV["RPC_URL"]
USDC_CONTRACT_ADDRESS = ENV["USDC_CONTRACT_ADDRESS"]

# USDC ABI (minimal - just balanceOf function)
USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    }
]


def get_my_balance(address: str) -> float:
    """
    Get USDC balance for a given address

    Args:
        address: Ethereum address to check balance for

    Returns:
        USDC balance as float
    """
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    usdc_contract = w3.eth.contract(address=Web3.to_checksum_address(USDC_CONTRACT_ADDRESS), abi=USDC_ABI)
    balance_usdc = usdc_contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
    # USDC has 6 decimals
    balance_usdc_real = balance_usdc / 10**6
    return float(balance_usdc_real)
