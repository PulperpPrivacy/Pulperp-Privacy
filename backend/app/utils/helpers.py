import hashlib
import hmac
import os
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def utcnow_iso() -> str:
    return utcnow().isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


def pct_change(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return (new - old) / abs(old) * 100.0


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def safe_div(num: float, den: float, default: float = 0.0) -> float:
    return default if den == 0 else num / den


def trim_context(text: str, max_tokens: int = 4000) -> str:
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def generate_commitment(value: str, salt: str) -> str:
    """Pedersen-style commitment: H(value || salt)"""
    payload = f"{value}:{salt}".encode()
    return hashlib.sha256(payload).hexdigest()


def generate_salt(length: int = 32) -> str:
    return secrets.token_hex(length)


def mask_size(size: float, precision: int = 1) -> str:
    """Round to nearest bucket to avoid exact size leakage."""
    buckets = [0.1, 0.5, 1, 5, 10, 25, 50, 100, 250, 500, 1000]
    for b in buckets:
        if size <= b:
            return f"<{b}"
    return f">{buckets[-1]}"


def short_id(full_id: str) -> str:
    return full_id[:8] if len(full_id) >= 8 else full_id


def annualized_funding(rate_8h: float) -> float:
    return ((1 + rate_8h) ** (3 * 365) - 1) * 100
