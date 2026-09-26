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

        return {
            "online": resposta.ok,
            "status_code": resposta.status_code,
        }

    except requests.RequestException:
        return {
            "online": False,
            "status_code": None,
        }