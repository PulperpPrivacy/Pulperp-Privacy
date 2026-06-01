from dataclasses import dataclass, field
from typing import Optional
from app.utils.helpers import utcnow_iso, mask_size


@dataclass
class PrivatePosition:
    id: str
    symbol: str
    direction: str
    size: float
    entry_price: float
    leverage: float
    commitment_hash: str
    status: str = "open"
    pnl_pct: Optional[float] = None
    opened_at: str = field(default_factory=utcnow_iso)

    def to_dict(self, reveal: bool = False) -> dict:
        d = {
            "id": self.id, "symbol": self.symbol,
            "direction": self.direction, "leverage": self.leverage,
            "commitment_hash": self.commitment_hash[:16] + "...",
            "status": self.status, "pnl_pct": self.pnl_pct,
            "opened_at": self.opened_at,
        }
        if reveal:
            d["size"] = self.size
            d["entry_price"] = self.entry_price
        else:
            d["masked_size"] = mask_size(self.size)
            d["entry_price_approx"] = round(self.entry_price, -1)
        return d
