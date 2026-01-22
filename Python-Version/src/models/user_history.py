"""
MongoDB models for user activity and positions
"""
from pymongo import MongoClient
from typing import Any
from ..config.db import get_connection


def get_user_activity_model(wallet_address: str):
    """Get user activity model for a specific wallet address"""
    from ..config.db import get_database
    collection_name = f"user_activities_{wallet_address}"
    db = get_database()
    return db[collection_name]


def get_user_position_model(wallet_address: str):
    """Get user position model for a specific wallet address"""
    from ..config.db import get_database
    collection_name = f"user_positions_{wallet_address}"
    db = get_database()
    return db[collection_name]


def create_indexes(wallet_address: str) -> None:
    """Create indexes for user collections"""
    # Activity indexes
    activity_collection = get_user_activity_model(wallet_address)
    activity_collection.create_index("transactionHash")
    activity_collection.create_index("timestamp")
    activity_collection.create_index([("timestamp", -1)])
    activity_collection.create_index([("conditionId", 1), ("timestamp", -1)])
    activity_collection.create_index([("type", 1), ("timestamp", -1)])
    activity_collection.create_index([("side", 1), ("timestamp", -1)])
    activity_collection.create_index([("bot", 1), ("botExcutedTime", 1)])

    # Position indexes
    position_collection = get_user_position_model(wallet_address)
    position_collection.create_index([("conditionId", 1), ("asset", 1)])
    position_collection.create_index([("proxyWallet", 1), ("conditionId", 1)])
    position_collection.create_index([("currentValue", -1)])
    position_collection.create_index([("percentPnl", -1)])
