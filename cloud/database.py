import os
import sqlite3


CLOUD_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUD_DATABASE_PATH = os.path.join(CLOUD_DIR, "cloud.db")


def conectar():
    # abre uma conexao com o banco da Cloud
    return sqlite3.connect(CLOUD_DATABASE_PATH)


def inicializar_banco():
    # cria as tabelas iniciais da Cloud
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT NOT NULL UNIQUE,
            company_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS terminals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            terminal_id TEXT NOT NULL UNIQUE,
            company_id TEXT NOT NULL,
            terminal_name TEXT NOT NULL,
            product TEXT NOT NULL,
            version TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        )
        """
    )

    conexao.commit()
    conexao.close()


def registrar_terminal(
    company_id,
    company_name,
    terminal_id,
    terminal_name,
    product,
    version,
):
    # cadastra a empresa caso ainda nao exista e registra ou atualiza o terminal
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO companies (company_id, company_name)
        VALUES (?, ?)
        ON CONFLICT(company_id) DO UPDATE SET
            company_name = excluded.company_name
        """,
        (company_id, company_name),
    )

    cursor.execute(
        """
        INSERT INTO terminals (
            terminal_id,
            company_id,
            terminal_name,
            product,
            version
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(terminal_id) DO UPDATE SET
            company_id = excluded.company_id,
            terminal_name = excluded.terminal_name,
            product = excluded.product,
            version = excluded.version,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            terminal_id,
            company_id,
            terminal_name,
            product,
            version,
        ),
    )

    conexao.commit()
    conexao.close()