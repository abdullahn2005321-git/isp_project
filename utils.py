from flask import jsonify, current_app


def server_error_response(e):
    """Log the real exception server-side and return a generic message to the client."""
    current_app.logger.exception("Unhandled server error: %s", e)
    return jsonify({
        "status": "error",
        "message": "حدث خطأ غير متوقع في السيرفر. يرجى المحاولة لاحقاً."
    }), 500
