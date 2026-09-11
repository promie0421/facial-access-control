from modules.database import init_database
from ui.main_window import MainWindow


def main():
    init_database()

    app = MainWindow()
    app.iniciar()


if __name__ == "__main__":
    main()