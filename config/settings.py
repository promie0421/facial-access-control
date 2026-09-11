import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "access_control.db")

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