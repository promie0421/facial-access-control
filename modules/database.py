import sqlite3
import os

from config.settings import DATABASE_PATH


def get_connection():
    """Abre uma conexao com o banco, criando a pasta se necessario."""
    pasta = os.path.dirname(DATABASE_PATH)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta)

    conexao = sqlite3.connect(DATABASE_PATH)

    # O SQLite nao mantem essa configuracao entre conexoes,
    # entao precisa ser ativada toda vez.
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row

    return conexao


def init_database():
    """Cria as tabelas do sistema caso ainda nao existam."""
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
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terminal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            event TEXT NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conexao.commit()
    conexao.close()


def criar_usuario(name, pin_hash):
    """
    Insere um novo usuario e gera o public_id a partir do id interno,
    tudo na mesma transacao, para evitar dois cadastros calculando
    o mesmo public_id ao mesmo tempo.

    Retorna (id_interno, public_id).
    """
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


def criar_usuario_com_embeddings(name, pin_hash, embeddings_bytes):
    """
    Cria o usuario e salva todos os embeddings em uma unica transacao.

    Se qualquer etapa falhar, nada e persistido (rollback).

    Retorna (id_interno, public_id).
    """
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
                "INSERT INTO face_embeddings (user_id, embedding) VALUES (?, ?)",
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
    """Busca um usuario pelo public_id. Retorna None se nao existir."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE public_id = ?",
        (public_id,)
    )

    usuario = cursor.fetchone()

    conexao.close()

    return usuario


def buscar_usuario_por_id(user_id):
    """Busca um usuario pelo id interno. Retorna None se nao existir."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    usuario = cursor.fetchone()

    conexao.close()

    return usuario


def remover_usuario(user_id):
    """
    Remove um usuario definitivamente.

    Os embeddings sao removidos junto (ON DELETE CASCADE) e os logs
    existentes permanecem, mas perdem a referencia ao usuario
    (ON DELETE SET NULL).
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conexao.commit()
    conexao.close()


def salvar_embedding(user_id, embedding_bytes):
    """Salva um embedding avulso vinculado ao usuario."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO face_embeddings (user_id, embedding) VALUES (?, ?)",
        (user_id, embedding_bytes)
    )

    conexao.commit()
    conexao.close()


def contar_embeddings_do_usuario(user_id):
    """Conta quantos embeddings um usuario tem salvos."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM face_embeddings WHERE user_id = ?",
        (user_id,)
    )

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def listar_embeddings_ativos():
    """Retorna todos os embeddings de usuarios ativos, com dados do usuario."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            users.id AS user_id,
            users.public_id,
            users.name,
            face_embeddings.embedding
        FROM face_embeddings
        JOIN users ON users.id = face_embeddings.user_id
        WHERE users.active = 1
    """)

    linhas = cursor.fetchall()

    conexao.close()

    return linhas


def listar_usuarios():
    """Retorna todos os usuarios cadastrados em ordem de cadastro."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM users ORDER BY id"
    )

    usuarios = cursor.fetchall()

    conexao.close()

    return usuarios


def ativar_usuario(user_id):
    """Marca um usuario como ativo."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE users SET active = 1 WHERE id = ?",
        (user_id,)
    )

    conexao.commit()
    conexao.close()


def desativar_usuario(user_id):
    """Marca um usuario como inativo, sem remover seus dados."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE users SET active = 0 WHERE id = ?",
        (user_id,)
    )

    conexao.commit()
    conexao.close()


def atualizar_pin(user_id, pin_hash):
    """Salva o hash do PIN de um usuario. Nunca recebe o PIN em texto puro."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE users SET pin_hash = ? WHERE id = ?",
        (pin_hash, user_id)
    )

    conexao.commit()
    conexao.close()


def contar_tentativas_pin_recentes(user_id, segundos):
    """
    Conta tentativas de PIN invalidas de um usuario especifico
    nos ultimos X segundos.
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM access_logs
        WHERE user_id = ?
        AND method = 'PIN'
        AND result = 'DENIED'
        AND timestamp >= datetime('now', ?)
    """, (user_id, f"-{segundos} seconds"))

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def registrar_log(user_id, method, result, reason=None):
    """Insere um registro de evento de autenticacao."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO access_logs (
            user_id,
            method,
            result,
            reason
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            method,
            result,
            reason,
        )
    )

    conexao.commit()
    conexao.close()


def listar_logs(limite):
    """Retorna os logs de acesso mais recentes."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            access_logs.timestamp,
            access_logs.method,
            access_logs.result,
            access_logs.reason,
            users.name,
            users.public_id
        FROM access_logs
        LEFT JOIN users ON users.id = access_logs.user_id
        ORDER BY access_logs.timestamp DESC
        LIMIT ?
    """, (limite,))

    linhas = cursor.fetchall()

    conexao.close()

    return linhas


def registrar_log_terminal(level, event, message=None):
    """Registra um evento tecnico do terminal."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO terminal_logs (
            level,
            event,
            message
        )
        VALUES (?, ?, ?)
        """,
        (
            level,
            event,
            message,
        )
    )

    conexao.commit()
    conexao.close()


def listar_logs_terminal(limite=100):
    """Retorna os logs tecnicos mais recentes do terminal."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            level,
            event,
            message,
            timestamp
        FROM terminal_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limite,)
    )

    linhas = cursor.fetchall()

    conexao.close()

    return linhas


def listar_tabelas():
    """Retorna os nomes das tabelas existentes no banco."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    tabelas = [linha[0] for linha in cursor.fetchall()]

    conexao.close()

    return tabelas