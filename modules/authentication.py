from modules.face_engine import analisar_frame

from modules.face_recognition import (
    obter_embedding,
    calcular_similaridade,
    bytes_para_embedding,
)

from modules.database import listar_embeddings_ativos
from config.settings import RECOGNITION_THRESHOLD


def carregar_base_embeddings():
    """Carrega os embeddings ativos e agrupa por usuário."""
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

        embedding = bytes_para_embedding(
            linha["embedding"]
        )

        usuarios[user_id]["embeddings"].append(
            embedding
        )

    return usuarios


def melhor_correspondencia(
    embedding_capturado,
    usuarios_agrupados
):
    """Busca a maior similaridade entre os usuários."""
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
    """Identifica um único rosto no frame."""

    try:
        rostos = analisar_frame(frame)

    except Exception as erro:
        return {
            "status": "SYSTEM_ERROR",
            "detalhe": str(erro),
        }

    if len(rostos) == 0:
        return {
            "status": "NO_FACE"
        }

    if len(rostos) > 1:
        return {
            "status": "MULTIPLE_FACES"
        }

    embedding_capturado = obter_embedding(
        rostos[0]
    )

    if len(base_embeddings) == 0:
        return {
            "status": "UNKNOWN_FACE",
            "similarity": 0.0,
        }

    melhor_user_id, melhor_similaridade = (
        melhor_correspondencia(
            embedding_capturado,
            base_embeddings,
        )
    )

    if melhor_similaridade >= RECOGNITION_THRESHOLD:
        dados = base_embeddings[
            melhor_user_id
        ]

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