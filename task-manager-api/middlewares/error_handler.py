from flask import jsonify
from werkzeug.exceptions import HTTPException


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, AppError):
            return handle_app_error(error)
        if isinstance(error, HTTPException):
            return jsonify({"error": error.description}), error.code
        app.logger.exception("Erro nao tratado")
        return jsonify({"error": "Erro interno"}), 500
