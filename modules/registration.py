import cv2

from modules.camera import (
    abrir_camera,
    camera_esta_aberta,
    ler_frame,
    fechar_camera,
)

from modules.face_engine import analisar_frame

from modules.face_recognition import (
    obter_embedding,
    calcular_similaridade,
    embedding_para_bytes,
)

from modules.database import criar_usuario_com_embeddings


QUANTIDADE_DE_AMOSTRAS = 5

SIMILARIDADE_MAXIMA_ENTRE_AMOSTRAS = 0.98


INSTRUCOES_POR_AMOSTRA = [
    "Olhe para frente",
    "Vire levemente para a esquerda",
    "Vire levemente para a direita",
    "Olhe para frente novamente",
    "Incline a cabeca levemente para baixo ou para cima",
]


def cadastrar_pessoa(nome):
    """Captura as amostras faciais e cadastra a pessoa."""

    camera = abrir_camera()

    if not camera_esta_aberta(camera):
        return False, "Nao foi possivel abrir a camera.", None

    embeddings_capturados = []

    try:
        indice_amostra = 0

        while indice_amostra < QUANTIDADE_DE_AMOSTRAS:
            instrucao = INSTRUCOES_POR_AMOSTRA[indice_amostra]

            sucesso, frame = ler_frame(camera)

            if not sucesso:
                return (
                    False,
                    "Erro ao ler frame da camera. Cadastro cancelado.",
                    None,
                )

            rostos = analisar_frame(frame)

            if len(rostos) == 1:
                x1, y1, x2, y2 = rostos[0].bbox.astype(int)

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

            texto = (
                f"{instrucao} - ESPACO para capturar "
                f"({indice_amostra + 1}/{QUANTIDADE_DE_AMOSTRAS})"
            )

            cv2.putText(
                frame,
                texto,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            if len(rostos) == 0:
                cv2.putText(
                    frame,
                    "Nenhum rosto detectado",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

            elif len(rostos) > 1:
                cv2.putText(
                    frame,
                    "Mais de um rosto detectado",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow(
                "Cadastro facial - ESC para cancelar",
                frame,
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:
                return (
                    False,
                    "Cadastro cancelado pelo usuario.",
                    None,
                )

            if tecla == 32:
                if len(rostos) != 1:
                    print(
                        "Captura ignorada: precisa haver "
                        "exatamente 1 rosto na imagem."
                    )
                    continue

                embedding_novo = obter_embedding(rostos[0])

                muito_parecido = False

                for embedding_existente in embeddings_capturados:
                    similaridade = calcular_similaridade(
                        embedding_novo,
                        embedding_existente,
                    )

                    if (
                        similaridade
                        > SIMILARIDADE_MAXIMA_ENTRE_AMOSTRAS
                    ):
                        muito_parecido = True
                        break

                if muito_parecido:
                    print(
                        "Amostra muito parecida com uma anterior. "
                        "Mude a pose e tente de novo."
                    )
                    continue

                embeddings_capturados.append(
                    embedding_novo
                )

                print(
                    f"Amostra {indice_amostra + 1} capturada."
                )

                indice_amostra += 1

    finally:
        fechar_camera(camera)

    if len(embeddings_capturados) < QUANTIDADE_DE_AMOSTRAS:
        return (
            False,
            "Cadastro incompleto. Nada foi salvo.",
            None,
        )

    embeddings_bytes = [
        embedding_para_bytes(embedding)
        for embedding in embeddings_capturados
    ]

    try:
        user_id, public_id = criar_usuario_com_embeddings(
            nome,
            None,
            embeddings_bytes,
        )

    except Exception as erro:
        return (
            False,
            f"Erro ao salvar no banco, nada foi persistido: {erro}",
            None,
        )

    return (
        True,
        "Usuario cadastrado com sucesso.",
        public_id,
    )