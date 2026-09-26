from modules.database import init_database, registrar_log_terminal
from ui.main_window import MainWindow


def main():
    init_database()

    registrar_log_terminal(
        "INFO",
        "TERMINAL_START",
        "Lancaster Access Terminal iniciado",
    )

    app = MainWindow()
    app.iniciar()


if __name__ == "__main__":
    main()