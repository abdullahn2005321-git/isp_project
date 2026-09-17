from datetime import datetime

from flask import jsonify, current_app


def server_error_response(e):
    """Log the real exception server-side and return a generic message to the client."""
    current_app.logger.exception("Unhandled server error: %s", e)
    return jsonify({
        "status": "error",
        "message": "حدث خطأ غير متوقع في السيرفر. يرجى المحاولة لاحقاً."
    }), 500


def parse_optional_date(raw):
    """Parse a 'YYYY-MM-DD' value into a date object, or None if blank/absent.

    Raises ValueError if raw is non-empty but not a valid YYYY-MM-DD date.
    """
    if raw is None or str(raw).strip() == "":
        return None
    return datetime.strptime(str(raw).strip(), "%Y-%m-%d").date()
