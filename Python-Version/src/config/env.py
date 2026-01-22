"""
Environment configuration and validation
"""
import os
import re
import sys
from typing import Optional
from dotenv import load_dotenv
from ..utils.errors import ConfigurationError
from .copy_strategy import (
    CopyStrategy,
    CopyStrategyConfig,
    parse_tiered_multipliers,
)

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Python < 3.7 or encoding not available, continue without
        pass

load_dotenv()


def is_valid_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))


def validate_required_env() -> None:
    """Validate required environment variables"""
    required = [
        "USER_ADDRESSES",
        "PROXY_WALLET",
        "PRIVATE_KEY",
        "CLOB_HTTP_URL",
        "CLOB_WS_URL",
        "MONGO_URI",
        "RPC_URL",
        "USDC_CONTRACT_ADDRESS",
    ]

    missing = [key for key in required if not os.getenv(key)]

    if missing:
        print("\n❌ Configuration Error: Missing required environment variables\n")
        print(f"Missing variables: {', '.join(missing)}\n")
        print("🔧 Quick fix:")
        print("   1. Create .env file with all required variables")
        print("   2. See docs/QUICK_START.md for detailed instructions\n")
        raise ConfigurationError(f"Missing required environment variables: {', '.join(missing)}")


def validate_addresses() -> None:
    """Validate Ethereum addresses"""
    proxy_wallet = os.getenv("PROXY_WALLET")
    if proxy_wallet and not is_valid_ethereum_address(proxy_wallet):
        print("\n❌ Invalid Wallet Address\n")
        print(f"Your PROXY_WALLET: {proxy_wallet}")
        print("Expected format:    0x followed by 40 hexadecimal characters\n")
        print("Example: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0\n")
        raise ConfigurationError(f"Invalid PROXY_WALLET address format: {proxy_wallet}")

    usdc_address = os.getenv("USDC_CONTRACT_ADDRESS")
    if usdc_address and not is_valid_ethereum_address(usdc_address):
        print("\n❌ Invalid USDC Contract Address\n")
        print(f"Current value: {usdc_address}")
        print("Default value: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174\n")
        raise ConfigurationError(f"Invalid USDC_CONTRACT_ADDRESS format: {usdc_address}")


def validate_numeric_config() -> None:
    """Validate numeric configuration values"""
    fetch_interval = int(os.getenv("FETCH_INTERVAL", "1"))
    if fetch_interval <= 0:
        raise ConfigurationError(f"Invalid FETCH_INTERVAL: {os.getenv('FETCH_INTERVAL')}. Must be a positive integer.")

    retry_limit = int(os.getenv("RETRY_LIMIT", "3"))
    if retry_limit < 1 or retry_limit > 10:
        raise ConfigurationError(f"Invalid RETRY_LIMIT: {os.getenv('RETRY_LIMIT')}. Must be between 1 and 10.")

    too_old_timestamp = int(os.getenv("TOO_OLD_TIMESTAMP", "24"))
    if too_old_timestamp < 1:
        raise ConfigurationError(
            f"Invalid TOO_OLD_TIMESTAMP: {os.getenv('TOO_OLD_TIMESTAMP')}. Must be a positive integer (hours)."
        )

    request_timeout = int(os.getenv("REQUEST_TIMEOUT_MS", "10000"))
    if request_timeout < 1000:
        raise ConfigurationError(
            f"Invalid REQUEST_TIMEOUT_MS: {os.getenv('REQUEST_TIMEOUT_MS')}. Must be at least 1000ms."
        )

    network_retry_limit = int(os.getenv("NETWORK_RETRY_LIMIT", "3"))
    if network_retry_limit < 1 or network_retry_limit > 10:
        raise ConfigurationError(
            f"Invalid NETWORK_RETRY_LIMIT: {os.getenv('NETWORK_RETRY_LIMIT')}. Must be between 1 and 10."
        )


def validate_urls() -> None:
    """Validate URL formats"""
    clob_http_url = os.getenv("CLOB_HTTP_URL")
    if clob_http_url and not clob_http_url.startswith("http"):
        print("\n❌ Invalid CLOB_HTTP_URL\n")
        print(f"Current value: {clob_http_url}")
        print("Default value: https://clob.polymarket.com/\n")
        raise ConfigurationError(f"Invalid CLOB_HTTP_URL: {clob_http_url}. Must be a valid HTTP/HTTPS URL.")

    clob_ws_url = os.getenv("CLOB_WS_URL")
    if clob_ws_url and not (clob_ws_url.startswith("ws://") or clob_ws_url.startswith("wss://")):
        print("\n❌ Invalid CLOB_WS_URL\n")
        print(f"Current value: {clob_ws_url}")
        print("Default value: wss://ws-subscriptions-clob.polymarket.com/ws\n")
        raise ConfigurationError(f"Invalid CLOB_WS_URL: {clob_ws_url}. Must be a valid WebSocket URL (ws:// or wss://).")

    rpc_url = os.getenv("RPC_URL")
    if rpc_url and not rpc_url.startswith("http"):
        print("\n❌ Invalid RPC_URL\n")
        print(f"Current value: {rpc_url}")
        raise ConfigurationError(f"Invalid RPC_URL: {rpc_url}. Must be a valid HTTP/HTTPS URL.")

    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri and not (mongo_uri.startswith("mongodb://") or mongo_uri.startswith("mongodb+srv://")):
        print("\n❌ Invalid MONGO_URI\n")
        print(f"Current value: {mongo_uri}")
        raise ConfigurationError(f"Invalid MONGO_URI: {mongo_uri}. Must be a valid MongoDB connection string.")


def parse_user_addresses(input_str: str) -> list[str]:
    """Parse USER_ADDRESSES: supports both comma-separated string and JSON array"""
    trimmed = input_str.strip()

    # Check if it's JSON array format
    if trimmed.startswith("[") and trimmed.endswith("]"):
        try:
            import json

            parsed = json.loads(trimmed)
            if isinstance(parsed, list):
                addresses = [addr.lower().strip() for addr in parsed if addr.strip()]
                # Validate each address
                for addr in addresses:
                    if not is_valid_ethereum_address(addr):
                        print("\n❌ Invalid Trader Address in USER_ADDRESSES\n")
                        print(f"Invalid address: {addr}")
                        raise ConfigurationError(f"Invalid Ethereum address in USER_ADDRESSES: {addr}")
                return addresses
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON format for USER_ADDRESSES: {e}")

    # Otherwise treat as comma-separated
    addresses = [addr.lower().strip() for addr in trimmed.split(",") if addr.strip()]
    # Validate each address
    for addr in addresses:
        if not is_valid_ethereum_address(addr):
            print("\n❌ Invalid Trader Address in USER_ADDRESSES\n")
            print(f"Invalid address: {addr}")
            raise ConfigurationError(f"Invalid Ethereum address in USER_ADDRESSES: {addr}")

    return addresses


def parse_copy_strategy() -> CopyStrategyConfig:
    """Parse copy strategy configuration"""
    # Support legacy COPY_PERCENTAGE + TRADE_MULTIPLIER for backward compatibility
    has_legacy_config = os.getenv("COPY_PERCENTAGE") and not os.getenv("COPY_STRATEGY")

    if has_legacy_config:
        print("⚠️  Using legacy COPY_PERCENTAGE configuration. Consider migrating to COPY_STRATEGY.")
        copy_percentage = float(os.getenv("COPY_PERCENTAGE", "10.0"))
        trade_multiplier = float(os.getenv("TRADE_MULTIPLIER", "1.0"))
        effective_percentage = copy_percentage * trade_multiplier

        config: CopyStrategyConfig = {
            "strategy": CopyStrategy.PERCENTAGE,
            "copySize": effective_percentage,
            "maxOrderSizeUSD": float(os.getenv("MAX_ORDER_SIZE_USD", "100.0")),
            "minOrderSizeUSD": float(os.getenv("MIN_ORDER_SIZE_USD", "1.0")),
        }

        max_position_size = os.getenv("MAX_POSITION_SIZE_USD")
        if max_position_size:
            config["maxPositionSizeUSD"] = float(max_position_size)

        max_daily_volume = os.getenv("MAX_DAILY_VOLUME_USD")
        if max_daily_volume:
            config["maxDailyVolumeUSD"] = float(max_daily_volume)

        # Parse tiered multipliers if configured (even for legacy mode)
        tiered_multipliers_str = os.getenv("TIERED_MULTIPLIERS")
        if tiered_multipliers_str:
            try:
                config["tieredMultipliers"] = parse_tiered_multipliers(tiered_multipliers_str)
                print(f"✓ Loaded {len(config['tieredMultipliers'])} tiered multipliers")
            except ValueError as e:
                raise ConfigurationError(f"Failed to parse TIERED_MULTIPLIERS: {e}")
        elif trade_multiplier != 1.0:
            # If using legacy single multiplier, store it
            config["tradeMultiplier"] = trade_multiplier

        return config

    # Parse new copy strategy configuration
    strategy_str = (os.getenv("COPY_STRATEGY", "PERCENTAGE")).upper()
    try:
        strategy = CopyStrategy[strategy_str]
    except KeyError:
        strategy = CopyStrategy.PERCENTAGE

    config: CopyStrategyConfig = {
        "strategy": strategy,
        "copySize": float(os.getenv("COPY_SIZE", "10.0")),
        "maxOrderSizeUSD": float(os.getenv("MAX_ORDER_SIZE_USD", "100.0")),
        "minOrderSizeUSD": float(os.getenv("MIN_ORDER_SIZE_USD", "1.0")),
    }

    max_position_size = os.getenv("MAX_POSITION_SIZE_USD")
    if max_position_size:
        config["maxPositionSizeUSD"] = float(max_position_size)

    max_daily_volume = os.getenv("MAX_DAILY_VOLUME_USD")
    if max_daily_volume:
        config["maxDailyVolumeUSD"] = float(max_daily_volume)

    # Add adaptive strategy parameters if applicable
    if strategy == CopyStrategy.ADAPTIVE:
        config["adaptiveMinPercent"] = float(os.getenv("ADAPTIVE_MIN_PERCENT", str(config["copySize"])))
        config["adaptiveMaxPercent"] = float(os.getenv("ADAPTIVE_MAX_PERCENT", str(config["copySize"])))
        config["adaptiveThreshold"] = float(os.getenv("ADAPTIVE_THRESHOLD_USD", "500.0"))

    # Parse tiered multipliers if configured
    tiered_multipliers_str = os.getenv("TIERED_MULTIPLIERS")
    if tiered_multipliers_str:
        try:
            config["tieredMultipliers"] = parse_tiered_multipliers(tiered_multipliers_str)
            print(f"✓ Loaded {len(config['tieredMultipliers'])} tiered multipliers")
        except ValueError as e:
            raise ConfigurationError(f"Failed to parse TIERED_MULTIPLIERS: {e}")
    else:
        # Fall back to single multiplier if no tiers configured
        trade_multiplier_str = os.getenv("TRADE_MULTIPLIER")
        if trade_multiplier_str:
            single_multiplier = float(trade_multiplier_str)
            if single_multiplier != 1.0:
                config["tradeMultiplier"] = single_multiplier
                print(f"✓ Using single trade multiplier: {single_multiplier}x")

    return config


# Run all validations
validate_required_env()
validate_addresses()
validate_numeric_config()
validate_urls()

# Parse USER_ADDRESSES
user_addresses_str = os.getenv("USER_ADDRESSES", "")
if not user_addresses_str:
    raise ConfigurationError("USER_ADDRESSES is required")

USER_ADDRESSES = parse_user_addresses(user_addresses_str)

# Export ENV configuration
ENV = {
    "USER_ADDRESSES": USER_ADDRESSES,
    "PROXY_WALLET": os.getenv("PROXY_WALLET", ""),
    "PRIVATE_KEY": os.getenv("PRIVATE_KEY", ""),
    "CLOB_HTTP_URL": os.getenv("CLOB_HTTP_URL", ""),
    "CLOB_WS_URL": os.getenv("CLOB_WS_URL", ""),
    "FETCH_INTERVAL": int(os.getenv("FETCH_INTERVAL", "1")),
    "TOO_OLD_TIMESTAMP": int(os.getenv("TOO_OLD_TIMESTAMP", "24")),
    "RETRY_LIMIT": int(os.getenv("RETRY_LIMIT", "3")),
    # Legacy parameters (kept for backward compatibility)
    "TRADE_MULTIPLIER": float(os.getenv("TRADE_MULTIPLIER", "1.0")),
    "COPY_PERCENTAGE": float(os.getenv("COPY_PERCENTAGE", "10.0")),
    # New copy strategy configuration
    "COPY_STRATEGY_CONFIG": parse_copy_strategy(),
    # Network settings
    "REQUEST_TIMEOUT_MS": int(os.getenv("REQUEST_TIMEOUT_MS", "10000")),
    "NETWORK_RETRY_LIMIT": int(os.getenv("NETWORK_RETRY_LIMIT", "3")),
    # Trade aggregation settings
    "TRADE_AGGREGATION_ENABLED": os.getenv("TRADE_AGGREGATION_ENABLED", "false").lower() == "true",
    "TRADE_AGGREGATION_WINDOW_SECONDS": int(os.getenv("TRADE_AGGREGATION_WINDOW_SECONDS", "300")),  # 5 minutes default
    "MONGO_URI": os.getenv("MONGO_URI", ""),
    "RPC_URL": os.getenv("RPC_URL", ""),
    "USDC_CONTRACT_ADDRESS": os.getenv("USDC_CONTRACT_ADDRESS", ""),
}
