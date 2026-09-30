from fastapi import HTTPException

from cloud.database import buscar_terminal, registrar_terminal
from cloud.schemas import TerminalRegistro


def processar_registro_terminal(terminal: TerminalRegistro):
    terminal_existente = buscar_terminal(terminal.terminal_id)

    if terminal_existente is not None:
        company_id_atual = terminal_existente[1]

        if company_id_atual != terminal.company_id:
            raise HTTPException(
                status_code=409,
                detail="terminal_id pertence a outra empresa",
            )

    registrar_terminal(
        company_id=terminal.company_id,
        company_name=terminal.company_name,
        terminal_id=terminal.terminal_id,
        terminal_name=terminal.terminal_name,
        product=terminal.product,
        version=terminal.version,
    )

    return {
        "status": "registered",
        "company_id": terminal.company_id,
        "terminal_id": terminal.terminal_id,
        "terminal_name": terminal.terminal_name,
    }