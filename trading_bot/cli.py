import argparse
import logging
import sys
from typing import Optional, List

from bot.logging_config import setup_logging
from bot.client import get_client
from bot.orders import place_futures_order, extract_order_summary
from bot.validators import (
    ValidationError,
    validate_symbol_format,
    validate_symbol_on_exchange,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)

logger = logging.getLogger(__name__)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse CLI arguments using argparse.
    """
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot (CLI)"
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading symbol (e.g. BTCUSDT).",
    )
    parser.add_argument(
        "--side",
        required=True,
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        help="Order type: MARKET or LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity (e.g. 0.001).",
    )
    parser.add_argument(
        "--price",
        required=False,
        help="Price for LIMIT orders (ignored for MARKET).",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Entry point for the CLI.
    """
    setup_logging()
    logger.info("Starting Binance Futures Testnet Trading Bot CLI.")

    try:
        args = parse_args(argv)

        # Validate basic inputs
        symbol = validate_symbol_format(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price_required = order_type == "LIMIT"
        price = validate_price(args.price, required=price_required)

        # Initialize client
        client = get_client()

        # Validate symbol on exchange
        symbol = validate_symbol_on_exchange(symbol, client)

        # Place order
        order_response = place_futures_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        # Extract and print order summary
        summary = extract_order_summary(order_response)
        print("\n=== Order Summary ===")
        print(f"Order ID    : {summary['orderId']}")
        print(f"Status      : {summary['status']}")
        print(f"Executed Qty: {summary['executedQty']}")
        print(f"Avg Price   : {summary['avgPrice']}")
        print("=====================\n")

        logger.info("CLI finished successfully.")
        return 0

    except ValidationError as e:
        logger.error("Validation error: %s", e)
        print(f"Input error: {e}", file=sys.stderr)
        return 1

    except RuntimeError as e:
        logger.error("Runtime error: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        logger.exception("Unexpected unhandled exception.")
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

