"""
Logging Service for structured logging with file output and console display
Matches the TypeScript LoggingService implementation
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # Fallback if colorama is not available
    class Fore:
        RESET = ""
        BLUE = ""
        GREEN = ""
        YELLOW = ""
        RED = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
    
    class Style:
        RESET_ALL = ""
        BRIGHT = ""
        DIM = ""

# Logging constants (matching TypeScript LOG_CONSTANTS)
LOG_CONSTANTS = {
    "LOGS_DIR": "logs",
    "LOG_FILE_PREFIX": "bot-",
    "MAX_LINE_LENGTH": 70,
}


class LoggingService:
    """Logging Service class matching TypeScript LoggingService structure"""

    _logs_dir = Path(LOG_CONSTANTS["LOGS_DIR"])
    _spinner_frames = ["⏳", "⌛", "⏳"]
    _spinner_index = 0

    @staticmethod
    def _get_log_file_name() -> Path:
        """Get log file name based on current date"""
        date = datetime.now().strftime("%Y-%m-%d")  # YYYY-MM-DD
        return LoggingService._logs_dir / f"{LOG_CONSTANTS['LOG_FILE_PREFIX']}{date}.log"

    @staticmethod
    def _ensure_logs_dir() -> None:
        """Ensure logs directory exists"""
        LoggingService._logs_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _write_to_file(message: str) -> None:
        """Write message to log file"""
        try:
            LoggingService._ensure_logs_dir()
            log_file = LoggingService._get_log_file_name()
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {message}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            # Silently fail to avoid infinite loops
            pass

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI color codes for file logging"""
        return re.sub(r"\x1b\[\d+m", "", text)

    @staticmethod
    def _format_address(address: str) -> str:
        """Format Ethereum address for display"""
        return f"{address[:6]}...{address[-4:]}"

    @staticmethod
    def _mask_address(address: str) -> str:
        """Mask Ethereum address for privacy"""
        # Show 0x and first 4 chars, mask middle, show last 4 chars
        return f"{address[:6]}{'*' * 34}{address[-4:]}"

    @staticmethod
    def header(title: str) -> None:
        """Print header with title"""
        max_length = LOG_CONSTANTS["MAX_LINE_LENGTH"]
        line = "━" * max_length
        print(f"\n{Fore.CYAN}{line}")
        print(f"{Fore.CYAN}{Style.BRIGHT}  {title}")
        print(f"{Fore.CYAN}{line}\n")
        LoggingService._write_to_file(f"HEADER: {title}")

    @staticmethod
    def info(message: str) -> None:
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {message}")
        LoggingService._write_to_file(f"INFO: {message}")

    @staticmethod
    def success(message: str) -> None:
        """Print success message"""
        print(f"{Fore.GREEN}✓ {message}")
        LoggingService._write_to_file(f"SUCCESS: {message}")

    @staticmethod
    def warning(message: str) -> None:
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {message}")
        LoggingService._write_to_file(f"WARNING: {message}")

    @staticmethod
    def error(message: str) -> None:
        """Print error message"""
        print(f"{Fore.RED}✗ {message}")
        LoggingService._write_to_file(f"ERROR: {message}")

    @staticmethod
    def trade(trader_address: str, action: str, details: dict[str, Any]) -> None:
        """Print trade information"""
        max_length = LOG_CONSTANTS["MAX_LINE_LENGTH"]
        line = "─" * max_length
        print(f"\n{Fore.MAGENTA}{line}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}📊 NEW TRADE DETECTED")
        print(f"{Fore.WHITE}Trader: {LoggingService._format_address(trader_address)}")
        print(f"{Fore.WHITE}Action: {Style.BRIGHT}{action}")

        if details.get("asset"):
            print(f"{Fore.WHITE}Asset:  {LoggingService._format_address(details['asset'])}")

        if details.get("side"):
            side_color = Fore.GREEN if details["side"] == "BUY" else Fore.RED
            print(f"{Fore.WHITE}Side:   {side_color}{Style.BRIGHT}{details['side']}")

        if details.get("amount"):
            print(f"{Fore.WHITE}Amount: {Fore.YELLOW}${details['amount']}")

        if details.get("price"):
            print(f"{Fore.WHITE}Price:  {Fore.CYAN}{details['price']}")

        if details.get("eventSlug") or details.get("slug"):
            # Use eventSlug for the correct market URL format
            slug = details.get("eventSlug") or details.get("slug")
            market_url = f"https://polymarket.com/event/{slug}"
            print(f"{Fore.WHITE}Market: {Fore.BLUE}{market_url}")

        if details.get("transactionHash"):
            tx_url = f"https://polygonscan.com/tx/{details['transactionHash']}"
            print(f"{Fore.WHITE}TX:     {Fore.BLUE}{tx_url}")

        print(f"{Fore.MAGENTA}{line}\n")

        # Log to file
        trade_log = f"TRADE: {LoggingService._format_address(trader_address)} - {action}"
        if details.get("side"):
            trade_log += f" | Side: {details['side']}"
        if details.get("amount"):
            trade_log += f" | Amount: ${details['amount']}"
        if details.get("price"):
            trade_log += f" | Price: {details['price']}"
        if details.get("title"):
            trade_log += f" | Market: {details['title']}"
        if details.get("transactionHash"):
            trade_log += f" | TX: {details['transactionHash']}"
        LoggingService._write_to_file(trade_log)

    @staticmethod
    def balance(my_balance: float, trader_balance: float, trader_address: str) -> None:
        """Print balance information"""
        print(f"{Fore.WHITE}Capital (USDC + Positions):")
        print(f"{Fore.WHITE}  Your total capital:   {Fore.GREEN}{Style.BRIGHT}${my_balance:.2f}")
        print(
            f"{Fore.WHITE}  Trader total capital: {Fore.BLUE}{Style.BRIGHT}${trader_balance:.2f} ({LoggingService._format_address(trader_address)})"
        )

    @staticmethod
    def order_result(success: bool, message: str) -> None:
        """Print order execution result"""
        if success:
            print(f"{Fore.GREEN}✓ {Fore.GREEN}{Style.BRIGHT}Order executed: {message}")
            LoggingService._write_to_file(f"ORDER SUCCESS: {message}")
        else:
            print(f"{Fore.RED}✗ {Fore.RED}{Style.BRIGHT}Order failed: {message}")
            LoggingService._write_to_file(f"ORDER FAILED: {message}")

    @staticmethod
    def monitoring(trader_count: int) -> None:
        """Print monitoring message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(
            f"{Fore.WHITE}{Style.DIM}[{timestamp}] {Fore.CYAN}👁️  Monitoring {Fore.YELLOW}{trader_count} trader(s)"
        )

    @staticmethod
    def startup(traders: list[str], my_wallet: str) -> None:
        """Print startup banner"""
        print("\n")
        # ASCII Art Logo with gradient colors (matching TypeScript)
        print(f"{Fore.CYAN}  ____       _        ____                 ")
        print(f"{Fore.CYAN} |  _ \\ ___ | |_   _ / ___|___  _ __  _   _ ")
        print(f"{Fore.CYAN}{Style.BRIGHT} | |_) / _ \\| | | | | |   / _ \\| '_ \\| | | |")
        print(f"{Fore.MAGENTA}{Style.BRIGHT} |  __/ (_) | | |_| | |__| (_) | |_) | |_| |")
        print(f"{Fore.MAGENTA} |_|   \\___/|_|\\__, |\\____\\___/| .__/ \\__, |")
        print(f"{Fore.MAGENTA}               |___/            |_|    |___/ ")
        print(f"{Fore.WHITE}               Copy the best, automate success\n")

        max_length = LOG_CONSTANTS["MAX_LINE_LENGTH"]
        print(f"{Fore.CYAN}{'━' * max_length}")
        print(f"{Fore.CYAN}📊 Tracking Traders:")
        for index, address in enumerate(traders, 1):
            print(f"{Fore.WHITE}   {index}. {address}")
        print(f"{Fore.CYAN}\n💼 Your Wallet:")
        print(f"{Fore.WHITE}   {LoggingService._mask_address(my_wallet)}\n")

    @staticmethod
    def db_connection(traders: list[str], counts: list[int]) -> None:
        """Print database connection status"""
        print(f"\n{Fore.CYAN}📦 Database Status:")
        for index, address in enumerate(traders):
            count_str = f"{Fore.YELLOW}{counts[index]} trades"
            print(f"{Fore.WHITE}   {LoggingService._format_address(address)}: {count_str}")
        print("")

    @staticmethod
    def separator() -> None:
        """Print separator line"""
        max_length = LOG_CONSTANTS["MAX_LINE_LENGTH"]
        print(f"{Fore.WHITE}{Style.DIM}{'─' * max_length}")

    @staticmethod
    def waiting(trader_count: int, extra_info: Optional[str] = None) -> None:
        """Print waiting message with spinner"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        spinner = LoggingService._spinner_frames[LoggingService._spinner_index % len(LoggingService._spinner_frames)]
        LoggingService._spinner_index += 1

        message = (
            f"{spinner} Waiting for trades from {trader_count} trader(s)... ({extra_info})"
            if extra_info
            else f"{spinner} Waiting for trades from {trader_count} trader(s)..."
        )

        print(f"{Fore.WHITE}{Style.DIM}[{timestamp}] {Fore.CYAN}{message}  ", end="", flush=True)

    @staticmethod
    def clear_line() -> None:
        """Clear current line"""
        print("\r" + " " * 100 + "\r", end="", flush=True)

    @staticmethod
    def my_positions(
        wallet: str,
        count: int,
        top_positions: list[dict[str, Any]],
        overall_pnl: float,
        total_value: float,
        initial_value: float,
        current_balance: float,
    ) -> None:
        """Print my positions information"""
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}💼 YOUR POSITIONS")
        print(f"{Fore.WHITE}   Wallet: {LoggingService._format_address(wallet)}")
        print("")

        # Show balance and portfolio overview
        balance_str = f"{Fore.YELLOW}{Style.BRIGHT}${current_balance:.2f}"
        total_portfolio = current_balance + total_value
        portfolio_str = f"{Fore.CYAN}{Style.BRIGHT}${total_portfolio:.2f}"

        print(f"{Fore.WHITE}   💰 Available Cash:    {balance_str}")
        print(f"{Fore.WHITE}   📊 Total Portfolio:   {portfolio_str}")

        if count == 0:
            print(f"{Fore.WHITE}\n   No open positions")
        else:
            count_str = f"{Fore.GREEN}{count} position{'s' if count > 1 else ''}"
            pnl_color = Fore.GREEN if overall_pnl >= 0 else Fore.RED
            pnl_sign = "+" if overall_pnl >= 0 else ""
            profit_str = f"{pnl_color}{Style.BRIGHT}{pnl_sign}{overall_pnl:.1f}%"
            value_str = f"{Fore.CYAN}${total_value:.2f}"
            initial_str = f"{Fore.WHITE}${initial_value:.2f}"

            print("")
            print(f"{Fore.WHITE}   📈 Open Positions:    {count_str}")
            print(f"{Fore.WHITE}      Invested:          {initial_str}")
            print(f"{Fore.WHITE}      Current Value:     {value_str}")
            print(f"{Fore.WHITE}      Profit/Loss:       {profit_str}")

            # Show top positions
            if top_positions:
                print(f"{Fore.WHITE}\n   🔝 Top Positions:")
                for pos in top_positions:
                    pnl_color = Fore.GREEN if pos.get("percentPnl", 0) >= 0 else Fore.RED
                    pnl_sign = "+" if pos.get("percentPnl", 0) >= 0 else ""
                    avg_price = pos.get("avgPrice", 0) or 0
                    cur_price = pos.get("curPrice", 0) or 0
                    title = pos.get("title", "")
                    title_display = title[:45] + "..." if len(title) > 45 else title
                    print(f"{Fore.WHITE}      • {pos.get('outcome', '')} - {title_display}")
                    print(
                        f"{Fore.WHITE}        Value: {Fore.CYAN}${pos.get('currentValue', 0):.2f} | PnL: {pnl_color}{pnl_sign}{pos.get('percentPnl', 0):.1f}%"
                    )
                    print(
                        f"{Fore.WHITE}        Bought @ {Fore.YELLOW}{(avg_price * 100):.1f}¢ | Current @ {Fore.YELLOW}{(cur_price * 100):.1f}¢"
                    )
        print("")

    @staticmethod
    def traders_positions(
        traders: list[str],
        position_counts: list[int],
        position_details: Optional[list[list[dict[str, Any]]]] = None,
        profitabilities: Optional[list[float]] = None,
    ) -> None:
        """Print traders positions information"""
        print(f"\n{Fore.CYAN}📈 TRADERS YOU'RE COPYING")
        for index, address in enumerate(traders):
            count = position_counts[index]
            count_str = (
                f"{Fore.GREEN}{count} position{'s' if count > 1 else ''}"
                if count > 0
                else f"{Fore.WHITE}0 positions"
            )

            # Add profitability if available
            profit_str = ""
            if profitabilities and index < len(profitabilities) and count > 0:
                pnl = profitabilities[index]
                pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
                pnl_sign = "+" if pnl >= 0 else ""
                profit_str = f" | {pnl_color}{Style.BRIGHT}{pnl_sign}{pnl:.1f}%"

            print(f"{Fore.WHITE}   {LoggingService._format_address(address)}: {count_str}{profit_str}")

            # Show position details if available
            if position_details and index < len(position_details) and position_details[index]:
                for pos in position_details[index]:
                    pnl_color = Fore.GREEN if pos.get("percentPnl", 0) >= 0 else Fore.RED
                    pnl_sign = "+" if pos.get("percentPnl", 0) >= 0 else ""
                    avg_price = pos.get("avgPrice", 0) or 0
                    cur_price = pos.get("curPrice", 0) or 0
                    title = pos.get("title", "")
                    title_display = title[:40] + "..." if len(title) > 40 else title
                    print(f"{Fore.WHITE}      • {pos.get('outcome', '')} - {title_display}")
                    print(
                        f"{Fore.WHITE}        Value: {Fore.CYAN}${pos.get('currentValue', 0):.2f} | PnL: {pnl_color}{pnl_sign}{pos.get('percentPnl', 0):.1f}%"
                    )
                    print(
                        f"{Fore.WHITE}        Bought @ {Fore.YELLOW}{(avg_price * 100):.1f}¢ | Current @ {Fore.YELLOW}{(cur_price * 100):.1f}¢"
                    )
        print("")


# For backward compatibility, export as default
Logger = LoggingService
