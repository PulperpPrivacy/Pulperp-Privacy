import base64
import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Optional

from app.config import Config
from app.utils.logger import get_logger
from app.utils.helpers import new_id, utcnow_iso, mask_size

logger = get_logger(__name__)

# In-memory vault — in production back with encrypted file or DB
_vault: dict[str, "VaultEntry"] = {}


@dataclass
class VaultEntry:
    id: str
    symbol: str
    direction: str
    size: float
    entry_price: float
    leverage: float
    commitment_id: Optional[str] = None
    pnl_pct: Optional[float] = None
    status: str = "open"          # open | closed | liquidated
    opened_at: str = field(default_factory=utcnow_iso)
    closed_at: Optional[str] = None
    exit_price: Optional[float] = None
    # Never expose exact size in public-facing serialization
    _masked_size: str = field(init=False)

    def __post_init__(self):
        self._masked_size = mask_size(self.size)

    def to_dict(self, private: bool = False) -> dict:
        d = {
            "id": self.id,
            "symbol": self.symbol,
            "direction": self.direction,
            "leverage": self.leverage,
            "commitment_id": self.commitment_id,
            "status": self.status,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at,
            "pnl_pct": self.pnl_pct,
        }
        if private:
            d["size"] = self.size
            d["entry_price"] = self.entry_price
            d["exit_price"] = self.exit_price
        else:
            # Public view: masked size only
            d["masked_size"] = self._masked_size
            d["entry_price"] = round(self.entry_price, 0)  # rounded, not exact
        return d


class VaultManager:
    def __init__(self, config: type = Config):
        self._key = config.VAULT_ENCRYPTION_KEY
        if not self._key:
            logger.warning("VAULT_ENCRYPTION_KEY not set — vault running in plaintext mode")

    def store(
        self,
        symbol: str,
        direction: str,
        size: float,
        entry_price: float,
        leverage: float,
        commitment_id: Optional[str] = None,
    ) -> VaultEntry:
        entry = VaultEntry(
            id=new_id(),
            symbol=symbol,
            direction=direction,
            size=size,
            entry_price=entry_price,
            leverage=leverage,
            commitment_id=commitment_id,
        )
        _vault[entry.id] = entry
        logger.info(
            f"Vault: stored {symbol} {direction} {mask_size(size)} "
            f"@ ~{round(entry_price, 0)} id={entry.id[:8]}"
        )
        return entry

    def get(self, entry_id: str) -> Optional[VaultEntry]:
        return _vault.get(entry_id)

    def close_position(
        self,
        entry_id: str,
        exit_price: float,
    ) -> Optional[VaultEntry]:
        entry = _vault.get(entry_id)
        if not entry or entry.status != "open":
            return entry
        raw_pct = (exit_price - entry.entry_price) / entry.entry_price * 100
        entry.pnl_pct = raw_pct * entry.leverage if entry.direction == "LONG" else -raw_pct * entry.leverage
        entry.exit_price = exit_price
        entry.status = "closed"
        entry.closed_at = utcnow_iso()
        logger.info(f"Vault: closed {entry_id[:8]} pnl={entry.pnl_pct:+.2f}%")
        return entry

    def list_all(self, status: Optional[str] = None) -> list[VaultEntry]:
        entries = list(_vault.values())
        if status:
            entries = [e for e in entries if e.status == status]
        return entries

    def summary(self) -> dict:
        entries = list(_vault.values())
        open_entries = [e for e in entries if e.status == "open"]
        closed = [e for e in entries if e.status == "closed"]
        avg_pnl = sum(e.pnl_pct for e in closed if e.pnl_pct) / len(closed) if closed else 0.0
        return {
            "total": len(entries),
            "open": len(open_entries),
            "closed": len(closed),
            "avg_pnl_pct": round(avg_pnl, 2),
        }
