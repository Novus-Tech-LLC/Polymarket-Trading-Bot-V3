"""
Health check utility for validating system components
"""
import json
from typing import TypedDict
from pymongo.errors import ConnectionFailure
from ..config.env import ENV
from ..config.db import get_connection
from .get_my_balance import get_my_balance
from .fetch_data import fetch_data
from .logger import Logger


class HealthCheckResult(TypedDict):
    """Health check result structure"""

    healthy: bool
    checks: dict[str, dict[str, str | float]]
    timestamp: int


async def perform_health_check() -> HealthCheckResult:
    """Perform health check on all critical components"""
    checks: dict[str, dict[str, str | float]] = {
        "database": {"status": "error", "message": "Not checked"},
        "rpc": {"status": "error", "message": "Not checked"},
        "balance": {"status": "error", "message": "Not checked"},
        "polymarketApi": {"status": "error", "message": "Not checked"},
    }

    # Check MongoDB connection
    try:
        connection = get_connection()
        connection.admin.command("ping")
        checks["database"] = {"status": "ok", "message": "Connected"}
    except ConnectionFailure as error:
        checks["database"] = {"status": "error", "message": f"Connection failed: {error}"}
    except Exception as error:
        checks["database"] = {"status": "error", "message": f"Connection failed: {error}"}

    # Check RPC endpoint
    try:
        import requests

        response = requests.post(
            ENV["RPC_URL"],
            json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get("result"):
                checks["rpc"] = {"status": "ok", "message": "RPC endpoint responding"}
            else:
                checks["rpc"] = {"status": "error", "message": "Invalid RPC response"}
        else:
            checks["rpc"] = {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as error:
        checks["rpc"] = {"status": "error", "message": f"RPC check failed: {error}"}

    # Check USDC balance
    try:
        balance = get_my_balance(ENV["PROXY_WALLET"])
        if balance > 0:
            if balance < 10:
                checks["balance"] = {"status": "warning", "message": f"Low balance: ${balance:.2f}", "balance": balance}
            else:
                checks["balance"] = {"status": "ok", "message": f"Balance: ${balance:.2f}", "balance": balance}
        else:
            checks["balance"] = {"status": "error", "message": "Zero balance"}
    except Exception as error:
        checks["balance"] = {"status": "error", "message": f"Balance check failed: {error}"}

    # Check Polymarket API
    try:
        test_url = "https://data-api.polymarket.com/positions?user=0x0000000000000000000000000000000000000000"
        fetch_data(test_url)
        checks["polymarketApi"] = {"status": "ok", "message": "API responding"}
    except Exception as error:
        checks["polymarketApi"] = {"status": "error", "message": f"API check failed: {error}"}

    # Determine overall health
    healthy = (
        checks["database"].get("status") == "ok"
        and checks["rpc"].get("status") == "ok"
        and checks["balance"].get("status") != "error"
        and checks["polymarketApi"].get("status") == "ok"
    )

    return {"healthy": healthy, "checks": checks, "timestamp": int(__import__("time").time() * 1000)}


def log_health_check(result: HealthCheckResult) -> None:
    """Log health check results"""
    Logger.separator()
    Logger.header("🏥 HEALTH CHECK")
    Logger.info(f"Overall Status: {'✅ Healthy' if result['healthy'] else '❌ Unhealthy'}")

    db_status = result["checks"]["database"].get("status")
    Logger.info(f"Database: {'✅' if db_status == 'ok' else '❌'} {result['checks']['database'].get('message')}")

    rpc_status = result["checks"]["rpc"].get("status")
    Logger.info(f"RPC: {'✅' if rpc_status == 'ok' else '❌'} {result['checks']['rpc'].get('message')}")

    balance_status = result["checks"]["balance"].get("status")
    balance_icon = "✅" if balance_status == "ok" else "⚠️" if balance_status == "warning" else "❌"
    Logger.info(f"Balance: {balance_icon} {result['checks']['balance'].get('message')}")

    api_status = result["checks"]["polymarketApi"].get("status")
    Logger.info(f"Polymarket API: {'✅' if api_status == 'ok' else '❌'} {result['checks']['polymarketApi'].get('message')}")

    Logger.separator()
