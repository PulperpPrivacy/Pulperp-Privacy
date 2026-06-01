import logging
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.ensure_ascii = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    from app.api.position import bp as position_bp
    from app.api.signal import bp as signal_bp
    from app.api.vault import bp as vault_bp

    app.register_blueprint(position_bp, url_prefix="/api/position")
    app.register_blueprint(signal_bp, url_prefix="/api/signal")
    app.register_blueprint(vault_bp, url_prefix="/api/vault")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "pulperp-privacy"})

    @app.before_request
    def log_req():
        from flask import request
        logger.debug(f"→ {request.method} {request.path}")

    logger.info("Pulperp Privacy backend initialized")
    return app
