import os
import sys

from insightface.app import FaceAnalysis


_face_app = None


def obter_diretorio_modelos():
    """Define onde o InsightFace deve procurar os modelos."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "models")

    return os.path.join(os.path.expanduser("~"), ".insightface")


def carregar_modelo():
    """Carrega deteccao + reconhecimento do InsightFace uma unica vez."""
    global _face_app

    if _face_app is None:
        print("Carregando InsightFace (deteccao + reconhecimento)...")

        _face_app = FaceAnalysis(
            name="buffalo_l",
            root=obter_diretorio_modelos(),
            providers=["CPUExecutionProvider"],
            allowed_modules=["detection", "recognition"]
        )

        _face_app.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

        print("Modelo carregado.")

    return _face_app


def analisar_frame(frame):
    """Roda deteccao + embedding no frame."""
    modelo = carregar_modelo()
    rostos = modelo.get(frame)

    return rostos