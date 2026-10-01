import requests

from config.settings import (
    CLOUD_API_URL,
    COMPANY_ID,
    TERMINAL_ID,
)

from modules.database import (
    listar_logs_pendentes_sync,
    marcar_log_como_sincronizado,
    registrar_log_terminal,
)


SYNC_TIMEOUT_SECONDS = 5


def sincronizar_logs(limite=100):
    """
    Envia logs pendentes para a Lancaster Cloud.

    O terminal continua funcionando offline caso a Cloud esteja
    indisponivel.

    Um evento somente e marcado como sincronizado localmente depois
    que a Cloud confirma o recebimento.
    """
    pendentes = listar_logs_pendentes_sync(limite)

    resultado = {
        "encontrados": len(pendentes),
        "sincronizados": 0,
        "falhas": 0,
    }

    for log in pendentes:
        payload = {
            "event_id": log["event_id"],
            "company_id": COMPANY_ID,
            "terminal_id": TERMINAL_ID,
            "user_public_id": log["user_public_id"],
            "method": log["method"],
            "result": log["result"],
            "reason": log["reason"],
            "event_timestamp": log["event_timestamp"],
        }

        try:
            resposta = requests.post(
                f"{CLOUD_API_URL}/access-logs/sync",
                json=payload,
                timeout=SYNC_TIMEOUT_SECONDS,
            )

        except requests.RequestException as erro:
            registrar_log_terminal(
                "WARNING",
                "CLOUD_SYNC_OFFLINE",
                f"Nao foi possivel sincronizar logs: {erro}",
            )

            resultado["falhas"] += 1
            break

        if resposta.status_code != 200:
            registrar_log_terminal(
                "WARNING",
                "CLOUD_SYNC_ERROR",
                (
                    f"Falha ao sincronizar evento "
                    f"{log['event_id']}. "
                    f"HTTP {resposta.status_code}"
                ),
            )

            resultado["falhas"] += 1
            continue

        try:
            dados = resposta.json()
        except ValueError:
            registrar_log_terminal(
                "WARNING",
                "CLOUD_SYNC_INVALID_RESPONSE",
                (
                    f"Resposta invalida da Cloud para o evento "
                    f"{log['event_id']}"
                ),
            )

            resultado["falhas"] += 1
            continue

        if dados.get("status") != "received":
            registrar_log_terminal(
                "WARNING",
                "CLOUD_SYNC_REJECTED",
                (
                    f"Cloud nao confirmou o evento "
                    f"{log['event_id']}"
                ),
            )

            resultado["falhas"] += 1
            continue

        marcado = marcar_log_como_sincronizado(
            log["event_id"]
        )

        if marcado:
            resultado["sincronizados"] += 1
        else:
            registrar_log_terminal(
                "WARNING",
                "CLOUD_SYNC_LOCAL_ERROR",
                (
                    f"Evento {log['event_id']} recebido pela Cloud, "
                    f"mas nao foi marcado localmente"
                ),
            )

            resultado["falhas"] += 1

    return resultado