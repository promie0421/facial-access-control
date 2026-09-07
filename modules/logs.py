from modules.database import get_connection


def registrar_log(user_id, method, result, reason=None):
    """Registra um evento de autenticacao no banco."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO access_logs (user_id, method, result, reason) VALUES (?, ?, ?, ?)",
        (user_id, method, result, reason)
    )

    conexao.commit()
    conexao.close()
