# Running the Python Version

## Prerequisites

1. **Python 3.9+** installed and in PATH
2. **.env file** with all required configuration
3. **MongoDB** running and accessible
4. **Dependencies** installed

## Quick Start

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
chmod +x run.sh
./run.sh
```

### Manual Run
```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Run the bot
python -m src.main
```

## Required Environment Variables

Create a `.env` file in the `PythonVersion` directory with:

```env
USER_ADDRESSES=0x...  # Comma-separated trader addresses
PROXY_WALLET=0x...    # Your wallet address
PRIVATE_KEY=0x...     # Your private key
CLOB_HTTP_URL=https://clob.polymarket.com/
CLOB_WS_URL=wss://ws-subscriptions-clob.polymarket.com/ws
MONGO_URI=mongodb://localhost:27017/polymarket_copytrading
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

## Troubleshooting

### Python Not Found
- Install Python 3.9+ from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Missing .env File
- Copy `.env` from TypeScriptVersion directory, or
- Create a new `.env` file with all required variables

### MongoDB Connection Error
- Make sure MongoDB is running
- Check your MONGO_URI in .env file
- For MongoDB Atlas, ensure your IP is whitelisted

### CLOB Client Error
⚠️ **Important**: The CLOB client needs to be implemented. See `src/utils/create_clob_client.py` for details.

## Expected Output

When running successfully, you should see:
1. Startup banner
2. Database connection status
3. Health check results
4. Trade monitor starting
5. Trade executor starting
6. Waiting for trades...

## Stopping the Bot

Press `Ctrl+C` to gracefully shutdown the bot.
