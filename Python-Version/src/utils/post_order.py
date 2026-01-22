"""
Post order to Polymarket based on trade condition
Note: This requires a fully implemented CLOB client. See create_clob_client.py
"""
from typing import Optional, Any
from ..config.env import ENV
from ..models.user_history import get_user_activity_model
from ..interfaces.user import UserActivityInterface, UserPositionInterface, TradeSide
from ..config.copy_strategy import calculate_order_size, get_trade_multiplier
from .logger import Logger
from .constants import TRADING_CONSTANTS, DB_FIELDS
from .errors import TradingError, InsufficientFundsError, normalize_error

RETRY_LIMIT = ENV["RETRY_LIMIT"]
COPY_STRATEGY_CONFIG = ENV["COPY_STRATEGY_CONFIG"]
MIN_ORDER_SIZE_USD = TRADING_CONSTANTS["MIN_ORDER_SIZE_USD"]
MIN_ORDER_SIZE_TOKENS = TRADING_CONSTANTS["MIN_ORDER_SIZE_TOKENS"]


def extract_order_error(response: dict) -> Optional[str]:
    """Extract error message from order response"""
    if not response:
        return None

    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        direct_error = response.get("error")
        if isinstance(direct_error, str):
            return direct_error

        if isinstance(direct_error, dict):
            nested = direct_error
            if isinstance(nested.get("error"), str):
                return nested["error"]
            if isinstance(nested.get("message"), str):
                return nested["message"]

        if isinstance(response.get("errorMsg"), str):
            return response["errorMsg"]

        if isinstance(response.get("message"), str):
            return response["message"]

    return None


def is_insufficient_balance_or_allowance_error(message: Optional[str]) -> bool:
    """Check if error message indicates insufficient balance or allowance"""
    if not message:
        return False
    lower = message.lower()
    return "not enough balance" in lower or "allowance" in lower


async def post_order(
    clob_client: Any,  # ClobClient type - placeholder
    condition: str,  # 'buy', 'sell', or 'merge'
    my_position: Optional[UserPositionInterface],
    user_position: Optional[UserPositionInterface],
    trade: UserActivityInterface,
    my_balance: float,
    user_balance: float,
    user_address: str,
) -> None:
    """
    Post order to Polymarket based on trade condition

    Args:
        clob_client: CLOB client instance
        condition: Trade condition: 'buy', 'sell', or 'merge'
        my_position: Current position in our wallet
        user_position: Current position in trader's wallet
        trade: Trade activity to execute
        my_balance: Our USDC balance
        user_balance: Trader's total portfolio value
        user_address: Trader's wallet address

    Raises:
        TradingError: If order execution fails
    """
    UserActivity = get_user_activity_model(user_address)

    if condition == "merge":
        Logger.info("Executing MERGE strategy...")
        if not my_position:
            Logger.warning("No position to merge")
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
            return

        remaining = my_position["size"]

        # Check minimum order size
        if remaining < MIN_ORDER_SIZE_TOKENS:
            Logger.warning(f"Position size ({remaining:.2f} tokens) too small to merge - skipping")
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
            return

        retry = 0
        abort_due_to_funds = False

        while remaining > 0 and retry < RETRY_LIMIT:
            order_book = await clob_client.get_order_book(trade["asset"])
            if not order_book.get("bids") or len(order_book["bids"]) == 0:
                Logger.warning("No bids available in order book")
                UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
                break

            max_price_bid = max(order_book["bids"], key=lambda bid: float(bid["price"]))

            Logger.info(f"Best bid: {max_price_bid['size']} @ ${max_price_bid['price']}")

            if remaining <= float(max_price_bid["size"]):
                order_args = {
                    "side": "SELL",
                    "tokenID": my_position["asset"],
                    "amount": remaining,
                    "price": float(max_price_bid["price"]),
                }
            else:
                order_args = {
                    "side": "SELL",
                    "tokenID": my_position["asset"],
                    "amount": float(max_price_bid["size"]),
                    "price": float(max_price_bid["price"]),
                }

            signed_order = await clob_client.create_market_order(order_args)
            resp = await clob_client.post_order(signed_order, "FOK")

            if resp.get("success") is True:
                retry = 0
                Logger.order_result(True, f"Sold {order_args['amount']} tokens at ${order_args['price']}")
                remaining -= order_args["amount"]
            else:
                error_message = extract_order_error(resp)
                if is_insufficient_balance_or_allowance_error(error_message):
                    abort_due_to_funds = True
                    Logger.warning(f"Order rejected: {error_message or 'Insufficient balance or allowance'}")
                    Logger.warning("Skipping remaining attempts. Top up funds or check allowance before retrying.")
                    break
                retry += 1
                Logger.warning(f"Order failed (attempt {retry}/{RETRY_LIMIT}){f' - {error_message}' if error_message else ''}")

        if abort_due_to_funds:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["BOT_EXECUTED_TIME"]: RETRY_LIMIT}},
            )
            return

        if retry >= RETRY_LIMIT:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["BOT_EXECUTED_TIME"]: retry}},
            )
        else:
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})

    elif condition == "buy":
        Logger.info("Executing BUY strategy...")

        Logger.info(f"Your balance: ${my_balance:.2f}")
        Logger.info(f"Trader bought: ${trade['usdcSize']:.2f}")

        # Get current position size for position limit checks
        current_position_value = (my_position["size"] * my_position["avgPrice"]) if my_position else 0

        # Use new copy strategy system
        order_calc = calculate_order_size(
            COPY_STRATEGY_CONFIG,
            trade["usdcSize"],
            my_balance,
            current_position_value,
        )

        # Log the calculation reasoning
        Logger.info(f"📊 {order_calc['reasoning']}")

        # Check if order should be executed
        if order_calc["finalAmount"] == 0:
            Logger.warning(f"❌ Cannot execute: {order_calc['reasoning']}")
            if order_calc["belowMinimum"]:
                Logger.warning("💡 Increase COPY_SIZE or wait for larger trades")
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
            return

        remaining = order_calc["finalAmount"]
        retry = 0
        abort_due_to_funds = False
        total_bought_tokens = 0

        while remaining > 0 and retry < RETRY_LIMIT:
            order_book = await clob_client.get_order_book(trade["asset"])
            if not order_book.get("asks") or len(order_book["asks"]) == 0:
                Logger.warning("No asks available in order book")
                UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
                break

            min_price_ask = min(order_book["asks"], key=lambda ask: float(ask["price"]))

            Logger.info(f"Best ask: {min_price_ask['size']} @ ${min_price_ask['price']}")

            if float(min_price_ask["price"]) - TRADING_CONSTANTS["MAX_PRICE_SLIPPAGE"] > trade["price"]:
                Logger.warning("Price slippage too high - skipping trade")
                UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
                break

            # Check if remaining amount is below minimum
            if remaining < MIN_ORDER_SIZE_USD:
                Logger.info(f"Remaining amount (${remaining:.2f}) below minimum - completing trade")
                UserActivity.update_one(
                    {"_id": trade["_id"]},
                    {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["MY_BOUGHT_SIZE"]: total_bought_tokens}},
                )
                break

            max_order_size = float(min_price_ask["size"]) * float(min_price_ask["price"])
            order_size = min(remaining, max_order_size)

            order_args = {
                "side": "BUY",
                "tokenID": trade["asset"],
                "amount": order_size,
                "price": float(min_price_ask["price"]),
            }

            Logger.info(f"Creating order: ${order_size:.2f} @ ${min_price_ask['price']} (Balance: ${my_balance:.2f})")

            signed_order = await clob_client.create_market_order(order_args)
            resp = await clob_client.post_order(signed_order, "FOK")

            if resp.get("success") is True:
                retry = 0
                tokens_bought = order_args["amount"] / order_args["price"]
                total_bought_tokens += tokens_bought
                Logger.order_result(
                    True,
                    f"Bought ${order_args['amount']:.2f} at ${order_args['price']} ({tokens_bought:.2f} tokens)",
                )
                remaining -= order_args["amount"]
            else:
                error_message = extract_order_error(resp)
                if is_insufficient_balance_or_allowance_error(error_message):
                    abort_due_to_funds = True
                    Logger.warning(f"Order rejected: {error_message or 'Insufficient balance or allowance'}")
                    Logger.warning("Skipping remaining attempts. Top up funds or check allowance before retrying.")
                    break
                retry += 1
                Logger.warning(f"Order failed (attempt {retry}/{RETRY_LIMIT}){f' - {error_message}' if error_message else ''}")

        if abort_due_to_funds:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {
                    "$set": {
                        DB_FIELDS["BOT_EXECUTED"]: True,
                        DB_FIELDS["BOT_EXECUTED_TIME"]: RETRY_LIMIT,
                        DB_FIELDS["MY_BOUGHT_SIZE"]: total_bought_tokens,
                    }
                },
            )
            return

        if retry >= RETRY_LIMIT:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {
                    "$set": {
                        DB_FIELDS["BOT_EXECUTED"]: True,
                        DB_FIELDS["BOT_EXECUTED_TIME"]: retry,
                        DB_FIELDS["MY_BOUGHT_SIZE"]: total_bought_tokens,
                    }
                },
            )
        else:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["MY_BOUGHT_SIZE"]: total_bought_tokens}},
            )

        # Log the tracked purchase
        if total_bought_tokens > 0:
            Logger.info(f"📝 Tracked purchase: {total_bought_tokens:.2f} tokens for future sell calculations")

    elif condition == "sell":
        Logger.info("Executing SELL strategy...")
        remaining = 0

        if not my_position:
            Logger.warning("No position to sell")
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
            return

        # Get all previous BUY trades for this asset to calculate total bought
        previous_buys = list(
            UserActivity.find(
                {
                    "asset": trade["asset"],
                    "conditionId": trade["conditionId"],
                    "side": DB_FIELDS["SIDE_BUY"],
                    DB_FIELDS["BOT_EXECUTED"]: True,
                    DB_FIELDS["MY_BOUGHT_SIZE"]: {"$exists": True, "$gt": 0},
                }
            )
        )

        total_bought_tokens = sum(buy.get(DB_FIELDS["MY_BOUGHT_SIZE"], 0) for buy in previous_buys)

        if total_bought_tokens > 0:
            Logger.info(f"📊 Found {len(previous_buys)} previous purchases: {total_bought_tokens:.2f} tokens bought")

        if not user_position:
            # Trader sold entire position - we sell entire position too
            remaining = my_position["size"]
            Logger.info(f"Trader closed entire position → Selling all your {remaining:.2f} tokens")
        else:
            # Calculate the % of position the trader is selling
            trader_sell_percent = trade["size"] / (user_position["size"] + trade["size"])
            trader_position_before = user_position["size"] + trade["size"]

            Logger.info(
                f"Position comparison: Trader has {trader_position_before:.2f} tokens, You have {my_position['size']:.2f} tokens"
            )
            Logger.info(f"Trader selling: {trade['size']:.2f} tokens ({(trader_sell_percent * 100):.2f}% of their position)")

            # Use tracked bought tokens if available, otherwise fallback to current position
            if total_bought_tokens > 0:
                base_sell_size = total_bought_tokens * trader_sell_percent
                Logger.info(
                    f"Calculating from tracked purchases: {total_bought_tokens:.2f} × {(trader_sell_percent * 100):.2f}% = {base_sell_size:.2f} tokens"
                )
            else:
                base_sell_size = my_position["size"] * trader_sell_percent
                Logger.warning(
                    f"No tracked purchases found, using current position: {my_position['size']:.2f} × {(trader_sell_percent * 100):.2f}% = {base_sell_size:.2f} tokens"
                )

            # Apply tiered or single multiplier
            multiplier = get_trade_multiplier(COPY_STRATEGY_CONFIG, trade["usdcSize"])
            remaining = base_sell_size * multiplier

            if multiplier != 1.0:
                Logger.info(
                    f"Applying {multiplier}x multiplier (based on trader's ${trade['usdcSize']:.2f} order): {base_sell_size:.2f} → {remaining:.2f} tokens"
                )

        # Check minimum order size
        if remaining < MIN_ORDER_SIZE_TOKENS:
            Logger.warning(f"❌ Cannot execute: Sell amount {remaining:.2f} tokens below minimum ({MIN_ORDER_SIZE_TOKENS} token)")
            Logger.warning("💡 This happens when position sizes are too small or mismatched")
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
            return

        # Cap sell amount to available position size
        if remaining > my_position["size"]:
            Logger.warning(
                f"⚠️  Calculated sell {remaining:.2f} tokens > Your position {my_position['size']:.2f} tokens"
            )
            Logger.warning(f"Capping to maximum available: {my_position['size']:.2f} tokens")
            remaining = my_position["size"]

        retry = 0
        abort_due_to_funds = False
        total_sold_tokens = 0

        while remaining > 0 and retry < RETRY_LIMIT:
            order_book = await clob_client.get_order_book(trade["asset"])
            if not order_book.get("bids") or len(order_book["bids"]) == 0:
                UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
                Logger.warning("No bids available in order book")
                break

            max_price_bid = max(order_book["bids"], key=lambda bid: float(bid["price"]))

            Logger.info(f"Best bid: {max_price_bid['size']} @ ${max_price_bid['price']}")

            # Check if remaining amount is below minimum
            if remaining < MIN_ORDER_SIZE_TOKENS:
                Logger.info(f"Remaining amount ({remaining:.2f} tokens) below minimum - completing trade")
                UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
                break

            sell_amount = min(remaining, float(max_price_bid["size"]))

            # Final check: don't create orders below minimum
            if sell_amount < MIN_ORDER_SIZE_TOKENS:
                Logger.info(f"Order amount ({sell_amount:.2f} tokens) below minimum - completing trade")
                UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})
                break

            order_args = {
                "side": "SELL",
                "tokenID": trade["asset"],
                "amount": sell_amount,
                "price": float(max_price_bid["price"]),
            }

            signed_order = await clob_client.create_market_order(order_args)
            resp = await clob_client.post_order(signed_order, "FOK")

            if resp.get("success") is True:
                retry = 0
                total_sold_tokens += order_args["amount"]
                Logger.order_result(True, f"Sold {order_args['amount']} tokens at ${order_args['price']}")
                remaining -= order_args["amount"]
            else:
                error_message = extract_order_error(resp)
                if is_insufficient_balance_or_allowance_error(error_message):
                    abort_due_to_funds = True
                    Logger.warning(f"Order rejected: {error_message or 'Insufficient balance or allowance'}")
                    Logger.warning("Skipping remaining attempts. Top up funds or check allowance before retrying.")
                    break
                retry += 1
                Logger.warning(f"Order failed (attempt {retry}/{RETRY_LIMIT}){f' - {error_message}' if error_message else ''}")

        # Update tracked purchases after successful sell
        if total_sold_tokens > 0 and total_bought_tokens > 0:
            sell_percentage = total_sold_tokens / total_bought_tokens

            if sell_percentage >= 0.99:
                # Sold essentially all tracked tokens - clear tracking
                UserActivity.update_many(
                    {
                        "asset": trade["asset"],
                        "conditionId": trade["conditionId"],
                        "side": DB_FIELDS["SIDE_BUY"],
                        DB_FIELDS["BOT_EXECUTED"]: True,
                        DB_FIELDS["MY_BOUGHT_SIZE"]: {"$exists": True, "$gt": 0},
                    },
                    {"$set": {DB_FIELDS["MY_BOUGHT_SIZE"]: 0}},
                )
                Logger.info(f"🧹 Cleared purchase tracking (sold {(sell_percentage * 100):.1f}% of position)")
            else:
                # Partial sell - reduce tracked purchases proportionally
                for buy in previous_buys:
                    new_size = (buy.get(DB_FIELDS["MY_BOUGHT_SIZE"], 0)) * (1 - sell_percentage)
                    UserActivity.update_one({"_id": buy["_id"]}, {"$set": {DB_FIELDS["MY_BOUGHT_SIZE"]: new_size}})
                Logger.info(f"📝 Updated purchase tracking (sold {(sell_percentage * 100):.1f}% of tracked position)")

        if abort_due_to_funds:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["BOT_EXECUTED_TIME"]: RETRY_LIMIT}},
            )
            return

        if retry >= RETRY_LIMIT:
            UserActivity.update_one(
                {"_id": trade["_id"]},
                {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["BOT_EXECUTED_TIME"]: retry}},
            )
        else:
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})

    else:
        Logger.error(f"Unknown condition: {condition}")
