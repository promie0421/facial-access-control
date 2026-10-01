from modules.database import (
    init_database,
    registrar_log_terminal,
)
from modules.cloud_sync import (
    iniciar_sincronizacao_automatica,
    parar_sincronizacao_automatica,
)

from ui.main_window import MainWindow


def executar_terminal():
    init_database()

    registrar_log_terminal(
        "INFO",
        "TERMINAL_START",
        "Lancaster Access Terminal iniciado",
    )

    iniciar_sincronizacao_automatica()

    try:
        app = MainWindow()
        app.iniciar()
    finally:
        parar_sincronizacao_automatica()


if __name__ == "__main__":
    executar_terminal()