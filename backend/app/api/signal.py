from flask import Blueprint, jsonify, request

from app.services.signal_generator import SignalGenerator
from app.config import Config
from app.utils.logger import get_logger

bp = Blueprint("signal", __name__)
logger = get_logger(__name__)

_generator = SignalGenerator()
_history: list[dict] = []


@bp.post("/generate")
def generate():
    body = request.get_json(silent=True) or {}
    symbol = body.get("symbol", "SOL-PERP").upper()
    blind = body.get("blind", True)

    if symbol not in Config.SUPPORTED_MARKETS:
        return jsonify({"error": f"Unsupported: {symbol}"}), 400
    try:
        sig = _generator.generate(symbol, blind=blind)
        result = sig.to_dict()
        _history.insert(0, result)
        if len(_history) > 100:
            _history.pop()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Signal error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.post("/generate-all")
def generate_all():
    blind = (request.get_json(silent=True) or {}).get("blind", True)
    try:
        signals = _generator.generate_all(blind=blind)
        results = [s.to_dict() for s in signals]
        for r in results:
            _history.insert(0, r)
        _history[:] = _history[:100]
        return jsonify({"signals": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/history")
def history():
    limit = min(int(request.args.get("limit", 20)), 100)
    symbol = request.args.get("symbol")
    data = [s for s in _history if not symbol or s["symbol"] == symbol.upper()]
    return jsonify({"signals": data[:limit], "total": len(data)})


@bp.get("/markets")
def markets():
    return jsonify({"markets": Config.SUPPORTED_MARKETS})
