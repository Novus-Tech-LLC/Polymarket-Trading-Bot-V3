"""
Trade monitor service - monitors traders for new trades and updates database
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Any
from ..config.env import ENV
from ..models.user_history import get_user_activity_model, get_user_position_model
from ..utils.fetch_data import fetch_data
from ..utils.logger import Logger
from ..utils.constants import POLYMARKET_API, DB_FIELDS, TIME_CONSTANTS
from ..utils.get_my_balance import get_my_balance
from ..interfaces.user import UserPositionInterface, UserActivityInterface

USER_ADDRESSES = ENV["USER_ADDRESSES"]
TOO_OLD_TIMESTAMP = ENV["TOO_OLD_TIMESTAMP"]
FETCH_INTERVAL = ENV["FETCH_INTERVAL"]

if not USER_ADDRESSES or len(USER_ADDRESSES) == 0:
    raise ValueError("USER_ADDRESSES is not defined or empty")

# Store addresses - models will be created lazily after DB connection
_user_addresses = USER_ADDRESSES


def get_user_models():
    """Get user models - creates them lazily after DB connection"""
    return [
        {"address": address, "UserActivity": get_user_activity_model(address), "UserPosition": get_user_position_model(address)}
        for address in _user_addresses
    ]

_is_running = True


def stop_trade_monitor() -> None:
    """Stop the trade monitor gracefully"""
    global _is_running
    _is_running = False
    Logger.info("Trade monitor shutdown requested...")


async def init() -> None:
    """Initialize trade monitor and display current status"""
    user_models = get_user_models()
    counts = []
    for model in user_models:
        count = model["UserActivity"].count_documents({})
        counts.append(count)
    Logger.clear_line()
    Logger.db_connection(USER_ADDRESSES, counts)

    # Show your own positions first
    try:
        my_positions_url = f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['POSITIONS_ENDPOINT']}?user={ENV['PROXY_WALLET']}"
        my_positions = fetch_data(my_positions_url)

        # Get current USDC balance
        from ..utils.get_my_balance import get_my_balance
        current_balance = get_my_balance(ENV["PROXY_WALLET"])

        if isinstance(my_positions, list) and len(my_positions) > 0:
            # Calculate your overall profitability and initial investment
            total_value = 0
            initial_value = 0
            weighted_pnl = 0
            for pos in my_positions:
                value = pos.get("currentValue", 0) or 0
                initial = pos.get("initialValue", 0) or 0
                pnl = pos.get("percentPnl", 0) or 0
                total_value += value
                initial_value += initial
                weighted_pnl += value * pnl
            my_overall_pnl = weighted_pnl / total_value if total_value > 0 else 0

            # Get top 5 positions by profitability (PnL)
            my_top_positions = sorted(my_positions, key=lambda p: p.get("percentPnl", 0) or 0, reverse=True)[:5]

            Logger.clear_line()
            Logger.my_positions(
                ENV["PROXY_WALLET"],
                len(my_positions),
                my_top_positions,
                my_overall_pnl,
                total_value,
                initial_value,
                current_balance,
            )
        else:
            Logger.clear_line()
            Logger.my_positions(ENV["PROXY_WALLET"], 0, [], 0, 0, 0, current_balance)
    except Exception as error:
        Logger.error(f"Failed to fetch your positions: {error}")

    # Show current positions count with details for traders you're copying
    position_counts = []
    position_details = []
    profitabilities = []

    for model in user_models:
        positions = list(model["UserPosition"].find())
        position_counts.append(len(positions))

        # Calculate overall profitability (weighted average by current value)
        total_value = 0
        weighted_pnl = 0
        for pos in positions:
            value = pos.get("currentValue", 0) or 0
            pnl = pos.get("percentPnl", 0) or 0
            total_value += value
            weighted_pnl += value * pnl
        overall_pnl = weighted_pnl / total_value if total_value > 0 else 0
        profitabilities.append(overall_pnl)

        # Get top 3 positions by profitability (PnL)
        top_positions = sorted(positions, key=lambda p: p.get("percentPnl", 0) or 0, reverse=True)[:3]
        top_positions = [
            pos
            for pos in top_positions
            if pos.get("proxyWallet") and isinstance(pos.get("proxyWallet"), str)
        ]
        position_details.append(top_positions)

    Logger.clear_line()
    Logger.traders_positions(USER_ADDRESSES, position_counts, position_details, profitabilities)


async def fetch_trade_data() -> None:
    """Fetch and process trade data from Polymarket API"""
    cutoff_timestamp = int((datetime.now() - timedelta(hours=TOO_OLD_TIMESTAMP)).timestamp() * 1000)
    user_models = get_user_models()

    for model in user_models:
        try:
            address = model["address"]
            UserActivity = model["UserActivity"]
            UserPosition = model["UserPosition"]

            # Fetch trade activities from Polymarket API
            api_url = f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['ACTIVITY_ENDPOINT']}?user={address}&type={DB_FIELDS['TYPE_TRADE']}"
            activities = fetch_data(api_url)

            if not isinstance(activities, list) or len(activities) == 0:
                continue

            # Process each activity
            for activity in activities:
                # Skip if too old
                if activity.get("timestamp", 0) < cutoff_timestamp:
                    continue

                # Check if this trade already exists in database
                existing_activity = UserActivity.find_one({"transactionHash": activity.get("transactionHash")})

                if existing_activity:
                    continue  # Already processed this trade

                # Save new trade to database
                new_activity = {
                    "proxyWallet": activity.get("proxyWallet"),
                    "timestamp": activity.get("timestamp"),
                    "conditionId": activity.get("conditionId"),
                    "type": activity.get("type"),
                    "size": activity.get("size", 0),
                    "usdcSize": activity.get("usdcSize", 0),
                    "transactionHash": activity.get("transactionHash"),
                    "price": activity.get("price", 0),
                    "asset": activity.get("asset"),
                    "side": activity.get("side"),
                    "outcomeIndex": activity.get("outcomeIndex"),
                    "title": activity.get("title"),
                    "slug": activity.get("slug"),
                    "icon": activity.get("icon"),
                    "eventSlug": activity.get("eventSlug"),
                    "outcome": activity.get("outcome"),
                    "name": activity.get("name"),
                    "pseudonym": activity.get("pseudonym"),
                    "bio": activity.get("bio"),
                    "profileImage": activity.get("profileImage"),
                    "profileImageOptimized": activity.get("profileImageOptimized"),
                    "bot": False,
                    "botExcutedTime": 0,
                }

                UserActivity.insert_one(new_activity)
                Logger.info(f"New trade detected for {address[:6]}...{address[-4:]}")

            # Also fetch and update positions
            positions_url = f"{POLYMARKET_API['DATA_API_BASE']}{POLYMARKET_API['POSITIONS_ENDPOINT']}?user={address}"
            positions = fetch_data(positions_url)

            if isinstance(positions, list) and len(positions) > 0:
                for position in positions:
                    # Update or create position
                    UserPosition.update_one(
                        {"asset": position.get("asset"), "conditionId": position.get("conditionId")},
                        {
                            "$set": {
                                "proxyWallet": position.get("proxyWallet"),
                                "asset": position.get("asset"),
                                "conditionId": position.get("conditionId"),
                                "size": position.get("size", 0),
                                "avgPrice": position.get("avgPrice", 0),
                                "initialValue": position.get("initialValue", 0),
                                "currentValue": position.get("currentValue", 0),
                                "cashPnl": position.get("cashPnl", 0),
                                "percentPnl": position.get("percentPnl", 0),
                                "totalBought": position.get("totalBought", 0),
                                "realizedPnl": position.get("realizedPnl", 0),
                                "percentRealizedPnl": position.get("percentRealizedPnl", 0),
                                "curPrice": position.get("curPrice", 0),
                                "redeemable": position.get("redeemable", False),
                                "mergeable": position.get("mergeable", False),
                                "title": position.get("title"),
                                "slug": position.get("slug"),
                                "icon": position.get("icon"),
                                "eventSlug": position.get("eventSlug"),
                                "outcome": position.get("outcome"),
                                "outcomeIndex": position.get("outcomeIndex"),
                                "oppositeOutcome": position.get("oppositeOutcome"),
                                "oppositeAsset": position.get("oppositeAsset"),
                                "endDate": position.get("endDate"),
                                "negativeRisk": position.get("negativeRisk", False),
                            }
                        },
                        upsert=True,
                    )
        except Exception as error:
            Logger.error(f"Error fetching data for {model['address'][:6]}...{model['address'][-4:]}: {error}")


_is_first_run = True


async def trade_monitor() -> None:
    """Main trade monitor function - monitors traders for new trades and updates database"""
    await init()
    Logger.success(f"Monitoring {len(USER_ADDRESSES)} trader(s) every {FETCH_INTERVAL}s")
    Logger.separator()

    # On first run, mark all existing historical trades as already processed
    global _is_first_run
    if _is_first_run:
        Logger.info("First run: marking all historical trades as processed...")
        user_models = get_user_models()
        for model in user_models:
            result = model["UserActivity"].update_many(
                {DB_FIELDS["BOT_EXECUTED"]: False},
                {"$set": {DB_FIELDS["BOT_EXECUTED"]: True, DB_FIELDS["BOT_EXECUTED_TIME"]: 999}},
            )
            if result.modified_count > 0:
                Logger.info(
                    f"Marked {result.modified_count} historical trades as processed for {model['address'][:6]}...{model['address'][-4:]}"
                )
        _is_first_run = False
        Logger.success("\nHistorical trades processed. Now monitoring for new trades only.")
        Logger.separator()

    while _is_running:
        await fetch_trade_data()
        if not _is_running:
            break
        await asyncio.sleep(FETCH_INTERVAL * TIME_CONSTANTS["SECOND_MS"] / 1000)

    Logger.info("Trade monitor stopped")
