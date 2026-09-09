import time

from modules.logs import registrar_log
from config.settings import (
    FRAMES_PARA_CONFIRMAR,
    DURACAO_RESULTADO_SEGUNDOS,
    DURACAO_COOLDOWN_SEGUNDOS,
)

# status de identificar_rosto() que participam da confirmacao por repeticao
STATUS_CONFIRMAVEIS = ("AUTHORIZED_FACE", "UNKNOWN_FACE")


class SessaoReconhecimento:
    """
    Controla a maquina de estados de uma sessao de reconhecimento:
    AVALIANDO -> CONFIRMADO -> COOLDOWN -> AVALIANDO.
    Nao roda deteccao nem embedding - so recebe o resultado ja pronto
    de authentication.identificar_rosto() e decide o que fazer com ele.
    """

    def __init__(self):
        self.estado = "AVALIANDO"
        self.ultimo_status = None
        self.ultimo_user_id = "sem_usuario"
        self.contador_repeticoes = 0
        self.momento_confirmacao = None
        self.momento_cooldown = None
        self.saida = {"tipo": "SEM_ROSTO"}

    def deve_avaliar(self):
        """Indica se a tela deve chamar identificar_rosto() agora."""
        return self.estado == "AVALIANDO"

    def obter_saida(self):
        return self.saida

    def processar_resultado(self, resultado):
        """Recebe o resultado de identificar_rosto() e atualiza a sessao."""
        status = resultado["status"]

        if status == "NO_FACE":
            self._resetar_contagem()
            self.saida = {"tipo": "SEM_ROSTO"}

        elif status == "MULTIPLE_FACES":
            self._resetar_contagem()
            self.saida = {"tipo": "MULTIPLOS_ROSTOS"}

        elif status == "SYSTEM_ERROR":
            self._resetar_contagem()
            self.saida = {"tipo": "ERRO", "detalhe": resultado.get("detalhe", "")}

        elif status in STATUS_CONFIRMAVEIS:
            self._processar_status_confirmavel(status, resultado)

    def _processar_status_confirmavel(self, status, resultado):
        user_id_atual = resultado.get("user_id", "sem_usuario")

        if status == self.ultimo_status and user_id_atual == self.ultimo_user_id:
            self.contador_repeticoes += 1
        else:
            self.contador_repeticoes = 1
            self.ultimo_status = status
            self.ultimo_user_id = user_id_atual

        self.saida = {"tipo": "AVALIANDO"}

        if self.contador_repeticoes >= FRAMES_PARA_CONFIRMAR:
            self._confirmar(status, resultado)

    def _confirmar(self, status, resultado):
        if status == "AUTHORIZED_FACE":
            registrar_log(resultado["user_id"], "FACE", "AUTHORIZED", None)
            self.saida = {
                "tipo": "AUTORIZADO",
                "nome": resultado["name"],
                "public_id": resultado["public_id"],
                "similaridade": resultado["similarity"],
            }
        else:  # UNKNOWN_FACE
            registrar_log(None, "FACE", "DENIED", "UNKNOWN_FACE")
            self.saida = {
                "tipo": "NEGADO",
                "similaridade": resultado.get("similarity", 0.0),
            }

        self.estado = "CONFIRMADO"
        self.momento_confirmacao = time.time()

    def atualizar_estado(self):
        """Chamado a cada ciclo da UI para tratar as transicoes por tempo."""
        agora = time.time()

        if self.estado == "CONFIRMADO":
            if agora - self.momento_confirmacao >= DURACAO_RESULTADO_SEGUNDOS:
                self.estado = "COOLDOWN"
                self.momento_cooldown = agora

        elif self.estado == "COOLDOWN":
            if agora - self.momento_cooldown >= DURACAO_COOLDOWN_SEGUNDOS:
                self._voltar_a_avaliar()

    def _resetar_contagem(self):
        self.contador_repeticoes = 0
        self.ultimo_status = None
        self.ultimo_user_id = "sem_usuario"

    def _voltar_a_avaliar(self):
        self.estado = "AVALIANDO"
        self._resetar_contagem()
        self.saida = {"tipo": "SEM_ROSTO"}