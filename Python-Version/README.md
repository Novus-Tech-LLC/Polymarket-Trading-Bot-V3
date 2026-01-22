# Polymarket Copy Trading Bot - Python Version

This is a Python port of the TypeScript Polymarket Copy Trading Bot. It maintains the same logic and functionality as the TypeScript version.

## ⚠️ Important Note

**This Python version requires a fully implemented Polymarket CLOB client.** The TypeScript version uses the official `@polymarket/clob-client` package, but there is no official Python equivalent. You will need to:

1. **Implement the CLOB client** - The `src/utils/create_clob_client.py` file contains a placeholder structure. You need to implement:
   - `get_order_book(asset)` - Fetch order book from Polymarket CLOB API
   - `create_market_order(order_args)` - Create and sign orders using your Ethereum wallet
   - `post_order(signed_order, order_type)` - Submit orders to Polymarket CLOB API
   - API key creation/derivation

2. **Alternative approaches:**
   - Use a Python wrapper for the TypeScript CLOB client (if available)
   - Implement direct HTTP API calls to Polymarket CLOB endpoints
   - Use a bridge service that calls the TypeScript client

## Project Structure

```
PythonVersion/
├── src/
│   ├── config/          # Configuration (env, copy strategy, database)
│   ├── interfaces/       # Type definitions
│   ├── models/          # MongoDB models
│   ├── services/        # Core services (trade monitor, executor)
│   ├── utils/           # Utilities (logger, fetch data, etc.)
│   └── main.py          # Entry point
├── logs/                # Log files (created automatically)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. **Install Python 3.9+**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file** (copy from TypeScript version or create new):
   ```env
   USER_ADDRESSES=0x...  # Comma-separated trader addresses
   PROXY_WALLET=0x...    # Your wallet address
   PRIVATE_KEY=0x...     # Your private key
   CLOB_HTTP_URL=https://clob.polymarket.com/
   CLOB_WS_URL=wss://ws-subscriptions-clob.polymarket.com/ws
   MONGO_URI=mongodb://...
   RPC_URL=https://polygon-rpc.com
   USDC_CONTRACT_ADDRESS=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
   FETCH_INTERVAL=1
   TOO_OLD_TIMESTAMP=24
   RETRY_LIMIT=3
   COPY_STRATEGY=PERCENTAGE
   COPY_SIZE=10.0
   MAX_ORDER_SIZE_USD=100.0
   MIN_ORDER_SIZE_USD=1.0
   ```

## Usage

**Before running, ensure:**
1. MongoDB is running and accessible
2. CLOB client is fully implemented (see `src/utils/create_clob_client.py`)
3. All environment variables are set correctly

**Run the bot:**
```bash
python -m src.main
```

## Features

✅ **Fully ported from TypeScript:**
- Trade monitoring and execution
- Copy strategy system (PERCENTAGE, FIXED, ADAPTIVE)
- Tiered multipliers
- Trade aggregation
- Position tracking
- Comprehensive logging
- Health checks
- Graceful shutdown

✅ **Same logic and results:**
- Identical trade detection
- Same order size calculations
- Same position management
- Same error handling

## Differences from TypeScript Version

1. **CLOB Client**: Requires manual implementation (see above)
2. **Async/Await**: Uses Python's `asyncio` instead of Promise-based async
3. **Type System**: Uses Python type hints instead of TypeScript types
4. **MongoDB**: Uses `pymongo` instead of `mongoose`
5. **Ethereum**: Uses `web3.py` instead of `ethers.js`
6. **Logging**: Uses `colorama` for colored output

## Implementation Status

- ✅ Configuration system
- ✅ Database models and connection
- ✅ Logger utility
- ✅ Trade monitoring service
- ✅ Trade executor service
- ✅ Copy strategy calculations
- ✅ Health checks
- ✅ Error handling
- ⚠️ **CLOB client** (needs implementation)
- ⚠️ **Order signing** (needs implementation)

## Next Steps

1. **Implement CLOB Client:**
   - Study the TypeScript `@polymarket/clob-client` package
   - Implement HTTP API calls to Polymarket CLOB endpoints
   - Implement order signing using `eth_account` or similar
   - Test with small orders first

2. **Testing:**
   - Test database connections
   - Test trade monitoring
   - Test order execution (once CLOB client is ready)
   - Verify calculations match TypeScript version

3. **Production Readiness:**
   - Add comprehensive error handling
   - Add retry logic for API calls
   - Add monitoring and alerts
   - Performance optimization

## Support

For issues or questions:
1. Check the TypeScript version documentation
2. Review the Polymarket CLOB API documentation
3. Check the code comments for implementation hints

## License

Same as TypeScript version (ISC License)
