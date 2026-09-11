from modules.face_engine import analisar_frame
from modules.face_recognition import obter_embedding, calcular_similaridade, embedding_para_bytes
from modules.database import criar_usuario_com_embeddings
from modules.registration import (
    QUANTIDADE_DE_AMOSTRAS,
    SIMILARIDADE_MAXIMA_ENTRE_AMOSTRAS,
    INSTRUCOES_POR_AMOSTRA,
)


class SessaoCadastro:
    """
    Controla o estado de uma sessao de cadastro facial em andamento.
    Nao sabe nada sobre Tkinter - so recebe frames e comandos de captura,
    e devolve o que a UI precisa mostrar.
    """

    def __init__(self):
        self.embeddings_capturados = []

    def instrucao_atual(self):
        """Texto da pose pedida para a proxima amostra."""
        if self.completo():
            return "Cadastro completo"
        return INSTRUCOES_POR_AMOSTRA[len(self.embeddings_capturados)]

    def progresso_texto(self):
        return f"{len(self.embeddings_capturados)}/{QUANTIDADE_DE_AMOSTRAS}"

    def completo(self):
        return len(self.embeddings_capturados) >= QUANTIDADE_DE_AMOSTRAS

    def avaliar_frame(self, frame):
        """Roda deteccao/embedding no frame atual e retorna a lista de rostos."""
        return analisar_frame(frame)

    def tentar_capturar(self, rostos):
        """
        Tenta aceitar uma amostra a partir dos rostos encontrados no
        frame atual (nao usa frame antigo). Retorna (sucesso, mensagem).
        """
        if self.completo():
            return False, "Cadastro ja esta completo."

        if len(rostos) == 0:
            return False, "Nenhum rosto detectado. Tente novamente."

        if len(rostos) > 1:
            return False, "Mais de um rosto detectado. Tente novamente."

        embedding_novo = obter_embedding(rostos[0])

        for embedding_existente in self.embeddings_capturados:
            similaridade = calcular_similaridade(embedding_novo, embedding_existente)
            if similaridade > SIMILARIDADE_MAXIMA_ENTRE_AMOSTRAS:
                return False, "Amostra muito parecida com uma anterior. Mude a pose."

        self.embeddings_capturados.append(embedding_novo)
        return True, "Amostra capturada."

    def finalizar(self, nome):
        """
        Salva o usuario com todos os embeddings em uma unica transacao.
        Protege a regra de so persistir quando a sessao estiver completa,
        mesmo que algum outro codigo chame este metodo incorretamente.
        Retorna (user_id, public_id). Propaga excecao se o banco falhar.
        """
        if not self.completo():
            raise ValueError("Nao e possivel finalizar: cadastro ainda esta incompleto.")

        embeddings_bytes = [embedding_para_bytes(e) for e in self.embeddings_capturados]
        user_id, public_id = criar_usuario_com_embeddings(nome, None, embeddings_bytes)
        return user_id, public_id