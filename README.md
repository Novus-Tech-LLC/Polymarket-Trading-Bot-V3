<div align="center">
# Polymarket Copy Trading Bot
</div>

<div align="center">

![License](https://img.shields.io/badge/license-ISC-blue.svg)
![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Code Quality](https://img.shields.io/badge/code%20quality-enterprise-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)

**Enterprise-Grade Automated Copy Trading System for Polymarket**

*Intelligently replicate trades from top-performing Polymarket traders with advanced position sizing, real-time execution, and comprehensive risk management.*

[![Quick Start](https://img.shields.io/badge/Quick%20Start-5%20minutes-brightgreen)](./docs/QUICK_START.md)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue)](./docs)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](./docs/DOCKER.md)
[![Support](https://img.shields.io/badge/Support-Available-green)](https://t.me/novustch)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Safety & Risk Management](#-safety--risk-management)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Polymarket Copy Trading Bot** is a production-ready, enterprise-grade automation system that enables you to automatically replicate trading strategies from successful Polymarket traders. Built with modern software engineering practices, the bot provides institutional-quality features for both TypeScript and Python implementations.

### Core Capabilities

- **🔄 Real-Time Trade Monitoring** - Continuous surveillance of selected traders using Polymarket's Data API with sub-second detection
- **📊 Intelligent Position Sizing** - Advanced algorithms for automatic trade size calculation based on capital ratios and configurable strategies
- **🛡️ Enterprise Risk Management** - Multi-layered safeguards including slippage protection, position limits, balance verification, and daily volume caps
- **💾 Persistent Data Storage** - Comprehensive trade history and position tracking via MongoDB with full audit trails
- **🏗️ Professional Architecture** - Clean, maintainable codebase following SOLID principles with full type safety and comprehensive error handling

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADER SELECTION                          │
│  Identify top performers from Polymarket Leaderboard         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  TRADE MONITORING SERVICE                   │
│  • Polls trader activity at configurable intervals          │
│  • Detects new trades via Polymarket Data API                │
│  • Validates trade timestamps and filters duplicates         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  TRADE EXECUTION SERVICE                    │
│  • Calculates optimal position size based on strategy        │
│  • Applies risk management rules and limits                  │
│  • Validates balance and slippage constraints                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOB API CLIENT                          │
│  • Interfaces with Polymarket CLOB API                       │
│  • Executes market orders with FOK (Fill-or-Kill)           │
│  • Handles Gnosis Safe and EOA wallet types                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    MONGODB DATABASE                          │
│  • Stores complete trade history                            │
│  • Tracks positions and profitability                       │
│  • Maintains audit trail for compliance                      │
└─────────────────────────────────────────────────────────────┘
```

### Workflow

1. **Trader Selection** → Identify top performers from [Polymarket Leaderboard](https://polymarket.com/leaderboard) or analyze detailed statistics on [Predictfolio](https://predictfolio.com)
2. **Configuration** → Set up your trading strategy, risk limits, and trader addresses via interactive setup wizard
3. **Continuous Monitoring** → Bot polls trader positions at configurable intervals (default: 1 second) for real-time detection
4. **Position Calculation** → Automatically scales trades based on your balance vs. trader's portfolio value using selected strategy
5. **Order Execution** → Places matching orders on Polymarket using your wallet via CLOB API with built-in safety checks
6. **Performance Tracking** → Maintains comprehensive trade history and position data in MongoDB for analysis

---

## ✨ Key Features

### Trading Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Trader Support** | Simultaneously track and copy trades from multiple traders | ✅ |
| **Smart Position Sizing** | Automatic trade size calculation with three strategies (Percentage, Fixed, Adaptive) | ✅ |
| **Tiered Multipliers** | Apply different multipliers based on trade size thresholds for sophisticated scaling | ✅ |
| **Position Tracking** | Accurate tracking of purchases and sells, even after balance changes | ✅ |
| **Trade Aggregation** | Combines multiple small trades into larger executable orders (optional) | ✅ |
| **Real-Time Execution** | Sub-second trade detection and execution for optimal entry prices | ✅ |
| **Price Protection** | Built-in slippage checks to prevent unfavorable fills | ✅ |
| **Balance Verification** | Automatic balance checks before each trade execution | ✅ |

### Technical Excellence

| Feature | Description | Status |
|---------|-------------|--------|
| **Type-Safe Codebase** | Full TypeScript/Python implementation with strict type checking | ✅ |
| **Error Handling** | Comprehensive error handling with custom error classes and recovery mechanisms | ✅ |
| **Database Integration** | MongoDB for persistent storage with optimized queries and indexing | ✅ |
| **Configuration Management** | Environment-based configuration with validation and helpful error messages | ✅ |
| **Logging System** | Structured logging with file output, console display, and log rotation | ✅ |
| **Health Monitoring** | Built-in health check system for configuration validation and diagnostics | ✅ |
| **Docker Support** | Complete containerization with Docker Compose for easy deployment | ✅ |
| **CLI Tools** | Comprehensive command-line utilities for monitoring and management | ✅ |

### Risk Management

- **Position Limits** - Configurable maximum position sizes per market
- **Daily Volume Caps** - Optional daily trading volume limits
- **Slippage Protection** - Price validation to prevent unfavorable fills
- **Balance Checks** - Automatic balance verification before trades
- **Error Recovery** - Comprehensive error handling and retry logic
- **Health Checks** - Configuration validation before startup

---

## 🏗️ Architecture

### Technology Stack

#### TypeScript Version
- **Runtime**: Node.js 18.0.0+
- **Language**: TypeScript 5.7 with strict type checking
- **Package Manager**: npm
- **Build System**: TypeScript Compiler

#### Python Version
- **Runtime**: Python 3.9+
- **Package Manager**: pip
- **Dependencies**: See `requirements.txt`

#### Shared Infrastructure
- **Database**: MongoDB (Atlas supported, free tier available)
- **Blockchain**: Polygon Network (Layer 2)
- **APIs**: 
  - Polymarket CLOB Client (v4.14.0+)
  - Polymarket Data API
- **Infrastructure**: Docker & Docker Compose for containerized deployment

### Project Structure

```
polymarket-trading-bot-v3/
├── Typescript-Version/          # TypeScript implementation
│   ├── src/
│   │   ├── application/         # Application layer
│   │   │   ├── commands/        # CLI commands
│   │   │   └── services/        # Core services
│   │   ├── domain/              # Domain layer
│   │   │   ├── entities/        # Data models
│   │   │   └── types/           # Type definitions
│   │   ├── infrastructure/      # Infrastructure layer
│   │   │   ├── clients/         # External API clients
│   │   │   └── database/        # Database configuration
│   │   ├── shared/              # Shared utilities
│   │   │   ├── config/          # Configuration
│   │   │   └── utilities/      # Utility functions
│   │   └── index.ts             # Application entry point
│   ├── docs/                    # Documentation
│   ├── tests/                   # Test files
│   └── package.json
│
├── Python-Version/              # Python implementation
│   ├── src/
│   │   ├── config/              # Configuration
│   │   ├── interfaces/          # Type definitions
│   │   ├── models/              # Data models
│   │   ├── services/            # Core services
│   │   ├── utils/               # Utility functions
│   │   └── main.py              # Application entry point
│   ├── docs/                    # Documentation
│   └── requirements.txt
│
└── README.md                    # This file
```

### Design Principles

- **Separation of Concerns** - Clear separation between application, domain, and infrastructure layers
- **Type Safety** - Full type coverage with strict TypeScript/Python typing
- **Error Handling** - Comprehensive error handling with custom error classes
- **Configuration Management** - Environment-based configuration with validation
- **Logging** - Structured logging with file and console output
- **Testing** - Unit tests and integration tests for critical components
- **Documentation** - Comprehensive inline documentation and guides

---

## 🚀 Quick Start

### Prerequisites

Before installation, ensure you have the following:

| Requirement | Minimum Version | Where to Get |
|------------|----------------|--------------|
| **Node.js** | v18.0.0+ | [Download](https://nodejs.org/) |
| **Python** | 3.9+ | [Download](https://www.python.org/downloads/) |
| **MongoDB** | Any version | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) (free tier) |
| **Polygon Wallet** | N/A | MetaMask or any Web3 wallet |
| **RPC Endpoint** | N/A | [Infura](https://infura.io) / [Alchemy](https://www.alchemy.com) / [Ankr](https://www.ankr.com) |

### Installation

#### TypeScript Version

```bash
# Clone the repository
git clone https://github.com/Novus-Tech-LLC/polymarket-trading-bot-v3.git
cd polymarket-trading-bot-v3/Typescript-Version

# Install dependencies
npm install

# Run interactive setup wizard
npm run setup

# Build the project
npm run build

# Verify configuration
npm run health-check

# Start the bot
npm start
```

#### Python Version

```bash
# Clone the repository
git clone https://github.com/Novus-Tech-LLC/polymarket-trading-bot-v3.git
cd polymarket-trading-bot-v3/Python-Version

# Install dependencies
pip install -r requirements.txt

# Run interactive setup (if available)
python setup.py

# Start the bot
python -m src.main
```

### First-Time Setup Checklist

- [ ] **Install Dependencies** - Run `npm install` or `pip install -r requirements.txt`
- [ ] **Run Setup Wizard** - Execute `npm run setup` to interactively configure your `.env` file
- [ ] **Verify Configuration** - Run `npm run health-check` to validate all settings
- [ ] **Fund Your Wallet** - Ensure your Polygon wallet has sufficient USDC and POL/MATIC for gas
- [ ] **Select Traders** - Add trader addresses to `USER_ADDRESSES` in your `.env` file
- [ ] **Test Run** - Start with minimal funds to verify everything works correctly
- [ ] **Monitor Performance** - Check bot logs and positions regularly

📖 **For detailed setup instructions, see [Getting Started Guide](./docs/GETTING_STARTED.md)**

---

## ⚙️ Configuration

### Environment Variables

The bot is configured via environment variables stored in a `.env` file. Copy `env.example` to `.env` and update with your values.

#### Required Configuration

| Variable | Description | Example | Validation |
|----------|-------------|---------|------------|
| `USER_ADDRESSES` | Comma-separated trader addresses to copy | `"0xABC...,0xDEF..."` | Ethereum address format |
| `PROXY_WALLET` | Your Polygon wallet address | `"0x123..."` | Ethereum address format |
| `PRIVATE_KEY` | Wallet private key (no 0x prefix) | `"abc123..."` | 64 hex characters |
| `MONGO_URI` | MongoDB connection string | `"mongodb+srv://..."` | MongoDB URI format |
| `RPC_URL` | Polygon RPC endpoint | `"https://polygon..."` | HTTP/HTTPS URL |
| `USDC_CONTRACT_ADDRESS` | USDC token contract | `"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"` | Ethereum address |
| `CLOB_HTTP_URL` | CLOB HTTP endpoint | `"https://clob.polymarket.com/"` | HTTP/HTTPS URL |
| `CLOB_WS_URL` | CLOB WebSocket endpoint | `"wss://ws-subscriptions-clob.polymarket.com/ws"` | WebSocket URL |

#### Optional Configuration

| Variable | Description | Default | Range |
|----------|-------------|---------|-------|
| `COPY_STRATEGY` | Copy strategy (PERCENTAGE, FIXED, ADAPTIVE) | `"PERCENTAGE"` | See strategies below |
| `COPY_SIZE` | Copy size parameter | `10.0` | Strategy-dependent |
| `TRADE_MULTIPLIER` | Position size multiplier | `1.0` | 0.1 - 10.0 |
| `MAX_ORDER_SIZE_USD` | Maximum order size in USD | `100.0` | > 0 |
| `MIN_ORDER_SIZE_USD` | Minimum order size in USD | `1.0` | > 0 |
| `FETCH_INTERVAL` | Polling interval in seconds | `1` | 1 - 60 |
| `TRADE_AGGREGATION_ENABLED` | Enable trade aggregation | `false` | true/false |
| `TRADE_AGGREGATION_WINDOW_SECONDS` | Aggregation time window | `300` | 60 - 3600 |

### Copy Strategy Configuration

The bot supports three sophisticated copy strategies:

#### 1. PERCENTAGE Strategy
Copy a fixed percentage of the trader's order size.

```bash
COPY_STRATEGY="PERCENTAGE"
COPY_SIZE="10.0"  # Copy 10% of trader's order
```

**Use Case**: Proportional scaling based on trader's position size.

#### 2. FIXED Strategy
Copy a fixed dollar amount per trade regardless of trader's order size.

```bash
COPY_STRATEGY="FIXED"
COPY_SIZE="50.0"  # Always copy $50 per trade
```

**Use Case**: Consistent position sizing regardless of trader's capital.

#### 3. ADAPTIVE Strategy
Dynamically adjust percentage based on trader's order size.

```bash
COPY_STRATEGY="ADAPTIVE"
COPY_SIZE="10.0"
ADAPTIVE_MIN_PERCENT="5.0"   # Minimum for large orders
ADAPTIVE_MAX_PERCENT="15.0"  # Maximum for small orders
ADAPTIVE_THRESHOLD_USD="500.0"  # Threshold for adaptation
```

**Use Case**: Optimize position sizing based on trade size.

📖 **For advanced configuration options, see [Tiered Multipliers Guide](./docs/TIERED_MULTIPLIERS.md)**

### Finding Quality Traders

To identify traders worth copying, follow these criteria:

1. **Visit [Polymarket Leaderboard](https://polymarket.com/leaderboard)**
2. **Look for traders with:**
   - ✅ Positive P&L over extended periods (30+ days)
   - ✅ Win rate above 55%
   - ✅ Active trading history (trades in last 7 days)
   - ✅ Consistent performance (not just one lucky bet)
   - ✅ Reasonable position sizes (within your budget)
3. **Verify detailed statistics on [Predictfolio](https://predictfolio.com)**
4. **Add wallet addresses to `USER_ADDRESSES` in your `.env` file**

📖 **For complete configuration guide, see [Quick Start Guide](./docs/QUICK_START.md)**

---

## 🐳 Deployment

### Docker Deployment (Recommended)

Deploy with Docker Compose for a production-ready, containerized setup:

```bash
# Navigate to TypeScript version
cd Typescript-Version

# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f polymarket

# Stop the container
docker-compose down
```

**Benefits:**
- ✅ Isolated environment
- ✅ Easy dependency management
- ✅ Consistent deployment across systems
- ✅ Built-in MongoDB container option
- ✅ Automatic restarts on failure

📖 **[Complete Docker Deployment Guide →](./docs/DOCKER.md)**

### Manual Deployment

For manual deployment on a server or VPS:

#### Using PM2 (Recommended)

```bash
# Install PM2 globally
npm install -g pm2

# Build the project
npm run build

# Start with PM2
pm2 start dist/index.js --name polymarket-bot

# Enable PM2 startup script
pm2 startup
pm2 save

# Monitor logs
pm2 logs polymarket-bot

# View status
pm2 status

# Restart bot
pm2 restart polymarket-bot
```

#### Using systemd (Linux)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/polymarket-bot.service
```

```ini
[Unit]
Description=Polymarket Copy Trading Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/polymarket-trading-bot-v3/Typescript-Version
ExecStart=/usr/bin/node dist/index.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable polymarket-bot
sudo systemctl start polymarket-bot
sudo systemctl status polymarket-bot
```

### Production Best Practices

- ✅ **Use Process Manager** - PM2, systemd, or similar for automatic restarts
- ✅ **Set Up Log Rotation** - Configure log rotation for log files
- ✅ **Monitor Resources** - Monitor CPU, memory, and API rate limits
- ✅ **Configure Alerts** - Set up alerts for critical errors
- ✅ **Regular Backups** - Schedule regular MongoDB backups
- ✅ **Keep Updated** - Regularly update dependencies and bot version
- ✅ **Security** - Use environment variables, restrict file permissions
- ✅ **Monitoring** - Set up monitoring and alerting systems

---

## 📚 Documentation

### Getting Started Guides

- **[🚀 Getting Started Guide](./docs/GETTING_STARTED.md)** - Complete beginner's guide with step-by-step instructions
- **[⚡ Quick Start](./docs/QUICK_START.md)** - Fast setup guide for experienced users
- **[🐳 Docker Deployment](./docs/DOCKER.md)** - Complete container deployment guide

### Advanced Configuration

- **[👥 Multi-Trader Guide](./docs/MULTI_TRADER_GUIDE.md)** - Configuring and managing multiple traders
- **[📍 Position Tracking](./docs/POSITION_TRACKING.md)** - Understanding position tracking mechanics
- **[💰 Funding Guide](./docs/FUNDING_GUIDE.md)** - Wallet funding and token management
- **[📊 Tiered Multipliers](./docs/TIERED_MULTIPLIERS.md)** - Advanced position sizing strategies

### Testing & Analysis

- **[🧪 Simulation Guide](./docs/SIMULATION_GUIDE.md)** - Backtesting trading strategies
- **[🔬 Simulation Runner](./docs/SIMULATION_RUNNER_GUIDE.md)** - Advanced backtesting tools

### Reference

- **[📖 Code Quality Improvements](./docs/CODE_QUALITY_IMPROVEMENTS.md)** - Code quality standards and practices
- **[🔍 Trader Selection Guide](./docs/TRADER_SELECTION_GUIDE.md)** - How to identify quality traders

---

## ⚠️ Safety & Risk Management

### Important Disclaimers

> **⚠️ WARNING: This software executes real trades with real money. Use at your own risk.**

- **No Guarantees** - Past performance does not guarantee future results
- **Financial Risk** - Trading involves substantial risk of financial loss
- **No Liability** - Developers are not responsible for financial losses
- **Educational Purpose** - This software is provided for educational and research purposes
- **Not Financial Advice** - This is not financial, investment, or trading advice

### Risk Management Best Practices

1. **Start Small** - Test with minimal funds before scaling up
2. **Diversify** - Copy multiple traders with different strategies
3. **Monitor Regularly** - Check bot logs and positions daily
4. **Set Limits** - Use position size limits and daily volume caps
5. **Dedicated Wallet** - Use a separate wallet from your main funds
6. **Emergency Stop** - Know how to stop the bot quickly (Ctrl+C or process manager)
7. **Research Traders** - Thoroughly research traders before copying
8. **Stay Informed** - Monitor market conditions and bot performance
9. **Regular Reviews** - Review and adjust your strategy regularly
10. **Backup Plans** - Have a plan for handling unexpected situations

### Built-in Safety Features

- **Balance Checks** - Automatic balance verification before each trade
- **Slippage Protection** - Price validation to prevent unfavorable fills
- **Position Limits** - Configurable maximum position sizes per market
- **Daily Volume Caps** - Optional daily trading volume limits
- **Error Handling** - Comprehensive error handling and recovery mechanisms
- **Health Checks** - Configuration validation before startup
- **Retry Logic** - Automatic retry with exponential backoff for transient errors

---

## 🔧 Troubleshooting

### Common Issues

#### Configuration Issues

**Problem**: Missing or invalid environment variables

```bash
# Solution: Run setup wizard
npm run setup

# Or manually create .env file
cp env.example .env
# Edit .env with your values
```

**Problem**: Configuration validation errors

```bash
# Solution: Run health check
npm run health-check
```

#### Database Issues

**Problem**: MongoDB connection failed

**Solutions:**
- Verify `MONGO_URI` is correct and properly formatted
- Whitelist your IP address in MongoDB Atlas
- Check network connectivity and firewall settings
- Verify database credentials are correct
- Ensure MongoDB service is running

#### Trading Issues

**Problem**: Bot not detecting trades

**Solutions:**
- Verify trader addresses in `USER_ADDRESSES` are correct
- Check trader has recent activity on Polymarket
- Verify `FETCH_INTERVAL` is appropriate (try 1-5 seconds)
- Check MongoDB connection and data storage
- Review bot logs for error messages

**Problem**: Insufficient balance errors

**Solutions:**
- Add USDC to your wallet (minimum recommended: $50+)
- Ensure POL/MATIC for gas fees (minimum: 0.1 POL)
- Check token allowances: `npm run check-allowance`
- Verify wallet address matches `PROXY_WALLET`
- Review balance: `npm run check-both`

**Problem**: Orders failing

**Solutions:**
- Verify wallet has sufficient balance
- Check and set token allowances
- Review slippage settings (may be too strict)
- Check network connectivity
- Verify RPC endpoint is working
- Review order book liquidity

### Diagnostic Commands

```bash
# Health check - Validate all configuration
npm run health-check

# Check token allowance
npm run check-allowance

# Verify wallet balance
npm run check-both

# View recent activity
npm run check-activity

# Check positions and statistics
npm run check-stats

# View detailed positions
npm run check-positions-detailed
```

📖 **For detailed troubleshooting, see [Quick Start Guide](./docs/QUICK_START.md)**

---

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### Contribution Process

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow code quality standards** - See [Code Quality Improvements](./docs/CODE_QUALITY_IMPROVEMENTS.md)
4. **Write tests** for new features
5. **Update documentation** as needed
6. **Commit your changes** with meaningful commit messages
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request** with detailed description

### Development Guidelines

- ✅ Follow TypeScript/Python best practices
- ✅ Maintain type safety (avoid `any` types)
- ✅ Add JSDoc/docstring comments for public APIs
- ✅ Write meaningful commit messages
- ✅ Update relevant documentation
- ✅ Test thoroughly before submitting
- ✅ Follow existing code style and patterns

### Code Standards

- **Type Safety** - Full type coverage with strict checking
- **Error Handling** - Comprehensive error handling
- **Documentation** - Inline documentation for all public APIs
- **Testing** - Unit tests for critical components
- **Code Style** - Follow project linting rules

---

## 📄 License

This project is licensed under the **ISC License** - see the [LICENSE](LICENSE) file for details.

---

## 🚀 Advanced Version

**Version 2 Available:** An advanced version with **RTDS (Real-Time Data Stream)** monitoring is now available as a private repository.

### Key Advantages of Version 2

- **⚡ Real-Time Data Stream (RTDS)** - Instant trade detection without polling delays
- **⚡ Lower Latency** - Near-instantaneous trade replication for optimal entry prices
- **⚡ Reduced API Load** - More efficient API usage compared to polling methods
- **⚡ Enhanced Performance** - Superior copy trading execution with minimal delay
- **⚡ Scalability** - Better handling of multiple traders and high-frequency trading

For access to the advanced version, please contact us through the [Support](#-support) channels.

---

## 🙏 Acknowledgments

- **[Polymarket CLOB Client](https://github.com/Polymarket/clob-client)** - Official Polymarket CLOB API client
- **[Predictfolio](https://predictfolio.com)** - Trader analytics and performance metrics
- **Polygon Network** - Layer 2 blockchain infrastructure
- **MongoDB** - Database infrastructure

---

## 💬 Support

For questions, issues, or support:

- **📱 Telegram**: [@novustch](https://t.me/novustch)
- **🐦 Twitter/X**: [@novustch](https://x.com/novustch)
- **🐛 Issues**: [GitHub Issues](https://github.com/Novus-Tech-LLC/polymarket-trading-bot-v3/issues)
- **📚 Documentation**: See [Documentation](#-documentation) section above

---

<div align="center">

Made with ❤️ by [Novus Tech LLC](https://github.com/Novus-Tech-LLC)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/Novus-Tech-LLC/polymarket-trading-bot-v3)
[![Telegram](https://img.shields.io/badge/Telegram-Support-blue?logo=telegram)](https://t.me/novustch)
[![Twitter](https://img.shields.io/badge/Twitter-Follow-blue?logo=twitter)](https://x.com/novustch)

</div>
