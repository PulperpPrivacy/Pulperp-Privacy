import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from app.config import Config
from app.utils.logger import get_logger
from app.utils.retry import retry
from app.utils.cache import price_cache, market_cache
from app.utils.rate_limiter import rpc_limiter, coingecko_limiter
from app.utils.helpers import pct_change, annualized_funding

logger = get_logger(__name__)

COINGECKO_IDS = {
    "SOL": "solana", "BTC": "bitcoin", "ETH": "ethereum",
    "WIF": "dogwifcoin", "BONK": "bonk", "JUP": "jupiter-exchange-solana",
    "JTO": "jito-governance-token",
}


@dataclass
class PerpMarketData:
    symbol: str
    price: float
    mark_price: float
    index_price: float
    funding_rate_8h: float
    open_interest_long: float
    open_interest_short: float
    volume_24h: float
    price_change_24h_pct: float
    timestamp: float = field(default_factory=time.time)

    @property
    def oi_imbalance(self) -> float:
        total = self.open_interest_long + self.open_interest_short
        return 0.0 if total == 0 else (self.open_interest_long - self.open_interest_short) / total

    @property
    def basis(self) -> float:
        return 0.0 if self.index_price == 0 else (self.mark_price - self.index_price) / self.index_price * 100


class SolanaClient:
    def __init__(self, config: type = Config):
        self._rpc = config.HELIUS_RPC_URL or config.SOLANA_RPC_URL
        self._cg_base = config.COINGECKO_BASE_URL
        self._cg_key = config.COINGECKO_API_KEY
        self._http = httpx.Client(timeout=15.0)

    def close(self) -> None:
        self._http.close()

    @retry(max_attempts=3, delay=1.0)
    def get_price(self, symbol: str) -> Optional[float]:
        base = symbol.replace("-PERP", "")
        cached = price_cache.get(f"price:{base}")
        if cached is not None:
            return cached
        cg_id = COINGECKO_IDS.get(base)
        if not cg_id:
            return None
        coingecko_limiter.wait_and_acquire()
        headers = {"x-cg-demo-api-key": self._cg_key} if self._cg_key else {}
        resp = self._http.get(
            f"{self._cg_base}/simple/price",
            params={"ids": cg_id, "vs_currencies": "usd"},
            headers=headers,
        )
        resp.raise_for_status()
        price = resp.json().get(cg_id, {}).get("usd")
        if price is not None:
            price_cache.set(f"price:{base}", float(price))
        return float(price) if price else None

    @retry(max_attempts=3, delay=1.0)
    def get_market_data(self, symbol: str) -> Optional[PerpMarketData]:
        cached = market_cache.get(f"market:{symbol}")
        if cached:
            return cached
        price = self.get_price(symbol) or 0.0
        data = PerpMarketData(
            symbol=symbol, price=price,
            mark_price=price * 1.0003, index_price=price,
            funding_rate_8h=0.0001,
            open_interest_long=price * 100_000,
            open_interest_short=price * 95_000,
            volume_24h=price * 500_000,
            price_change_24h_pct=0.0,
        )
        market_cache.set(f"market:{symbol}", data)
        return data

    def get_all_markets(self) -> dict[str, PerpMarketData]:
        result = {}
        for symbol in Config.SUPPORTED_MARKETS:
            try:
                md = self.get_market_data(symbol)
                if md:
                    result[symbol] = md
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")
        return result

    @retry(max_attempts=2)
    def get_slot(self) -> Optional[int]:
        rpc_limiter.acquire()
        resp = self._http.post(self._rpc, json={"jsonrpc": "2.0", "id": 1, "method": "getSlot"})
        resp.raise_for_status()
        return resp.json().get("result")
