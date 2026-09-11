import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from modules.face_engine import analisar_frame
from modules.face_recognition import obter_embedding, calcular_similaridade, bytes_para_embedding
from modules.database import (
    listar_embeddings_ativos,
    buscar_usuario_por_public_id,
    atualizar_pin,
    contar_tentativas_pin_recentes,
)
from modules.logs import registrar_log
from config.settings import (
    RECOGNITION_THRESHOLD,
    PIN_TAMANHO,
    PIN_MAX_TENTATIVAS,
    PIN_BLOQUEIO_SEGUNDOS,
)


# ---------- Reconhecimento facial ----------

def carregar_base_embeddings():
    """
    Le os embeddings ativos do banco UMA vez, converte para numpy
    e agrupa por usuario. O resultado deve ser mantido em memoria
    durante a sessao de reconhecimento.
    """
    linhas = listar_embeddings_ativos()

    usuarios = {}

    for linha in linhas:
        user_id = linha["user_id"]

        if user_id not in usuarios:
            usuarios[user_id] = {
                "public_id": linha["public_id"],
                "name": linha["name"],
                "embeddings": [],
            }

        embedding = bytes_para_embedding(linha["embedding"])
        usuarios[user_id]["embeddings"].append(embedding)

    return usuarios


def melhor_correspondencia(embedding_capturado, usuarios_agrupados):
    """
    Para cada usuario, usa a maior similaridade entre suas amostras salvas.
    Retorna o usuario com a maior pontuacao entre todos.
    """
    melhor_user_id = None
    melhor_similaridade = -1.0

    for user_id, dados in usuarios_agrupados.items():
        for embedding_salvo in dados["embeddings"]:
            similaridade = calcular_similaridade(
                embedding_capturado,
                embedding_salvo,
            )

            if similaridade > melhor_similaridade:
                melhor_similaridade = similaridade
                melhor_user_id = user_id

    return melhor_user_id, melhor_similaridade


def identificar_rosto(frame, base_embeddings):
    """
    Roda deteccao + reconhecimento em um frame usando uma base de
    embeddings ja carregada em memoria.
    """
    try:
        rostos = analisar_frame(frame)
    except Exception as erro:
        return {
            "status": "SYSTEM_ERROR",
            "detalhe": str(erro),
        }

    if len(rostos) == 0:
        return {"status": "NO_FACE"}

    if len(rostos) > 1:
        return {"status": "MULTIPLE_FACES"}

    embedding_capturado = obter_embedding(rostos[0])

    if len(base_embeddings) == 0:
        return {
            "status": "UNKNOWN_FACE",
            "similarity": 0.0,
        }

    melhor_user_id, melhor_similaridade = melhor_correspondencia(
        embedding_capturado,
        base_embeddings,
    )

    if melhor_similaridade >= RECOGNITION_THRESHOLD:
        dados = base_embeddings[melhor_user_id]

        return {
            "status": "AUTHORIZED_FACE",
            "user_id": melhor_user_id,
            "public_id": dados["public_id"],
            "name": dados["name"],
            "similarity": melhor_similaridade,
        }

    return {
        "status": "UNKNOWN_FACE",
        "similarity": melhor_similaridade,
    }


# ---------- Autenticacao por PIN ----------

_hasher = PasswordHasher()


def pin_e_valido_formato(pin):
    """Verifica se o PIN tem exatamente PIN_TAMANHO digitos numericos."""
    return bool(
        re.fullmatch(
            r"\d{" + str(PIN_TAMANHO) + "}",
            pin,
        )
    )


def gerar_hash_pin(pin):
    """Gera o hash Argon2 de um PIN."""
    if not pin_e_valido_formato(pin):
        raise ValueError(
            f"O PIN deve ter exatamente {PIN_TAMANHO} digitos numericos."
        )

    return _hasher.hash(pin)


def definir_pin_usuario(user_id, pin):
    """Gera o hash e salva o PIN do usuario no banco."""
    hash_pin = gerar_hash_pin(pin)
    atualizar_pin(user_id, hash_pin)


def autenticar_por_pin(public_id, pin):
    """
    Autentica um usuario pelo public_id + PIN.

    O lockout desta V1 funciona por usuario.
    Bloqueio global do terminal nao esta implementado.
    """
    usuario = buscar_usuario_por_public_id(public_id)

    # Public ID inexistente, conta inativa ou sem PIN recebem
    # a mesma resposta generica.
    if (
        usuario is None
        or usuario["active"] == 0
        or usuario["pin_hash"] is None
    ):
        return {"status": "PIN_INVALID"}

    tentativas_recentes = contar_tentativas_pin_recentes(
        usuario["id"],
        PIN_BLOQUEIO_SEGUNDOS,
    )

    if tentativas_recentes >= PIN_MAX_TENTATIVAS:
        return {"status": "LOCKOUT"}

    try:
        _hasher.verify(usuario["pin_hash"], pin)

    except VerifyMismatchError:
        registrar_log(
            usuario["id"],
            "PIN",
            "DENIED",
            "PIN_INVALID",
        )

        return {"status": "PIN_INVALID"}

    except Exception as erro:
        return {
            "status": "SYSTEM_ERROR",
            "detalhe": str(erro),
        }

    registrar_log(
        usuario["id"],
        "PIN",
        "AUTHORIZED",
        None,
    )

    return {
        "status": "AUTHORIZED_PIN",
        "user_id": usuario["id"],
        "public_id": usuario["public_id"],
        "name": usuario["name"],
    }