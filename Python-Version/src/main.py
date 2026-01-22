"""
Main entry point for Polymarket Copy Trading Bot
"""
import asyncio
import signal
import sys
from .config.db import connect_db, close_db
from .config.env import ENV
from .utils.create_clob_client import create_clob_client
from .services.trade_monitor import trade_monitor, stop_trade_monitor
from .services.trade_executor import trade_executor, stop_trade_executor
from .utils.logger import Logger
from .utils.health_check import perform_health_check, log_health_check
from .utils.errors import normalize_error, is_operational_error

USER_ADDRESSES = ENV["USER_ADDRESSES"]
PROXY_WALLET = ENV["PROXY_WALLET"]

_is_shutting_down = False


async def graceful_shutdown(signal_name: str) -> None:
    """Gracefully shutdown the application"""
    global _is_shutting_down

    if _is_shutting_down:
        Logger.warning("Shutdown already in progress, forcing exit...")
        sys.exit(1)

    _is_shutting_down = True
    Logger.separator()
    Logger.info(f"Received {signal_name}, initiating graceful shutdown...")

    try:
        # Stop services
        stop_trade_monitor()
        stop_trade_executor()

        # Give services time to finish current operations
        Logger.info("Waiting for services to finish current operations...")
        await asyncio.sleep(2)

        # Close database connection
        close_db()

        Logger.success("Graceful shutdown completed")
        sys.exit(0)
    except Exception as error:
        Logger.error(f"Error during shutdown: {error}")
        sys.exit(1)


_shutdown_event = None

def setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown"""
    global _shutdown_event
    
    def signal_handler(signum, frame):
        signal_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
        if _shutdown_event:
            _shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


async def main() -> None:
    """Main application entry point"""
    global _shutdown_event
    
    try:
        # Welcome message for first-time users
        print("\n💡 First time running the bot?")
        print("   Read the guide: GETTING_STARTED.md")
        print("   Run health check: python -m src.utils.health_check\n")

        connect_db()
        Logger.startup(USER_ADDRESSES, PROXY_WALLET)

        # Perform initial health check
        Logger.info("Performing initial health check...")
        health_result = await perform_health_check()
        log_health_check(health_result)

        if not health_result["healthy"]:
            Logger.warning("Health check failed, but continuing startup...")

        Logger.info("Initializing CLOB client...")
        clob_client = await create_clob_client()
        Logger.success("CLOB client ready")

        Logger.separator()
        Logger.info("Starting trade monitor...")
        monitor_task = asyncio.create_task(trade_monitor())

        Logger.info("Starting trade executor...")
        executor_task = asyncio.create_task(trade_executor(clob_client))

        # Wait for both tasks or shutdown signal
        try:
            await asyncio.gather(monitor_task, executor_task, return_exceptions=True)
        except asyncio.CancelledError:
            Logger.info("Tasks cancelled, shutting down...")

    except KeyboardInterrupt:
        await graceful_shutdown("SIGINT")
    except Exception as error:
        normalized_error = normalize_error(error)
        Logger.error(
            f"Fatal error during startup: {normalized_error.message}{f'\n{normalized_error.__traceback__}' if hasattr(normalized_error, '__traceback__') else ''}"
        )
        await graceful_shutdown("startup-error")


if __name__ == "__main__":
    setup_signal_handlers()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
