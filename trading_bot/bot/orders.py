import logging
from typing import Any, Dict, Optional

from binance.um_futures import UMFutures
from binance.error import BinanceAPIException, BinanceOrderException

logger = logging.getLogger(__name__)


def place_futures_order(
    client: UMFutures,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Place a Binance Futures order (MARKET or LIMIT, BUY or SELL).

    All API requests and responses are logged.
    Raises RuntimeError on API-related failures.
    """
    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        # Good-Til-Cancelled limit order
        params["timeInForce"] = "GTC"
        params["price"] = f"{price:.8f}"

    logger.info("Sending new order request to Binance.")
    logger.debug("Order request params: %s", params)

    try:
        response = client.new_order(**params)
        logger.info("Order successfully placed on Binance.")
        logger.debug("Order response: %s", response)
        return response

    except BinanceOrderException as e:
        logger.error("Binance order error: %s", e)
        raise RuntimeError(f"Order rejected by Binance: {e}") from e

    except BinanceAPIException as e:
        logger.error("Binance API error: %s", e)
        raise RuntimeError(f"Binance API error: {e}") from e

    except Exception as e:
        logger.exception("Unexpected error while placing order.")
        raise RuntimeError(f"Unexpected error while placing order: {e}") from e


def extract_order_summary(order_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize key fields from the Binance Futures order response.

    Returns a dict with:
    - orderId
    - status
    - executedQty
    - avgPrice
    """
    order_id = order_response.get("orderId")
    status = order_response.get("status")
    executed_qty = order_response.get("executedQty")
    avg_price = order_response.get("avgPrice")

    # Some responses may not include avgPrice, so we try other fields as fallback
    if avg_price in (None, ""):
        avg_price = order_response.get("price") or "0"

    summary = {
        "orderId": order_id,
        "status": status,
        "executedQty": executed_qty,
        "avgPrice": avg_price,
    }

    logger.debug("Extracted order summary: %s", summary)
    return summary

