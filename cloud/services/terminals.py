from cloud.database import registrar_terminal
from cloud.schemas import TerminalRegistro


def processar_registro_terminal(terminal: TerminalRegistro):
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