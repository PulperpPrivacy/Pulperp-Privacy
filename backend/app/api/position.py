from flask import Blueprint, jsonify, request

from app.services.privacy_engine import PrivacyEngine
from app.services.vault_manager import VaultManager
from app.config import Config
from app.utils.logger import get_logger

bp = Blueprint("position", __name__)
logger = get_logger(__name__)

_privacy = PrivacyEngine()
_vault = VaultManager()


@bp.post("/open")
def open_position():
    body = request.get_json(silent=True) or {}
    required = ["symbol", "direction", "size", "entry_price", "leverage"]
    for f in required:
        if f not in body:
            return jsonify({"error": f"Missing: {f}"}), 400

    symbol = body["symbol"].upper()
    if symbol not in Config.SUPPORTED_MARKETS:
        return jsonify({"error": f"Unsupported market: {symbol}"}), 400

    try:
        commitment = _privacy.commit_position(
            symbol=symbol,
            direction=body["direction"].upper(),
            size=float(body["size"]),
            entry_price=float(body["entry_price"]),
            leverage=float(body["leverage"]),
        )
        entry = _vault.store(
            symbol=symbol,
            direction=body["direction"].upper(),
            size=float(body["size"]),
            entry_price=float(body["entry_price"]),
            leverage=float(body["leverage"]),
            commitment_id=commitment.commitment_id,
        )
        return jsonify({
            "vault_id": entry.id,
            "commitment_id": commitment.commitment_id,
            "commitment_hash": commitment.commitment_hash[:16] + "...",
            "masked_size": commitment.masked_size,
            "symbol": symbol,
            "direction": entry.direction,
            "status": entry.status,
        }), 201
    except Exception as e:
        logger.error(f"Open position error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/<vault_id>/close")
def close_position(vault_id: str):
    body = request.get_json(silent=True) or {}
    exit_price = body.get("exit_price")
    if not exit_price:
        return jsonify({"error": "exit_price required"}), 400
    entry = _vault.close_position(vault_id, float(exit_price))
    if not entry:
        return jsonify({"error": "Position not found"}), 404
    return jsonify(entry.to_dict(private=False))


@bp.get("/")
def list_positions():
    status = request.args.get("status")
    private = request.args.get("private", "false").lower() == "true"
    entries = _vault.list_all(status=status)
    return jsonify({
        "positions": [e.to_dict(private=private) for e in entries],
        "total": len(entries),
    })


@bp.get("/summary")
def summary():
    return jsonify(_vault.summary())


@bp.get("/<vault_id>")
def get_position(vault_id: str):
    private = request.args.get("private", "false").lower() == "true"
    entry = _vault.get(vault_id)
    if not entry:
        return jsonify({"error": "Not found"}), 404
    return jsonify(entry.to_dict(private=private))
