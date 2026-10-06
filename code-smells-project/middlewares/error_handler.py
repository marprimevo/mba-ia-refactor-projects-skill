from werkzeug.exceptions import HTTPException
from flask import jsonify


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, AppError):
            return handle_app_error(error)
        if isinstance(error, HTTPException):
            return jsonify({"erro": error.description, "sucesso": False}), error.code
        app.logger.exception("Erro nao tratado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
