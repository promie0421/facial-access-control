from modules.database import (
    registrar_log as registrar_log_no_banco,
    listar_logs as listar_logs_do_banco,
)
from config.settings import LOGS_LIMITE_EXIBICAO


def registrar_log(user_id, method, result, reason=None):
    """Registra um evento de autenticacao."""
    registrar_log_no_banco(
        user_id,
        method,
        result,
        reason,
    )


def listar_logs(limite=None):
    """Retorna os logs mais recentes."""
    if limite is None:
        limite = LOGS_LIMITE_EXIBICAO

    return listar_logs_do_banco(limite)