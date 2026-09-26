import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "access_control.db")
TERMINAL_CONFIG_PATH = os.path.join(BASE_DIR, "config", "terminal.json")

# informacoes do produto
PRODUCT_NAME = "Lancaster Access Terminal"
PRODUCT_VERSION = "1.0.0"


def carregar_configuracao_terminal():
    # carrega a identificacao e configuracao desta instalacao
    with open(TERMINAL_CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


TERMINAL_CONFIG = carregar_configuracao_terminal()

COMPANY_ID = TERMINAL_CONFIG["company_id"]
COMPANY_NAME = TERMINAL_CONFIG["company_name"]
TERMINAL_ID = TERMINAL_CONFIG["terminal_id"]
TERMINAL_NAME = TERMINAL_CONFIG["terminal_name"]
CLOUD_API_URL = TERMINAL_CONFIG["cloud_api_url"]

# threshold provisorio, sera calibrado com testes reais na Etapa 16
RECOGNITION_THRESHOLD = 0.50

# quantos frames seguidos com o mesmo resultado sao necessarios para confirmar uma sessao
FRAMES_PARA_CONFIRMAR = 8

# por quanto tempo o resultado confirmado fica na tela antes do cooldown
DURACAO_RESULTADO_SEGUNDOS = 3

# tempo de cooldown apos mostrar um resultado, antes de aceitar nova tentativa
DURACAO_COOLDOWN_SEGUNDOS = 3

# intervalo minimo entre execucoes do reconhecimento facial na tela de teste
# valor provisorio, sera ajustado apos testes reais
INTERVALO_RECONHECIMENTO_MS = 250

# quantidade exata de digitos do PIN
PIN_TAMANHO = 6

# quantas tentativas invalidas de PIN sao permitidas antes do bloqueio temporario
PIN_MAX_TENTATIVAS = 3

# por quantos segundos o usuario fica bloqueado apos exceder as tentativas de PIN
PIN_BLOQUEIO_SEGUNDOS = 60

# quantos registros de log sao exibidos por padrao na tela de logs
LOGS_LIMITE_EXIBICAO = 50