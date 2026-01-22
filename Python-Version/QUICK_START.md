# Quick Start Guide

## Step 1: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

## Step 2: Create .env File

Create a `.env` file in the `PythonVersion` directory with the following variables:

```env
# Trader addresses to copy (comma-separated or JSON array)
USER_ADDRESSES=0x...  # Replace with trader addresses

# Your wallet address
PROXY_WALLET=0x...    # Your wallet address

# Your private key (keep this secret!)
PRIVATE_KEY=0x...     # Your private key

# Polymarket CLOB URLs
CLOB_HTTP_URL=https://clob.polymarket.com/
CLOB_WS_URL=wss://ws-subscriptions-clob.polymarket.com/ws

# MongoDB connection string
MONGO_URI=mongodb://localhost:27017/polymarket_copytrading
# Or for MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# Polygon RPC endpoint
RPC_URL=https://polygon-rpc.com
# Or use your own RPC provider:
# RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID

# USDC contract address on Polygon
USDC_CONTRACT_ADDRESS=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174

# Monitoring settings
FETCH_INTERVAL=1
TOO_OLD_TIMESTAMP=24

# Retry settings
RETRY_LIMIT=3
NETWORK_RETRY_LIMIT=3
REQUEST_TIMEOUT_MS=10000

# Copy strategy (PERCENTAGE, FIXED, or ADAPTIVE)
COPY_STRATEGY=PERCENTAGE
COPY_SIZE=10.0

# Order size limits
MAX_ORDER_SIZE_USD=100.0
MIN_ORDER_SIZE_USD=1.0
```

## Step 3: Run the Bot

```bash
python -m src.main
```

## Getting Configuration Values

### USER_ADDRESSES
- Find trader addresses from:
  - Polymarket Leaderboard: https://polymarket.com/leaderboard
  - Predictfolio: https://predictfolio.com
- Format: Comma-separated or JSON array
  - Example: `USER_ADDRESSES=0x123...,0x456...`
  - Or: `USER_ADDRESSES=["0x123...","0x456..."]`

### PROXY_WALLET
- Your Ethereum wallet address (the one you'll use for trading)
- Format: `0x` followed by 40 hexadecimal characters

### PRIVATE_KEY
- Your wallet's private key (keep this secret!)
- Format: `0x` followed by 64 hexadecimal characters
- ⚠️ **Never share this or commit it to version control!**

### MONGO_URI
- **Local MongoDB:**
  - `mongodb://localhost:27017/polymarket_copytrading`
- **MongoDB Atlas (Free):**
  1. Visit https://www.mongodb.com/cloud/atlas/register
  2. Create a free cluster
  3. Create database user
  4. Whitelist IP: `0.0.0.0/0` (or your IP)
  5. Get connection string from "Connect" button
  6. Format: `mongodb+srv://username:password@cluster.mongodb.net/database`

### RPC_URL
- **Free options:**
  - `https://polygon-rpc.com`
  - `https://rpc.ankr.com/polygon`
- **Or use your own:**
  - Infura: https://infura.io
  - Alchemy: https://www.alchemy.com
  - Format: `https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID`

## Next Steps

1. ✅ Install dependencies
2. ✅ Create `.env` file
3. ✅ Run the bot: `python -m src.main`

## Troubleshooting

### Missing .env file
- Create `.env` file in `PythonVersion` directory
- Copy template above and fill in your values

### MongoDB connection error
- Make sure MongoDB is running (if using local)
- Check MONGO_URI format
- For Atlas, verify IP whitelist

### CLOB Client Error
⚠️ **Note:** The CLOB client needs to be implemented. See `src/utils/create_clob_client.py`

## Need Help?

See:
- `README.md` - Full documentation
- `RUN_INSTRUCTIONS.md` - Running instructions
- `FIX_PYTHON.md` - Python installation help
