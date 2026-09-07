import numpy as np


def obter_embedding(rosto):
    """Retorna o embedding normalizado do rosto."""
    return rosto.normed_embedding.astype(np.float32)


def calcular_similaridade(embedding_a, embedding_b):
    """Calcula a similaridade de cosseno."""
    a = np.asarray(embedding_a, dtype=np.float32)
    b = np.asarray(embedding_b, dtype=np.float32)

    return float(
        np.dot(a, b) /
        (np.linalg.norm(a) * np.linalg.norm(b))
    )


def embedding_para_bytes(embedding):
    """Converte o embedding para bytes."""
    return np.asarray(
        embedding,
        dtype=np.float32
    ).tobytes()


def bytes_para_embedding(dado_blob):
    """Converte os bytes de volta para um embedding."""
    return np.frombuffer(
        dado_blob,
        dtype=np.float32
    )