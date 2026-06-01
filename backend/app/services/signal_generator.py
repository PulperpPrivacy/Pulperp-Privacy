import uuid
from dataclasses import dataclass, field
from typing import Optional

from app.config import Config
from app.services.solana_client import SolanaClient, PerpMarketData
from app.services.llm_analyst import LLMAnalyst, AnalystSignal
from app.utils.logger import get_logger
from app.utils.helpers import (
    utcnow_iso, new_id, pct_change, clamp, annualized_funding,
)

logger = get_logger(__name__)


def _build_summary(market: PerpMarketData) -> str:
    ann = annualized_funding(market.funding_rate_8h)
    return (
        f"{market.symbol} @ ${market.price:,.2f} | "
        f"24h: {market.price_change_24h_pct:+.2f}% | "
        f"Funding: {market.funding_rate_8h * 100:.4f}% (8h) / {ann:.1f}% ann | "
        f"OI Imbalance: {market.oi_imbalance * 100:+.1f}% | "
        f"Basis: {market.basis:+.4f}% | "
        f"Vol 24h: ${market.volume_24h:,.0f}"
    )


@dataclass
class PrivateSignal:
    id: str = field(default_factory=new_id)
    symbol: str = ""
    direction: str = "NEUTRAL"
    confidence: float = 0.0
    timeframe: str = "4h"
    thesis: str = ""
    risks: list[str] = field(default_factory=list)
    privacy_note: str = ""
    funding_rate_8h: float = 0.0
    oi_imbalance: float = 0.0
    price: float = 0.0
    blind_mode: bool = True
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "symbol": self.symbol,
            "direction": self.direction, "confidence": self.confidence,
            "timeframe": self.timeframe, "thesis": self.thesis,
            "risks": self.risks, "privacy_note": self.privacy_note,
            "funding_rate_8h": self.funding_rate_8h,
            "oi_imbalance": self.oi_imbalance, "price": self.price,
            "blind_mode": self.blind_mode, "created_at": self.created_at,
        }


class SignalGenerator:
    def __init__(
        self,
        solana_client: Optional[SolanaClient] = None,
        analyst: Optional[LLMAnalyst] = None,
        config: type = Config,
    ):
        self._client = solana_client or SolanaClient(config)
        self._analyst = analyst or LLMAnalyst(config)
        self._threshold = config.SIGNAL_CONFIDENCE_THRESHOLD

    def generate(self, symbol: str, blind: bool = True) -> PrivateSignal:
        logger.info(f"Generating {'blind' if blind else 'standard'} signal for {symbol}")
        market = self._client.get_market_data(symbol)
        if not market:
            raise ValueError(f"No market data for {symbol}")

        summary = _build_summary(market)
        result: AnalystSignal = self._analyst.analyze(summary, blind=blind)

        return PrivateSignal(
            symbol=symbol,
            direction=result.direction,
            confidence=result.confidence,
            timeframe=result.timeframe,
            thesis=result.thesis,
            risks=result.risks,
            privacy_note=result.privacy_note,
            funding_rate_8h=market.funding_rate_8h,
            oi_imbalance=market.oi_imbalance,
            price=market.price,
            blind_mode=blind,
        )

    def generate_all(self, blind: bool = True) -> list[PrivateSignal]:
        signals = []
        for symbol in Config.SUPPORTED_MARKETS:
            try:
                sig = self.generate(symbol, blind=blind)
                if sig.confidence >= self._threshold:
                    signals.append(sig)
            except Exception as e:
                logger.error(f"Signal failed for {symbol}: {e}")
        return signals
