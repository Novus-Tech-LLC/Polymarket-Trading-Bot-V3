"""
Create Polymarket CLOB client
Note: This is a placeholder. You'll need to either:
1. Install a Python wrapper for @polymarket/clob-client
2. Implement HTTP API calls to Polymarket CLOB API directly
3. Use a bridge to the TypeScript client
"""
from web3 import Web3
from eth_account import Account
from ..config.env import ENV
from ..utils.logger import Logger

PROXY_WALLET = ENV["PROXY_WALLET"]
PRIVATE_KEY = ENV["PRIVATE_KEY"]
CLOB_HTTP_URL = ENV["CLOB_HTTP_URL"]
RPC_URL = ENV["RPC_URL"]


async def is_gnosis_safe(address: str) -> bool:
    """Determines if a wallet is a Gnosis Safe by checking if it has contract code"""
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        code = w3.eth.get_code(Web3.to_checksum_address(address))
        # If code is not "0x", then it's a contract (likely Gnosis Safe)
        return code != b"0x"
    except Exception as error:
        Logger.error(f"Error checking wallet type: {error}")
        return False


class ClobClient:
    """
    Polymarket CLOB Client wrapper
    This is a placeholder implementation. You'll need to implement the actual
    CLOB API integration or use a Python wrapper for @polymarket/clob-client
    """

    def __init__(self, host: str, chain_id: int, wallet: Account, creds: dict | None = None, signature_type: str = "EOA", proxy_wallet: str | None = None):
        self.host = host
        self.chain_id = chain_id
        self.wallet = wallet
        self.creds = creds
        self.signature_type = signature_type
        self.proxy_wallet = proxy_wallet

    async def create_api_key(self) -> dict:
        """Create API key - placeholder"""
        # TODO: Implement actual API key creation
        return {"key": None}

    async def derive_api_key(self) -> dict:
        """Derive API key - placeholder"""
        # TODO: Implement actual API key derivation
        return {"key": None}

    async def get_order_book(self, asset: str) -> dict:
        """
        Get order book for an asset
        Returns: {"bids": [{"price": str, "size": str}], "asks": [{"price": str, "size": str}]}
        """
        # TODO: Implement actual order book fetching from CLOB API
        # This should call the Polymarket CLOB HTTP API
        raise NotImplementedError("getOrderBook not implemented - needs CLOB API integration")

    async def create_market_order(self, order_args: dict) -> dict:
        """
        Create a signed market order
        Args:
            order_args: {"side": "BUY"|"SELL", "tokenID": str, "amount": float, "price": float}
        Returns:
            Signed order object
        """
        # TODO: Implement order signing using Ethereum wallet
        # This needs to sign the order according to Polymarket's order format
        raise NotImplementedError("createMarketOrder not implemented - needs order signing logic")

    async def post_order(self, signed_order: dict, order_type: str = "FOK") -> dict:
        """
        Post order to Polymarket
        Args:
            signed_order: Signed order from createMarketOrder
            order_type: Order type (e.g., "FOK" for Fill-or-Kill)
        Returns:
            {"success": bool, ...}
        """
        # TODO: Implement order posting to CLOB API
        raise NotImplementedError("postOrder not implemented - needs CLOB API integration")


async def create_clob_client() -> ClobClient:
    """Create and initialize CLOB client"""
    chain_id = 137  # Polygon
    host = CLOB_HTTP_URL
    wallet = Account.from_key(PRIVATE_KEY)

    # Detect if the proxy wallet is a Gnosis Safe or EOA
    is_proxy_safe = await is_gnosis_safe(PROXY_WALLET)
    signature_type = "POLY_GNOSIS_SAFE" if is_proxy_safe else "EOA"

    Logger.info(f"Wallet type detected: {'Gnosis Safe' if is_proxy_safe else 'EOA (Externally Owned Account)'}")

    # Suppress output during API key creation
    import sys
    from io import StringIO

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        clob_client = ClobClient(host, chain_id, wallet, None, signature_type, PROXY_WALLET if is_proxy_safe else None)

        creds = await clob_client.create_api_key()
        if not creds.get("key"):
            creds = await clob_client.derive_api_key()

        clob_client = ClobClient(host, chain_id, wallet, creds, signature_type, PROXY_WALLET if is_proxy_safe else None)
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    return clob_client
