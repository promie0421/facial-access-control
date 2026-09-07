import os
import sqlite3

from config.settings import DATABASE_PATH


def get_connection():
    """Abre uma conexão com o banco."""
    pasta = os.path.dirname(DATABASE_PATH)

    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta)

    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row

    return conexao


def init_database():
    """Cria as tabelas caso ainda não existam."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            public_id TEXT UNIQUE,
            name TEXT NOT NULL,
            pin_hash TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            embedding BLOB NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)
                REFERENCES users (id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            method TEXT NOT NULL,
            result TEXT NOT NULL,
            reason TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)
                REFERENCES users (id)
                ON DELETE SET NULL
        )
    """)

    conexao.commit()
    conexao.close()


def criar_usuario(name, pin_hash):
    """Cria um usuário e gera seu public_id."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO users (name, pin_hash) VALUES (?, ?)",
        (name, pin_hash)
    )

    novo_id = cursor.lastrowid
    public_id = str(novo_id).zfill(4)

    cursor.execute(
        "UPDATE users SET public_id = ? WHERE id = ?",
        (public_id, novo_id)
    )

    conexao.commit()
    conexao.close()

    return novo_id, public_id


def criar_usuario_com_embeddings(
    name,
    pin_hash,
    embeddings_bytes
):
    """Cria usuário e embeddings em uma única transação."""
    conexao = get_connection()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO users (name, pin_hash) VALUES (?, ?)",
            (name, pin_hash)
        )

        novo_id = cursor.lastrowid
        public_id = str(novo_id).zfill(4)

        cursor.execute(
            "UPDATE users SET public_id = ? WHERE id = ?",
            (public_id, novo_id)
        )

        for embedding_bytes in embeddings_bytes:
            cursor.execute(
                """
                INSERT INTO face_embeddings (
                    user_id,
                    embedding
                )
                VALUES (?, ?)
                """,
                (novo_id, embedding_bytes)
            )

        conexao.commit()

        return novo_id, public_id

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def buscar_usuario_por_public_id(public_id):
    """Busca um usuário pelo public_id."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE public_id = ?",
        (public_id,)
    )

    usuario = cursor.fetchone()

    conexao.close()

    return usuario


def remover_usuario(user_id):
    """Remove um usuário definitivamente."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conexao.commit()
    conexao.close()


def salvar_embedding(user_id, embedding_bytes):
    """Salva um embedding vinculado ao usuário."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO face_embeddings (
            user_id,
            embedding
        )
        VALUES (?, ?)
        """,
        (user_id, embedding_bytes)
    )

    conexao.commit()
    conexao.close()


def contar_embeddings_do_usuario(user_id):
    """Conta os embeddings salvos de um usuário."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM face_embeddings
        WHERE user_id = ?
        """,
        (user_id,)
    )

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def listar_embeddings_ativos():
    """Retorna embeddings dos usuários ativos."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            users.id AS user_id,
            users.public_id,
            users.name,
            face_embeddings.embedding
        FROM face_embeddings
        JOIN users
            ON users.id = face_embeddings.user_id
        WHERE users.active = 1
    """)

    linhas = cursor.fetchall()

    conexao.close()

    return linhas


def listar_tabelas():
    """Retorna os nomes das tabelas existentes."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    )

    tabelas = [
        linha[0]
        for linha in cursor.fetchall()
    ]

    conexao.close()

    return tabelas