"""
Copy Trading Strategy Configuration

This module defines the strategy for copying trades from followed traders.
Three strategies are supported:
- PERCENTAGE: Copy a fixed percentage of trader's order size
- FIXED: Copy a fixed dollar amount per trade
- ADAPTIVE: Dynamically adjust percentage based on trader's order size
"""
from enum import Enum
from typing import TypedDict, Optional


class CopyStrategy(str, Enum):
    """Copy strategy types"""

    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"
    ADAPTIVE = "ADAPTIVE"


class MultiplierTier(TypedDict):
    """Tier definition for tiered multipliers"""

    min: float  # Minimum trade size in USD (inclusive)
    max: Optional[float]  # Maximum trade size in USD (exclusive), None = infinity
    multiplier: float  # Multiplier to apply


class CopyStrategyConfig(TypedDict, total=False):
    """Copy strategy configuration"""

    # Core strategy
    strategy: CopyStrategy

    # Main parameter (meaning depends on strategy)
    # PERCENTAGE: Percentage of trader's order (e.g., 10.0 = 10%)
    # FIXED: Fixed dollar amount per trade (e.g., 50.0 = $50)
    # ADAPTIVE: Base percentage for adaptive scaling
    copySize: float

    # Adaptive strategy parameters (only used if strategy = ADAPTIVE)
    adaptiveMinPercent: Optional[float]  # Minimum percentage for large orders
    adaptiveMaxPercent: Optional[float]  # Maximum percentage for small orders
    adaptiveThreshold: Optional[float]  # Threshold in USD to trigger adaptation

    # Tiered multipliers (optional - applies to all strategies)
    # If set, multiplier is applied based on trader's order size
    tieredMultipliers: Optional[list[MultiplierTier]]

    # Legacy single multiplier (for backward compatibility)
    # Ignored if tieredMultipliers is set
    tradeMultiplier: Optional[float]

    # Safety limits
    maxOrderSizeUSD: float  # Maximum size for a single order
    minOrderSizeUSD: float  # Minimum size for a single order
    maxPositionSizeUSD: Optional[float]  # Maximum total size for a position (optional)
    maxDailyVolumeUSD: Optional[float]  # Maximum total volume per day (optional)


class OrderSizeCalculation(TypedDict):
    """Order size calculation result"""

    traderOrderSize: float  # Original trader's order size
    baseAmount: float  # Calculated amount before limits
    finalAmount: float  # Final amount after applying limits
    strategy: CopyStrategy  # Strategy used
    cappedByMax: bool  # Whether capped by MAX_ORDER_SIZE
    reducedByBalance: bool  # Whether reduced due to balance
    belowMinimum: bool  # Whether below minimum threshold
    reasoning: str  # Human-readable explanation


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values"""
    return a + (b - a) * max(0, min(1, t))


def calculate_adaptive_percent(config: CopyStrategyConfig, trader_order_size: float) -> float:
    """
    Calculate adaptive percentage based on trader's order size

    Logic:
    - Small orders (< threshold): Use higher percentage (up to maxPercent)
    - Large orders (> threshold): Use lower percentage (down to minPercent)
    - Medium orders: Linear interpolation between copySize and min/max
    """
    min_percent = config.get("adaptiveMinPercent") or config["copySize"]
    max_percent = config.get("adaptiveMaxPercent") or config["copySize"]
    threshold = config.get("adaptiveThreshold") or 500.0

    if trader_order_size >= threshold:
        # Large order: scale down to minPercent
        # At threshold = minPercent, at 10x threshold = minPercent
        factor = min(1, trader_order_size / threshold - 1)
        return lerp(config["copySize"], min_percent, factor)
    else:
        # Small order: scale up to maxPercent
        # At $0 = maxPercent, at threshold = copySize
        factor = trader_order_size / threshold
        return lerp(max_percent, config["copySize"], factor)


def get_trade_multiplier(config: CopyStrategyConfig, trader_order_size: float) -> float:
    """
    Get the appropriate multiplier for a given trade size

    Args:
        config: Copy strategy configuration
        trader_order_size: Trader's order size in USD

    Returns:
        Multiplier to apply (1.0 if no multiplier configured)
    """
    # Use tiered multipliers if configured
    tiered_multipliers = config.get("tieredMultipliers")
    if tiered_multipliers and len(tiered_multipliers) > 0:
        for tier in tiered_multipliers:
            if trader_order_size >= tier["min"]:
                if tier["max"] is None or trader_order_size < tier["max"]:
                    return tier["multiplier"]
        # If no tier matches, use the last tier's multiplier
        return tiered_multipliers[-1]["multiplier"]

    # Fall back to single multiplier if configured
    trade_multiplier = config.get("tradeMultiplier")
    if trade_multiplier is not None:
        return trade_multiplier

    # Default: no multiplier
    return 1.0


def calculate_order_size(
    config: CopyStrategyConfig,
    trader_order_size: float,
    available_balance: float,
    current_position_size: float = 0,
) -> OrderSizeCalculation:
    """Calculate order size based on copy strategy"""
    base_amount: float
    reasoning: str

    # Step 1: Calculate base amount based on strategy
    strategy = config["strategy"]
    if strategy == CopyStrategy.PERCENTAGE:
        base_amount = trader_order_size * (config["copySize"] / 100)
        reasoning = f"{config['copySize']}% of trader's ${trader_order_size:.2f} = ${base_amount:.2f}"
    elif strategy == CopyStrategy.FIXED:
        base_amount = config["copySize"]
        reasoning = f"Fixed amount: ${base_amount:.2f}"
    elif strategy == CopyStrategy.ADAPTIVE:
        adaptive_percent = calculate_adaptive_percent(config, trader_order_size)
        base_amount = trader_order_size * (adaptive_percent / 100)
        reasoning = f"Adaptive {adaptive_percent:.1f}% of trader's ${trader_order_size:.2f} = ${base_amount:.2f}"
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Step 1.5: Apply tiered or single multiplier based on trader's order size
    multiplier = get_trade_multiplier(config, trader_order_size)
    final_amount = base_amount * multiplier

    if multiplier != 1.0:
        reasoning += f" → {multiplier}x multiplier: ${base_amount:.2f} → ${final_amount:.2f}"

    capped_by_max = False
    reduced_by_balance = False
    below_minimum = False

    # Step 2: Apply maximum order size limit
    if final_amount > config["maxOrderSizeUSD"]:
        final_amount = config["maxOrderSizeUSD"]
        capped_by_max = True
        reasoning += f" → Capped at max ${config['maxOrderSizeUSD']}"

    # Step 3: Apply maximum position size limit (if configured)
    max_position_size = config.get("maxPositionSizeUSD")
    if max_position_size:
        new_total_position = current_position_size + final_amount
        if new_total_position > max_position_size:
            allowed_amount = max(0, max_position_size - current_position_size)
            if allowed_amount < config["minOrderSizeUSD"]:
                final_amount = 0
                reasoning += " → Position limit reached"
            else:
                final_amount = allowed_amount
                reasoning += " → Reduced to fit position limit"

    # Step 4: Check available balance (with 1% safety buffer)
    max_affordable = available_balance * 0.99
    if final_amount > max_affordable:
        final_amount = max_affordable
        reduced_by_balance = True
        reasoning += f" → Reduced to fit balance (${max_affordable:.2f})"

    # Step 5: Check minimum order size
    if final_amount < config["minOrderSizeUSD"]:
        below_minimum = True
        reasoning += f" → Below minimum ${config['minOrderSizeUSD']}"
        final_amount = 0  # Don't execute

    return {
        "traderOrderSize": trader_order_size,
        "baseAmount": base_amount,
        "finalAmount": final_amount,
        "strategy": strategy,
        "cappedByMax": capped_by_max,
        "reducedByBalance": reduced_by_balance,
        "belowMinimum": below_minimum,
        "reasoning": reasoning,
    }


def validate_copy_strategy_config(config: CopyStrategyConfig) -> list[str]:
    """Validate copy strategy configuration"""
    errors: list[str] = []

    # Validate copySize
    if config["copySize"] <= 0:
        errors.append("copySize must be positive")

    if config["strategy"] == CopyStrategy.PERCENTAGE and config["copySize"] > 100:
        errors.append("copySize for PERCENTAGE strategy should be <= 100")

    # Validate limits
    if config["maxOrderSizeUSD"] <= 0:
        errors.append("maxOrderSizeUSD must be positive")

    if config["minOrderSizeUSD"] <= 0:
        errors.append("minOrderSizeUSD must be positive")

    if config["minOrderSizeUSD"] > config["maxOrderSizeUSD"]:
        errors.append("minOrderSizeUSD cannot be greater than maxOrderSizeUSD")

    # Validate adaptive parameters
    if config["strategy"] == CopyStrategy.ADAPTIVE:
        if not config.get("adaptiveMinPercent") or not config.get("adaptiveMaxPercent"):
            errors.append("ADAPTIVE strategy requires adaptiveMinPercent and adaptiveMaxPercent")

        adaptive_min = config.get("adaptiveMinPercent")
        adaptive_max = config.get("adaptiveMaxPercent")
        if adaptive_min and adaptive_max and adaptive_min > adaptive_max:
            errors.append("adaptiveMinPercent cannot be greater than adaptiveMaxPercent")

    return errors


def parse_tiered_multipliers(tiers_str: str) -> list[MultiplierTier]:
    """
    Parse tiered multipliers from environment string
    Format: "1-10:2.0,10-100:1.0,100-500:0.2,500+:0.1"

    Args:
        tiers_str: Comma-separated tier definitions

    Returns:
        Array of MultiplierTier objects, sorted by min value

    Raises:
        ValueError: If format is invalid
    """
    if not tiers_str or tiers_str.strip() == "":
        return []

    tiers: list[MultiplierTier] = []
    tier_defs = [t.strip() for t in tiers_str.split(",") if t.strip()]

    for tier_def in tier_defs:
        # Format: "min-max:multiplier" or "min+:multiplier"
        parts = tier_def.split(":")
        if len(parts) != 2:
            raise ValueError(f'Invalid tier format: "{tier_def}". Expected "min-max:multiplier" or "min+:multiplier"')

        range_str, multiplier_str = parts
        try:
            multiplier = float(multiplier_str)
        except ValueError:
            raise ValueError(f'Invalid multiplier in tier "{tier_def}": {multiplier_str}')

        if multiplier < 0:
            raise ValueError(f'Invalid multiplier in tier "{tier_def}": {multiplier_str}')

        # Parse range
        if range_str.endswith("+"):
            # Infinite upper bound: "500+"
            try:
                min_val = float(range_str[:-1])
            except ValueError:
                raise ValueError(f'Invalid minimum value in tier "{tier_def}": {range_str}')
            if min_val < 0:
                raise ValueError(f'Invalid minimum value in tier "{tier_def}": {range_str}')
            tiers.append({"min": min_val, "max": None, "multiplier": multiplier})
        elif "-" in range_str:
            # Bounded range: "100-500"
            range_parts = range_str.split("-")
            if len(range_parts) != 2 or not range_parts[0] or not range_parts[1]:
                raise ValueError(f'Invalid range format in tier "{tier_def}": "{range_str}"')

            try:
                min_val = float(range_parts[0])
                max_val = float(range_parts[1])
            except ValueError as e:
                raise ValueError(f'Invalid range values in tier "{tier_def}": {e}')

            if min_val < 0:
                raise ValueError(f'Invalid minimum value in tier "{tier_def}": {range_parts[0]}')
            if max_val <= min_val:
                raise ValueError(
                    f'Invalid maximum value in tier "{tier_def}": {range_parts[1]} (must be > {min_val})'
                )

            tiers.append({"min": min_val, "max": max_val, "multiplier": multiplier})
        else:
            raise ValueError(f'Invalid range format in tier "{tier_def}". Use "min-max" or "min+"')

    # Sort tiers by min value
    tiers.sort(key=lambda t: t["min"])

    # Validate no overlaps and no gaps
    for i in range(len(tiers) - 1):
        current = tiers[i]
        next_tier = tiers[i + 1]

        if current["max"] is None:
            raise ValueError(f"Tier with infinite upper bound must be last: {current['min']}+")

        if current["max"] > next_tier["min"]:
            raise ValueError(
                f"Overlapping tiers: [{current['min']}-{current['max']}] and [{next_tier['min']}-{next_tier['max'] or '∞'}]"
            )

    return tiers


def get_recommended_config(balance_usd: float) -> CopyStrategyConfig:
    """Get recommended configuration for different balance sizes"""
    if balance_usd < 500:
        # Small balance: Conservative
        return {
            "strategy": CopyStrategy.PERCENTAGE,
            "copySize": 5.0,
            "maxOrderSizeUSD": 20.0,
            "minOrderSizeUSD": 1.0,
            "maxPositionSizeUSD": 50.0,
            "maxDailyVolumeUSD": 100.0,
        }
    elif balance_usd < 2000:
        # Medium balance: Balanced
        return {
            "strategy": CopyStrategy.PERCENTAGE,
            "copySize": 10.0,
            "maxOrderSizeUSD": 50.0,
            "minOrderSizeUSD": 1.0,
            "maxPositionSizeUSD": 200.0,
            "maxDailyVolumeUSD": 500.0,
        }
    else:
        # Large balance: Adaptive
        return {
            "strategy": CopyStrategy.ADAPTIVE,
            "copySize": 10.0,
            "adaptiveMinPercent": 5.0,
            "adaptiveMaxPercent": 15.0,
            "adaptiveThreshold": 300.0,
            "maxOrderSizeUSD": 100.0,
            "minOrderSizeUSD": 1.0,
            "maxPositionSizeUSD": 1000.0,
            "maxDailyVolumeUSD": 2000.0,
        }
