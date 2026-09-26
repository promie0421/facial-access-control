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
    # monta os dados que identificam este terminal para o futuro servidor
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