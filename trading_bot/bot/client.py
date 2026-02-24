import logging
import os
from typing import Optional

from dotenv import load_dotenv
from binance.um_futures import UMFutures

logger = logging.getLogger(__name__)


TESTNET_BASE_URL = "https://testnet.binancefuture.com"


_client_instance: Optional[UMFutures] = None


def _load_env() -> None:
    """
    Load environment variables from a .env file if present.
    """
    load_dotenv()


def get_client() -> UMFutures:
    """
    Create or return a cached Binance USDⓈ-M Futures client
    configured for TESTNET only.

    Reads the following environment variables:
    - BINANCE_API_KEY
    - BINANCE_API_SECRET
    """
    global _client_instance
    if _client_instance is not None:
        return _client_instance

    _load_env()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise RuntimeError(
            "Missing API credentials. Please set BINANCE_API_KEY and "
            "BINANCE_API_SECRET in your environment or .env file."
        )

    logger.info("Initializing Binance UMFutures client for TESTNET.")
    logger.debug("Using base URL: %s", TESTNET_BASE_URL)

    client = UMFutures(key=api_key, secret=api_secret, base_url=TESTNET_BASE_URL)

    _client_instance = client
    return client

