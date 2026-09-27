import json
import os
import sys


def obter_diretorio_base():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = obter_diretorio_base()

DATABASE_PATH = os.path.join(BASE_DIR, "database", "access_control.db")
TERMINAL_CONFIG_PATH = os.path.join(BASE_DIR, "config", "terminal.json")

PRODUCT_NAME = "Lancaster Access Terminal"
PRODUCT_VERSION = "1.0.0"


def carregar_configuracao_terminal():
    with open(TERMINAL_CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


TERMINAL_CONFIG = carregar_configuracao_terminal()

COMPANY_ID = TERMINAL_CONFIG["company_id"]
COMPANY_NAME = TERMINAL_CONFIG["company_name"]
TERMINAL_ID = TERMINAL_CONFIG["terminal_id"]
TERMINAL_NAME = TERMINAL_CONFIG["terminal_name"]
CLOUD_API_URL = TERMINAL_CONFIG["cloud_api_url"]

RECOGNITION_THRESHOLD = 0.50

FRAMES_PARA_CONFIRMAR = 8
DURACAO_RESULTADO_SEGUNDOS = 3
DURACAO_COOLDOWN_SEGUNDOS = 3
INTERVALO_RECONHECIMENTO_MS = 250

PIN_TAMANHO = 6
PIN_MAX_TENTATIVAS = 3
PIN_BLOQUEIO_SEGUNDOS = 60

LOGS_LIMITE_EXIBICAO = 50