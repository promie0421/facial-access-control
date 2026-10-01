import threading
import time

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
SYNC_INTERVAL_SECONDS = 30

_sync_thread = None
_sync_stop_event = threading.Event()


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


def _loop_sincronizacao():
    """
    Executa a sincronizacao periodicamente em segundo plano.

    A primeira tentativa acontece imediatamente. Depois disso,
    o worker aguarda SYNC_INTERVAL_SECONDS antes da proxima tentativa.
    """
    registrar_log_terminal(
        "INFO",
        "CLOUD_SYNC_WORKER_STARTED",
        (
            "Worker de sincronizacao com a Cloud iniciado. "
            f"Intervalo: {SYNC_INTERVAL_SECONDS} segundos"
        ),
    )

    while not _sync_stop_event.is_set():
        try:
            resultado = sincronizar_logs()

            if resultado["sincronizados"] > 0:
                registrar_log_terminal(
                    "INFO",
                    "CLOUD_SYNC_SUCCESS",
                    (
                        f"{resultado['sincronizados']} evento(s) "
                        "sincronizado(s) com a Cloud"
                    ),
                )

        except Exception as erro:
            registrar_log_terminal(
                "ERROR",
                "CLOUD_SYNC_WORKER_ERROR",
                f"Erro inesperado no worker de sincronizacao: {erro}",
            )

        _sync_stop_event.wait(SYNC_INTERVAL_SECONDS)

    registrar_log_terminal(
        "INFO",
        "CLOUD_SYNC_WORKER_STOPPED",
        "Worker de sincronizacao com a Cloud encerrado",
    )


def iniciar_sincronizacao_automatica():
    """
    Inicia o worker de sincronizacao em uma daemon thread.

    Se o worker ja estiver em execucao, nenhuma segunda thread
    sera criada.
    """
    global _sync_thread

    if _sync_thread is not None and _sync_thread.is_alive():
        return False

    _sync_stop_event.clear()

    _sync_thread = threading.Thread(
        target=_loop_sincronizacao,
        name="LancasterCloudSync",
        daemon=True,
    )

    _sync_thread.start()

    return True


def parar_sincronizacao_automatica():
    """
    Solicita o encerramento do worker de sincronizacao.

    A chamada nao bloqueia a interface esperando a thread terminar.
    """
    _sync_stop_event.set()