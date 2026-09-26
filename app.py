from modules.database import init_database, registrar_log_terminal
from ui.main_window import MainWindow


def executar_terminal():
    registrar_log_terminal(
        "INFO",
        "TERMINAL_START",
        "Lancaster Access Terminal iniciado",
    )

    app = MainWindow()
    app.iniciar()


def main():
    init_database()

    try:
        executar_terminal()

    except Exception as erro:
        registrar_log_terminal(
            "ERROR",
            "TERMINAL_FATAL_ERROR",
            f"Erro inesperado: {type(erro).__name__}: {erro}",
        )

        raise


if __name__ == "__main__":
    main()