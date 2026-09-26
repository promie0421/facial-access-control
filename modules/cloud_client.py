import requests

from config.settings import (
    PRODUCT_NAME,
    PRODUCT_VERSION,
    COMPANY_ID,
    COMPANY_NAME,
    TERMINAL_ID,
    TERMINAL_NAME,
    CLOUD_API_URL,
)

from modules.database import registrar_log_terminal


def obter_identidade_terminal():
    # monta os dados que identificam este terminal para o servidor
    return {
        "product": PRODUCT_NAME,
        "version": PRODUCT_VERSION,
        "company_id": COMPANY_ID,
        "company_name": COMPANY_NAME,
        "terminal_id": TERMINAL_ID,
        "terminal_name": TERMINAL_NAME,
    }


def obter_cloud_api_url():
    # retorna o endereco configurado para a API Lancaster Access Cloud
    return CLOUD_API_URL


def verificar_conexao_cloud():
    # verifica se a API esta acessivel sem interromper o funcionamento local
    url = f"{CLOUD_API_URL}/health"

    try:
        resposta = requests.get(url, timeout=3)

        if resposta.ok:
            registrar_log_terminal(
                "INFO",
                "CLOUD_ONLINE",
                f"Cloud acessivel. HTTP {resposta.status_code}",
            )
        else:
            registrar_log_terminal(
                "WARNING",
                "CLOUD_ERROR",
                f"Cloud respondeu com HTTP {resposta.status_code}",
            )

        return {
            "online": resposta.ok,
            "status_code": resposta.status_code,
        }

    except requests.RequestException as erro:
        registrar_log_terminal(
            "WARNING",
            "CLOUD_OFFLINE",
            f"Nao foi possivel conectar com a Cloud: {erro}",
        )

        return {
            "online": False,
            "status_code": None,
        }


def registrar_terminal_cloud():
    # envia a identidade deste terminal para a Cloud
    url = f"{CLOUD_API_URL}/terminals/register"
    dados = obter_identidade_terminal()

    try:
        resposta = requests.post(
            url,
            json=dados,
            timeout=5,
        )

        if resposta.ok:
            registrar_log_terminal(
                "INFO",
                "CLOUD_TERMINAL_REGISTERED",
                f"Terminal {TERMINAL_ID} registrado na Cloud",
            )

            return resposta.json()

        registrar_log_terminal(
            "WARNING",
            "CLOUD_TERMINAL_REGISTER_ERROR",
            f"Falha ao registrar terminal. HTTP {resposta.status_code}",
        )

        return {
            "status": "error",
            "status_code": resposta.status_code,
        }

    except requests.RequestException as erro:
        registrar_log_terminal(
            "WARNING",
            "CLOUD_OFFLINE",
            f"Nao foi possivel registrar o terminal na Cloud: {erro}",
        )

        return {
            "status": "offline",
            "status_code": None,
        }