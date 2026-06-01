from flask import Blueprint, jsonify, request

from app.services.vault_manager import VaultManager
from app.services.privacy_engine import PrivacyEngine
from app.utils.helpers import generate_salt
from app.utils.logger import get_logger

bp = Blueprint("vault", __name__)
logger = get_logger(__name__)

_vault = VaultManager()
_privacy = PrivacyEngine()


@bp.get("/status")
def vault_status():
    return jsonify({
        **_vault.summary(),
        "encryption": "enabled" if _vault._key else "plaintext_mode",
    })


@bp.post("/commit")
def commit():
    body = request.get_json(silent=True) or {}
    required = ["symbol", "direction", "size", "entry_price", "leverage"]
    for f in required:
        if f not in body:
            return jsonify({"error": f"Missing: {f}"}), 400
    commitment = _privacy.commit_position(
        symbol=body["symbol"].upper(),
        direction=body["direction"].upper(),
        size=float(body["size"]),
        entry_price=float(body["entry_price"]),
        leverage=float(body["leverage"]),
    )
    return jsonify({
        "commitment_id": commitment.commitment_id,
        "commitment_hash": commitment.commitment_hash,
        "masked_size": commitment.masked_size,
        "created_at": commitment.created_at,
    })


@bp.get("/keygen")
def keygen():
    """Generate a new vault encryption key and commitment salt."""
    return jsonify({
        "vault_encryption_key": generate_salt(32),
        "privacy_commitment_salt": generate_salt(32),
        "note": "Store these securely in your .env file. Never commit them.",
    })
