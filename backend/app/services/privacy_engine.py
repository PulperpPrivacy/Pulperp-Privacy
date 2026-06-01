import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from typing import Optional

from app.config import Config
from app.utils.logger import get_logger
from app.utils.helpers import generate_commitment, generate_salt, mask_size, new_id, utcnow_iso

logger = get_logger(__name__)


@dataclass
class PositionCommitment:
    commitment_id: str
    commitment_hash: str
    masked_size: str
    symbol: str
    direction: str
    created_at: str = field(default_factory=utcnow_iso)
    revealed: bool = False
    reveal_hash: Optional[str] = None


@dataclass
class RevealedPosition:
    commitment_id: str
    symbol: str
    direction: str
    size: float
    entry_price: float
    leverage: float
    reveal_at: str = field(default_factory=utcnow_iso)


class PrivacyEngine:
    def __init__(self, config: type = Config):
        self._salt = config.PRIVACY_COMMITMENT_SALT or generate_salt()
        logger.info("Privacy engine initialized")

    def commit_position(
        self,
        symbol: str,
        direction: str,
        size: float,
        entry_price: float,
        leverage: float,
    ) -> PositionCommitment:
        """
        Create a commitment to a position without revealing exact size on-chain.
        The commitment is H(symbol || direction || size || entry || leverage || salt).
        """
        nonce = generate_salt(16)
        payload = f"{symbol}:{direction}:{size}:{entry_price}:{leverage}:{nonce}:{self._salt}"
        commitment_hash = hashlib.sha256(payload.encode()).hexdigest()

        commitment = PositionCommitment(
            commitment_id=new_id(),
            commitment_hash=commitment_hash,
            masked_size=mask_size(size),
            symbol=symbol,
            direction=direction,
        )
        logger.info(
            f"Position committed: {symbol} {direction} size={mask_size(size)} "
            f"hash={commitment_hash[:16]}..."
        )
        return commitment

    def reveal_commitment(
        self,
        commitment: PositionCommitment,
        size: float,
        entry_price: float,
        leverage: float,
    ) -> RevealedPosition:
        """Reveal the actual position details — use only when settlement requires it."""
        reveal_hash = hashlib.sha256(
            f"reveal:{commitment.commitment_id}:{size}:{entry_price}".encode()
        ).hexdigest()
        commitment.revealed = True
        commitment.reveal_hash = reveal_hash
        logger.info(f"Position revealed: {commitment.commitment_id[:8]}")
        return RevealedPosition(
            commitment_id=commitment.commitment_id,
            symbol=commitment.symbol,
            direction=commitment.direction,
            size=size,
            entry_price=entry_price,
            leverage=leverage,
        )

    def blind_query_key(self, wallet: str) -> str:
        """
        Generate a one-time query key that dissociates wallet from the RPC query.
        Prevents associating wallet address with specific market data requests.
        """
        nonce = generate_salt(8)
        return hashlib.sha256(f"{wallet}:{nonce}:{self._salt}".encode()).hexdigest()[:32]

    def verify_commitment(self, commitment_hash: str, payload: str) -> bool:
        expected = hashlib.sha256(payload.encode()).hexdigest()
        return hmac.compare_digest(commitment_hash, expected)
