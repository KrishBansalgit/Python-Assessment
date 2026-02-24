import logging
from typing import Optional

from binance.um_futures import UMFutures
from binance.error import BinanceAPIException

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_symbol_format(symbol: str) -> str:
    """
    Basic symbol format validation (e.g. BTCUSDT).
    Actual exchange availability is checked separately.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string.")

    symbol = symbol.strip().upper()

    if len(symbol) < 6 or len(symbol) > 20:
        raise ValidationError("Symbol length looks invalid (expected something like BTCUSDT).")

    if not symbol.isalnum():
        raise ValidationError("Symbol must be alphanumeric (e.g. BTCUSDT).")

    return symbol


def validate_symbol_on_exchange(symbol: str, client: UMFutures) -> str:
    """
    Validate that the symbol exists on Binance Futures testnet.
    """
    try:
        logger.debug("Fetching exchange info to validate symbol: %s", symbol)
        exchange_info = client.exchange_info()
    except BinanceAPIException as e:
        logger.error("Failed to fetch exchange info from Binance: %s", e)
        raise ValidationError(
            "Unable to validate symbol with Binance. Please try again later."
        ) from e

    symbols = {s["symbol"] for s in exchange_info.get("symbols", [])}
    if symbol not in symbols:
        raise ValidationError(
            f"Symbol '{symbol}' is not listed on Binance Futures testnet."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side (BUY/SELL).
    """
    if not side:
        raise ValidationError("Side is required (BUY or SELL).")

    side = side.strip().upper()
    if side not in {"BUY", "SELL"}:
        raise ValidationError("Side must be either BUY or SELL.")
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type (MARKET/LIMIT).
    """
    if not order_type:
        raise ValidationError("Order type is required (MARKET or LIMIT).")

    order_type = order_type.strip().upper()
    if order_type not in {"MARKET", "LIMIT"}:
        raise ValidationError("Order type must be either MARKET or LIMIT.")
    return order_type


def validate_quantity(quantity: float) -> float:
    """
    Validate order quantity (must be positive).
    """
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be a number.") from None

    if q <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    return q


def validate_price(price: Optional[float], required: bool) -> Optional[float]:
    """
    Validate price. For LIMIT orders, price is required and must be positive.
    For MARKET orders, price must not be provided.
    """
    if required:
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValidationError("Price must be a number.") from None

        if p <= 0:
            raise ValidationError("Price must be greater than zero.")
        return p
    else:
        if price is not None:
            raise ValidationError("Price must not be provided for MARKET orders.")
        return None

