from fastapi import HTTPException

from cloud.database import buscar_terminal, registrar_access_log
from cloud.schemas import AccessLogSync


def processar_access_log(log: AccessLogSync):
    """Valida e registra um evento de acesso recebido de um terminal."""
    terminal = buscar_terminal(log.terminal_id)

    if terminal is None:
        raise HTTPException(
            status_code=404,
            detail="terminal nao encontrado",
        )

    company_id_terminal = terminal[1]

    if company_id_terminal != log.company_id:
        raise HTTPException(
            status_code=409,
            detail="terminal nao pertence a empresa informada",
        )

    inserido = registrar_access_log(
        event_id=log.event_id,
        company_id=log.company_id,
        terminal_id=log.terminal_id,
        user_public_id=log.user_public_id,
        method=log.method,
        result=log.result,
        reason=log.reason,
        event_timestamp=log.event_timestamp,
    )

    return {
        "status": "received",
        "event_id": log.event_id,
        "inserted": inserido,
    }