"""
User interface definitions
"""
from typing import TypedDict, Literal
from bson import ObjectId

TradeSide = Literal["BUY", "SELL"]
ActivityType = Literal["TRADE", "REDEEM", "MERGE"]


class UserActivityInterface(TypedDict, total=False):
    """User activity interface representing a trade or activity"""

    _id: ObjectId
    proxyWallet: str
    timestamp: int
    conditionId: str
    type: ActivityType
    size: float
    usdcSize: float
    transactionHash: str
    price: float
    asset: str
    side: TradeSide
    outcomeIndex: int
    title: str
    slug: str
    icon: str
    eventSlug: str
    outcome: str
    name: str
    pseudonym: str
    bio: str
    profileImage: str
    profileImageOptimized: str
    bot: bool
    botExcutedTime: int
    myBoughtSize: float  # Tracks actual tokens we bought for this trade


class UserPositionInterface(TypedDict, total=False):
    """User position interface representing an open position"""

    _id: ObjectId
    proxyWallet: str
    asset: str
    conditionId: str
    size: float
    avgPrice: float
    initialValue: float
    currentValue: float
    cashPnl: float
    percentPnl: float
    totalBought: float
    realizedPnl: float
    percentRealizedPnl: float
    curPrice: float
    redeemable: bool
    mergeable: bool
    title: str
    slug: str
    icon: str
    eventSlug: str
    outcome: str
    outcomeIndex: int
    oppositeOutcome: str
    oppositeAsset: str
    endDate: str
    negativeRisk: bool


class OrderBookEntry(TypedDict):
    """Order book entry interface"""

    price: str
    size: str


class OrderBook(TypedDict):
    """Order book interface"""

    bids: list[OrderBookEntry]
    asks: list[OrderBookEntry]


class PositionSummary(TypedDict):
    """Position summary for display"""

    title: str
    outcome: str
    currentValue: float
    percentPnl: float
    avgPrice: float
    curPrice: float
