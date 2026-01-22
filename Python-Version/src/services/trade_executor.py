"""
Trade executor service - monitors database for new trades and executes them
"""
import asyncio
import time
from typing import Any
from ..config.env import ENV
from ..models.user_history import get_user_activity_model
from ..utils.fetch_data import fetch_data
from ..utils.get_my_balance import get_my_balance
from ..utils.post_order import post_order
from ..utils.logger import Logger
from ..utils.constants import TRADING_CONSTANTS, DB_FIELDS, TIME_CONSTANTS
from ..utils.constants import POLYMARKET_API
from ..interfaces.user import UserPositionInterface, UserActivityInterface, TradeSide

USER_ADDRESSES = ENV["USER_ADDRESSES"]
RETRY_LIMIT = ENV["RETRY_LIMIT"]
PROXY_WALLET = ENV["PROXY_WALLET"]
TRADE_AGGREGATION_ENABLED = ENV["TRADE_AGGREGATION_ENABLED"]
TRADE_AGGREGATION_WINDOW_SECONDS = ENV["TRADE_AGGREGATION_WINDOW_SECONDS"]
TRADE_AGGREGATION_MIN_TOTAL_USD = TRADING_CONSTANTS["TRADE_AGGREGATION_MIN_TOTAL_USD"]

# Store addresses - models will be created lazily after DB connection
_user_addresses = USER_ADDRESSES


def get_user_activity_models():
    """Get user activity models - creates them lazily after DB connection"""
    return [
        {"address": address, "model": get_user_activity_model(address)} for address in _user_addresses
    ]

# Buffer for aggregating trades
trade_aggregation_buffer: dict[str, dict[str, Any]] = {}


def get_aggregation_key(trade: dict[str, Any], user_address: str) -> str:
    """Generate a unique key for trade aggregation based on user, market, side"""
    return f"{user_address}:{trade.get('conditionId')}:{trade.get('asset')}:{trade.get('side')}"


def add_to_aggregation_buffer(trade: dict[str, Any], user_address: str) -> None:
    """Add trade to aggregation buffer or update existing aggregation"""
    key = get_aggregation_key(trade, user_address)
    existing = trade_aggregation_buffer.get(key)
    now = int(time.time() * 1000)

    if existing:
        # Update existing aggregation
        existing["trades"].append(trade)
        existing["totalUsdcSize"] += trade.get("usdcSize", 0)
        # Recalculate weighted average price
        total_value = sum(t.get("usdcSize", 0) * t.get("price", 0) for t in existing["trades"])
        existing["averagePrice"] = total_value / existing["totalUsdcSize"] if existing["totalUsdcSize"] > 0 else 0
        existing["lastTradeTime"] = now
    else:
        # Create new aggregation
        trade_aggregation_buffer[key] = {
            "userAddress": user_address,
            "conditionId": trade.get("conditionId"),
            "asset": trade.get("asset"),
            "side": trade.get("side", DB_FIELDS["SIDE_BUY"]),
            "slug": trade.get("slug"),
            "eventSlug": trade.get("eventSlug"),
            "trades": [trade],
            "totalUsdcSize": trade.get("usdcSize", 0),
            "averagePrice": trade.get("price", 0),
            "firstTradeTime": now,
            "lastTradeTime": now,
        }


def get_ready_aggregated_trades() -> list[dict[str, Any]]:
    """Check buffer and return ready aggregated trades"""
    ready = []
    now = int(time.time() * 1000)
    window_ms = TRADE_AGGREGATION_WINDOW_SECONDS * TIME_CONSTANTS["SECOND_MS"]

    keys_to_remove = []
    for key, agg in trade_aggregation_buffer.items():
        time_elapsed = now - agg["firstTradeTime"]

        # Check if aggregation is ready
        if time_elapsed >= window_ms:
            if agg["totalUsdcSize"] >= TRADE_AGGREGATION_MIN_TOTAL_USD:
                # Aggregation meets minimum and window passed - ready to execute
                ready.append(agg)
            else:
                # Window passed but total too small - mark individual trades as skipped
                Logger.info(
                    f"Trade aggregation for {agg['userAddress']} on {agg.get('slug') or agg.get('asset')}: ${agg['totalUsdcSize']:.2f} total from {len(agg['trades'])} trades below minimum (${TRADE_AGGREGATION_MIN_TOTAL_USD}) - skipping"
                )

                # Mark all trades in this aggregation as processed
                for trade in agg["trades"]:
                    UserActivity = get_user_activity_model(agg["userAddress"])
                    UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED"]: True}})

            keys_to_remove.append(key)

    # Remove processed aggregations
    for key in keys_to_remove:
        trade_aggregation_buffer.pop(key, None)

    return ready


async def read_temp_trades() -> list[dict[str, Any]]:
    """Read unprocessed trades from database"""
    all_trades = []
    user_activity_models = get_user_activity_models()

    for model in user_activity_models:
        # Only get trades that haven't been processed yet
        trades = list(
            model["model"].find(
                {
                    "type": DB_FIELDS["TYPE_TRADE"],
                    DB_FIELDS["BOT_EXECUTED"]: False,
                    DB_FIELDS["BOT_EXECUTED_TIME"]: 0,
                }
            )
        )

        trades_with_user = [{**trade, "userAddress": model["address"]} for trade in trades]
        all_trades.extend(trades_with_user)

    return all_trades


async def do_trading(clob_client: Any, trades: list[dict[str, Any]]) -> None:
    """Execute individual trades"""
    for trade in trades:
        # Mark trade as being processed immediately
        UserActivity = get_user_activity_model(trade["userAddress"])
        UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED_TIME"]: 1}})

        Logger.trade(
            trade["userAddress"],
            trade.get("side", "UNKNOWN"),
            {
                "asset": trade.get("asset"),
                "side": trade.get("side"),
                "amount": trade.get("usdcSize", 0),
                "price": trade.get("price", 0),
                "slug": trade.get("slug"),
                "eventSlug": trade.get("eventSlug"),
                "transactionHash": trade.get("transactionHash"),
            },
        )

        my_positions = fetch_data(
            f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['POSITIONS_ENDPOINT']}?user={PROXY_WALLET}"
        )
        user_positions = fetch_data(
            f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['POSITIONS_ENDPOINT']}?user={trade['userAddress']}"
        )

        my_position = next(
            (pos for pos in my_positions if pos.get("conditionId") == trade.get("conditionId")), None
        ) if isinstance(my_positions, list) else None
        user_position = next(
            (pos for pos in user_positions if pos.get("conditionId") == trade.get("conditionId")), None
        ) if isinstance(user_positions, list) else None

        # Get USDC balance
        my_balance = get_my_balance(PROXY_WALLET)

        # Calculate trader's total portfolio value from positions
        user_balance = sum(pos.get("currentValue", 0) or 0 for pos in user_positions) if isinstance(user_positions, list) else 0

        Logger.balance(my_balance, user_balance, trade["userAddress"])

        # Determine condition
        condition = "buy" if trade.get("side") == "BUY" else "sell"

        # Execute the trade
        await post_order(
            clob_client,
            condition,
            my_position,
            user_position,
            trade,
            my_balance,
            user_balance,
            trade["userAddress"],
        )

        Logger.separator()


async def do_aggregated_trading(clob_client: Any, aggregated_trades: list[dict[str, Any]]) -> None:
    """Execute aggregated trades"""
    for agg in aggregated_trades:
        Logger.header(f"📊 AGGREGATED TRADE ({len(agg['trades'])} trades combined)")
        Logger.info(f"Market: {agg.get('slug') or agg.get('asset')}")
        Logger.info(f"Side: {agg['side']}")
        Logger.info(f"Total volume: ${agg['totalUsdcSize']:.2f}")
        Logger.info(f"Average price: ${agg['averagePrice']:.4f}")

        # Mark all individual trades as being processed
        for trade in agg["trades"]:
            UserActivity = get_user_activity_model(agg["userAddress"])
            UserActivity.update_one({"_id": trade["_id"]}, {"$set": {DB_FIELDS["BOT_EXECUTED_TIME"]: 1}})

        my_positions = fetch_data(
            f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['POSITIONS_ENDPOINT']}?user={PROXY_WALLET}"
        )
        user_positions = fetch_data(
            f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['POSITIONS_ENDPOINT']}?user={agg['userAddress']}"
        )

        my_position = next(
            (pos for pos in my_positions if pos.get("conditionId") == agg.get("conditionId")), None
        ) if isinstance(my_positions, list) else None
        user_position = next(
            (pos for pos in user_positions if pos.get("conditionId") == agg.get("conditionId")), None
        ) if isinstance(user_positions, list) else None

        # Get USDC balance
        my_balance = get_my_balance(PROXY_WALLET)

        # Calculate trader's total portfolio value
        user_balance = sum(pos.get("currentValue", 0) or 0 for pos in user_positions) if isinstance(user_positions, list) else 0

        Logger.balance(my_balance, user_balance, agg["userAddress"])

        # Create a synthetic trade object for postOrder using aggregated values
        synthetic_trade = {
            **agg["trades"][0],  # Use first trade as template
            "usdcSize": agg["totalUsdcSize"],
            "price": agg["averagePrice"],
            "side": agg["side"],
        }

        # Execute the aggregated trade
        condition = "buy" if agg["side"] == "BUY" else "sell"
        await post_order(
            clob_client,
            condition,
            my_position,
            user_position,
            synthetic_trade,
            my_balance,
            user_balance,
            agg["userAddress"],
        )

        Logger.separator()


_is_running = True


def stop_trade_executor() -> None:
    """Stop the trade executor gracefully"""
    global _is_running
    _is_running = False
    Logger.info("Trade executor shutdown requested...")


async def trade_executor(clob_client: Any) -> None:
    """Main trade executor function - monitors database for new trades and executes them"""
    Logger.success(f"Trade executor ready for {len(USER_ADDRESSES)} trader(s)")
    if TRADE_AGGREGATION_ENABLED:
        Logger.info(
            f"Trade aggregation enabled: {TRADE_AGGREGATION_WINDOW_SECONDS}s window, ${TRADE_AGGREGATION_MIN_TOTAL_USD} minimum"
        )

    last_check = int(time.time() * 1000)

    while _is_running:
        trades = await read_temp_trades()

        if TRADE_AGGREGATION_ENABLED:
            # Process with aggregation logic
            if len(trades) > 0:
                Logger.clear_line()
                Logger.info(f"📥 {len(trades)} new trade{'s' if len(trades) > 1 else ''} detected")

                # Add trades to aggregation buffer
                for trade in trades:
                    # Only aggregate BUY trades below minimum threshold
                    if trade.get("side") == DB_FIELDS["SIDE_BUY"] and trade.get("usdcSize", 0) < TRADE_AGGREGATION_MIN_TOTAL_USD:
                        Logger.info(
                            f"Adding ${trade.get('usdcSize', 0):.2f} {trade.get('side')} trade to aggregation buffer for {trade.get('slug') or trade.get('asset')}"
                        )
                        add_to_aggregation_buffer(trade, trade["userAddress"])
                    else:
                        # Execute large trades immediately (not aggregated)
                        Logger.clear_line()
                        Logger.header("⚡ IMMEDIATE TRADE (above threshold)")
                        await do_trading(clob_client, [trade])

                last_check = int(time.time() * 1000)

            # Check for ready aggregated trades
            ready_aggregations = get_ready_aggregated_trades()
            if len(ready_aggregations) > 0:
                Logger.clear_line()
                Logger.header(f"⚡ {len(ready_aggregations)} AGGREGATED TRADE{'S' if len(ready_aggregations) > 1 else ''} READY")
                await do_aggregated_trading(clob_client, ready_aggregations)
                last_check = int(time.time() * 1000)

            # Update waiting message
            if len(trades) == 0 and len(ready_aggregations) == 0:
                if int(time.time() * 1000) - last_check > 300:
                    buffered_count = len(trade_aggregation_buffer)
                    if buffered_count > 0:
                        Logger.waiting(len(USER_ADDRESSES), f"{buffered_count} trade group(s) pending")
                    else:
                        Logger.waiting(len(USER_ADDRESSES))
                    last_check = int(time.time() * 1000)
        else:
            # Original non-aggregation logic
            if len(trades) > 0:
                Logger.clear_line()
                Logger.header(f"⚡ {len(trades)} NEW TRADE{'S' if len(trades) > 1 else ''} TO COPY")
                await do_trading(clob_client, trades)
                last_check = int(time.time() * 1000)
            else:
                # Update waiting message every 300ms for smooth animation
                if int(time.time() * 1000) - last_check > 300:
                    Logger.waiting(len(USER_ADDRESSES))
                    last_check = int(time.time() * 1000)

        if not _is_running:
            break
        await asyncio.sleep(0.3)  # 300ms polling interval

    Logger.info("Trade executor stopped")
