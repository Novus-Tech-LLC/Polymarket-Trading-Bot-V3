"""
Fetch data from URL with retry logic and error handling
"""
import time
import requests
from typing import TypeVar, Generic
from ..config.env import ENV
from ..utils.errors import NetworkError, normalize_error
from ..utils.constants import RETRY_CONFIG, TIME_CONSTANTS

T = TypeVar("T")


def is_network_error(error: Exception) -> bool:
    """Check if error is a network-related error"""
    if isinstance(error, requests.exceptions.RequestException):
        # Network timeout/connection errors
        return isinstance(
            error,
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
            ),
        )
    return False


def fetch_data(url: str) -> dict | list:
    """
    Fetch data from URL with retry logic and error handling

    Args:
        url: URL to fetch

    Returns:
        Response data as dict or list

    Raises:
        NetworkError: If all retries fail
    """
    retries = ENV["NETWORK_RETRY_LIMIT"]
    timeout = ENV["REQUEST_TIMEOUT_MS"] / 1000  # Convert to seconds
    retry_delay = RETRY_CONFIG["DEFAULT_RETRY_DELAY"] / 1000  # Convert to seconds

    # Validate URL
    if not url or not isinstance(url, str):
        raise NetworkError("Invalid URL provided", None, url)

    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            last_error = error
            is_last_attempt = attempt == retries

            if is_network_error(error) and not is_last_attempt:
                delay = retry_delay * (2 ** (attempt - 1))  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️  Network error (attempt {attempt}/{retries}), retrying in {delay:.1f}s...")
                time.sleep(delay)
                continue

            # If it's the last attempt or not a network error, raise
            if is_last_attempt:
                if is_network_error(error):
                    error_code = getattr(error, "code", "UNKNOWN")
                    raise NetworkError(f"Network timeout after {retries} attempts - {error_code}", error, url)
                # Non-network error on last attempt
                raise normalize_error(error)

    # This should never be reached, but needed for type checking
    raise normalize_error(last_error) if last_error else NetworkError("Unknown error", None, url)
