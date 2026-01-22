import { ClobClient } from '@polymarket/clob-client';
import { UserActivityInterface, UserPositionInterface } from '../../domain/types/TraderTypes';
import { ENV } from '../../shared/config/EnvironmentConfig';
import { getTraderActivityRepository } from '../../domain/entities/TraderActivityRepository';
import { HttpClient } from '../../shared/utilities/HttpClient';
import { BalanceService } from '../../shared/utilities/BalanceService';
import { OrderExecutionService } from '../../shared/utilities/OrderExecutionService';
import { LoggingService } from '../../shared/utilities/LoggingService';
import { ApplicationConstants, DatabaseFields, TimeConstants } from '../../shared/utilities/ApplicationConstants';

const USER_ADDRESSES = ENV.USER_ADDRESSES;
const RETRY_LIMIT = ENV.RETRY_LIMIT;
const PROXY_WALLET = ENV.PROXY_WALLET;
const TRADE_AGGREGATION_ENABLED = ENV.TRADE_AGGREGATION_ENABLED;
const TRADE_AGGREGATION_WINDOW_SECONDS = ENV.TRADE_AGGREGATION_WINDOW_SECONDS;
const TRADE_AGGREGATION_MIN_TOTAL_USD = ApplicationConstants.TRADING.TRADE_AGGREGATION_MIN_TOTAL_USD;

// Create activity models for each user
const userActivityModels = USER_ADDRESSES.map((address) => ({
    address,
    model: getTraderActivityRepository(address),
}));

interface TradeWithUser extends UserActivityInterface {
    userAddress: string;
}

interface AggregatedTrade {
    userAddress: string;
    conditionId: string;
    asset: string;
    side: string;
    slug?: string;
    eventSlug?: string;
    trades: TradeWithUser[];
    totalUsdcSize: number;
    averagePrice: number;
    firstTradeTime: number;
    lastTradeTime: number;
}

// Buffer for aggregating trades
const tradeAggregationBuffer: Map<string, AggregatedTrade> = new Map();

/**
 * Read unprocessed trades from database
 * @returns Array of trades with user address attached
 */
const readTempTrades = async (): Promise<TradeWithUser[]> => {
    const allTrades: TradeWithUser[] = [];

    for (const { address, model } of userActivityModels) {
        // Only get trades that haven't been processed yet (bot: false AND botExcutedTime: 0)
        // This prevents processing the same trade multiple times
        const trades = await model
            .find({
                $and: [
                    { type: DatabaseFields.TYPE_TRADE },
                    { [DatabaseFields.BOT_EXECUTED]: false },
                    { [DatabaseFields.BOT_EXECUTED_TIME]: 0 },
                ],
            })
            .exec();

        const tradesWithUser = trades.map((trade) => ({
            ...(trade.toObject() as UserActivityInterface),
            userAddress: address,
        }));

        allTrades.push(...tradesWithUser);
    }

    return allTrades;
};

/**
 * Generate a unique key for trade aggregation based on user, market, side
 * @param trade - Trade to generate key for
 * @returns Unique aggregation key
 */
const getAggregationKey = (trade: TradeWithUser): string => {
    return `${trade.userAddress}:${trade.conditionId}:${trade.asset}:${trade.side}`;
};

/**
 * Add trade to aggregation buffer or update existing aggregation
 * @param trade - Trade to add to buffer
 */
const addToAggregationBuffer = (trade: TradeWithUser): void => {
    const key = getAggregationKey(trade);
    const existing = tradeAggregationBuffer.get(key);
    const now = Date.now();

    if (existing) {
        // Update existing aggregation
        existing.trades.push(trade);
        existing.totalUsdcSize += trade.usdcSize;
        // Recalculate weighted average price
        const totalValue = existing.trades.reduce((sum, t) => sum + t.usdcSize * t.price, 0);
        existing.averagePrice = totalValue / existing.totalUsdcSize;
        existing.lastTradeTime = now;
    } else {
        // Create new aggregation
        tradeAggregationBuffer.set(key, {
            userAddress: trade.userAddress,
            conditionId: trade.conditionId,
            asset: trade.asset,
            side: (trade.side || DatabaseFields.SIDE_BUY) as 'BUY' | 'SELL',
            slug: trade.slug,
            eventSlug: trade.eventSlug,
            trades: [trade],
            totalUsdcSize: trade.usdcSize,
            averagePrice: trade.price,
            firstTradeTime: now,
            lastTradeTime: now,
        });
    }
};

/**
 * Check buffer and return ready aggregated trades
 * Trades are ready if:
 * 1. Total size >= minimum AND
 * 2. Time window has passed since first trade
 * @returns Array of ready aggregated trades
 */
const getReadyAggregatedTrades = (): AggregatedTrade[] => {
    const ready: AggregatedTrade[] = [];
    const now = Date.now();
    const windowMs = TRADE_AGGREGATION_WINDOW_SECONDS * TimeConstants.SECOND_MS;

    for (const [key, agg] of tradeAggregationBuffer.entries()) {
        const timeElapsed = now - agg.firstTradeTime;

        // Check if aggregation is ready
        if (timeElapsed >= windowMs) {
            if (agg.totalUsdcSize >= TRADE_AGGREGATION_MIN_TOTAL_USD) {
                // Aggregation meets minimum and window passed - ready to execute
                ready.push(agg);
            } else {
                // Window passed but total too small - mark individual trades as skipped
                LoggingService.info(
                    `Trade aggregation for ${agg.userAddress} on ${agg.slug || agg.asset}: $${agg.totalUsdcSize.toFixed(2)} total from ${agg.trades.length} trades below minimum ($${TRADE_AGGREGATION_MIN_TOTAL_USD}) - skipping`
                );

                // Mark all trades in this aggregation as processed (bot: true)
                for (const trade of agg.trades) {
                    const UserActivity = getTraderActivityRepository(trade.userAddress);
                    UserActivity.updateOne(
                        { _id: trade._id },
                        { [DatabaseFields.BOT_EXECUTED]: true }
                    ).exec();
                }
            }
            // Remove from buffer either way
            tradeAggregationBuffer.delete(key);
        }
    }

    return ready;
};

/**
 * Execute individual trades
 * @param clobClient - CLOB client instance
 * @param trades - Array of trades to execute
 */
const doTrading = async (clobClient: ClobClient, trades: TradeWithUser[]): Promise<void> => {
    for (const trade of trades) {
        // Mark trade as being processed immediately to prevent duplicate processing
        const UserActivity = getTraderActivityRepository(trade.userAddress);
        await UserActivity.updateOne(
            { _id: trade._id },
            { $set: { [DatabaseFields.BOT_EXECUTED_TIME]: 1 } }
        );

        LoggingService.trade(trade.userAddress, trade.side || 'UNKNOWN', {
            asset: trade.asset,
            side: trade.side,
            amount: trade.usdcSize,
            price: trade.price,
            slug: trade.slug,
            eventSlug: trade.eventSlug,
            transactionHash: trade.transactionHash,
        });

        const my_positions: UserPositionInterface[] = await HttpClient.fetch<UserPositionInterface[]>(
            `${ApplicationConstants.POLYMARKET_API.DATA_API_BASE}${ApplicationConstants.POLYMARKET_API.POSITIONS_ENDPOINT}?user=${PROXY_WALLET}`
        );
        const user_positions: UserPositionInterface[] = await HttpClient.fetch<UserPositionInterface[]>(
            `${ApplicationConstants.POLYMARKET_API.DATA_API_BASE}${ApplicationConstants.POLYMARKET_API.POSITIONS_ENDPOINT}?user=${trade.userAddress}`
        );
        const my_position = my_positions.find(
            (position: UserPositionInterface) => position.conditionId === trade.conditionId
        );
        const user_position = user_positions.find(
            (position: UserPositionInterface) => position.conditionId === trade.conditionId
        );

        // Get USDC balance
        const my_balance = await BalanceService.getBalance(PROXY_WALLET);

        // Calculate trader's total portfolio value from positions
        const user_balance = user_positions.reduce((total, pos) => {
            return total + (pos.currentValue || 0);
        }, 0);

        LoggingService.balance(my_balance, user_balance, trade.userAddress);

        // Execute the trade
        await OrderExecutionService.executeOrder(
            clobClient,
            trade.side === 'BUY' ? 'buy' : 'sell',
            my_position,
            user_position,
            trade,
            my_balance,
            user_balance,
            trade.userAddress
        );

        LoggingService.separator();
    }
};

/**
 * Execute aggregated trades
 * @param clobClient - CLOB client instance
 * @param aggregatedTrades - Array of aggregated trades to execute
 */
const doAggregatedTrading = async (
    clobClient: ClobClient,
    aggregatedTrades: AggregatedTrade[]
): Promise<void> => {
    for (const agg of aggregatedTrades) {
        LoggingService.header(`📊 AGGREGATED TRADE (${agg.trades.length} trades combined)`);
        LoggingService.info(`Market: ${agg.slug || agg.asset}`);
        LoggingService.info(`Side: ${agg.side}`);
        LoggingService.info(`Total volume: $${agg.totalUsdcSize.toFixed(2)}`);
        LoggingService.info(`Average price: $${agg.averagePrice.toFixed(4)}`);

        // Mark all individual trades as being processed
        for (const trade of agg.trades) {
            const UserActivity = getTraderActivityRepository(trade.userAddress);
            await UserActivity.updateOne(
                { _id: trade._id },
                { $set: { [DatabaseFields.BOT_EXECUTED_TIME]: 1 } }
            );
        }

        const my_positions: UserPositionInterface[] = await HttpClient.fetch<UserPositionInterface[]>(
            `${ApplicationConstants.POLYMARKET_API.DATA_API_BASE}${ApplicationConstants.POLYMARKET_API.POSITIONS_ENDPOINT}?user=${PROXY_WALLET}`
        );
        const user_positions: UserPositionInterface[] = await HttpClient.fetch<UserPositionInterface[]>(
            `${ApplicationConstants.POLYMARKET_API.DATA_API_BASE}${ApplicationConstants.POLYMARKET_API.POSITIONS_ENDPOINT}?user=${agg.userAddress}`
        );
        const my_position = my_positions.find(
            (position: UserPositionInterface) => position.conditionId === agg.conditionId
        );
        const user_position = user_positions.find(
            (position: UserPositionInterface) => position.conditionId === agg.conditionId
        );

        // Get USDC balance
        const my_balance = await BalanceService.getBalance(PROXY_WALLET);

        // Calculate trader's total portfolio value from positions
        const user_balance = user_positions.reduce((total, pos) => {
            return total + (pos.currentValue || 0);
        }, 0);

        LoggingService.balance(my_balance, user_balance, agg.userAddress);

        // Create a synthetic trade object for postOrder using aggregated values
        const syntheticTrade: UserActivityInterface = {
            ...agg.trades[0], // Use first trade as template
            usdcSize: agg.totalUsdcSize,
            price: agg.averagePrice,
            side: agg.side,
        };

        // Execute the aggregated trade
        await OrderExecutionService.executeOrder(
            clobClient,
            agg.side === 'BUY' ? 'buy' : 'sell',
            my_position,
            user_position,
            syntheticTrade,
            my_balance,
            user_balance,
            agg.userAddress
        );

        LoggingService.separator();
    }
};

// Track if executor should continue running
let isRunning = true;

/**
 * Stop the trade executor gracefully
 */
export const stopTradeExecutionService = (): void => {
    isRunning = false;
    LoggingService.info('Trade executor shutdown requested...');
};

/**
 * Main trade executor function
 * Monitors database for new trades and executes them
 * @param clobClient - CLOB client instance
 */
const tradeExecutionService = async (clobClient: ClobClient): Promise<void> => {
    LoggingService.success(`Trade executor ready for ${USER_ADDRESSES.length} trader(s)`);
    if (TRADE_AGGREGATION_ENABLED) {
        LoggingService.info(
            `Trade aggregation enabled: ${TRADE_AGGREGATION_WINDOW_SECONDS}s window, $${TRADE_AGGREGATION_MIN_TOTAL_USD} minimum`
        );
    }

    let lastCheck = Date.now();
    while (isRunning) {
        const trades = await readTempTrades();

        if (TRADE_AGGREGATION_ENABLED) {
            // Process with aggregation logic
            if (trades.length > 0) {
                LoggingService.clearLine();
                LoggingService.info(
                    `📥 ${trades.length} new trade${trades.length > 1 ? 's' : ''} detected`
                );

                // Add trades to aggregation buffer
                for (const trade of trades) {
                    // Only aggregate BUY trades below minimum threshold
                    if (
                        trade.side === DatabaseFields.SIDE_BUY &&
                        trade.usdcSize < TRADE_AGGREGATION_MIN_TOTAL_USD
                    ) {
                        LoggingService.info(
                            `Adding $${trade.usdcSize.toFixed(2)} ${trade.side} trade to aggregation buffer for ${trade.slug || trade.asset}`
                        );
                        addToAggregationBuffer(trade);
                    } else {
                        // Execute large trades immediately (not aggregated)
                        LoggingService.clearLine();
                        LoggingService.header(`⚡ IMMEDIATE TRADE (above threshold)`);
                        await doTrading(clobClient, [trade]);
                    }
                }
                lastCheck = Date.now();
            }

            // Check for ready aggregated trades
            const readyAggregations = getReadyAggregatedTrades();
            if (readyAggregations.length > 0) {
                LoggingService.clearLine();
                LoggingService.header(
                    `⚡ ${readyAggregations.length} AGGREGATED TRADE${readyAggregations.length > 1 ? 'S' : ''} READY`
                );
                await doAggregatedTrading(clobClient, readyAggregations);
                lastCheck = Date.now();
            }

            // Update waiting message
            if (trades.length === 0 && readyAggregations.length === 0) {
                if (Date.now() - lastCheck > 300) {
                    const bufferedCount = tradeAggregationBuffer.size;
                    if (bufferedCount > 0) {
                        LoggingService.waiting(
                            USER_ADDRESSES.length,
                            `${bufferedCount} trade group(s) pending`
                        );
                    } else {
                        LoggingService.waiting(USER_ADDRESSES.length);
                    }
                    lastCheck = Date.now();
                }
            }
        } else {
            // Original non-aggregation logic
            if (trades.length > 0) {
                LoggingService.clearLine();
                LoggingService.header(
                    `⚡ ${trades.length} NEW TRADE${trades.length > 1 ? 'S' : ''} TO COPY`
                );
                await doTrading(clobClient, trades);
                lastCheck = Date.now();
            } else {
                // Update waiting message every 300ms for smooth animation
                if (Date.now() - lastCheck > 300) {
                    LoggingService.waiting(USER_ADDRESSES.length);
                    lastCheck = Date.now();
                }
            }
        }

        if (!isRunning) break;
        await new Promise((resolve) => setTimeout(resolve, 300)); // 300ms polling interval
    }

    LoggingService.info('Trade executor stopped');
};

export default tradeExecutionService;
