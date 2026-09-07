import cv2
import time

from modules.camera import (
    abrir_camera,
    camera_esta_aberta,
    ler_frame,
    fechar_camera,
)

from modules.database import init_database

from modules.authentication import (
    carregar_base_embeddings,
    identificar_rosto,
)

from modules.logs import registrar_log

from config.settings import (
    FRAMES_PARA_CONFIRMAR,
    DURACAO_RESULTADO_SEGUNDOS,
    DURACAO_COOLDOWN_SEGUNDOS,
)


init_database()

STATUS_CONFIRMAVEIS = (
    "AUTHORIZED_FACE",
    "UNKNOWN_FACE",
)

print("Carregando base de embeddings...")

base_embeddings = carregar_base_embeddings()

print(
    f"Base carregada com "
    f"{len(base_embeddings)} usuario(s) ativo(s)."
)

camera = abrir_camera()

if not camera_esta_aberta(camera):
    print(
        "ERRO: nao foi possivel abrir a camera."
    )

else:
    print(
        "Camera aberta. Pressione 'q' para encerrar."
    )

    estado = "AVALIANDO"

    ultimo_status = None
    ultimo_user_id = "sem_usuario"

    contador_repeticoes = 0

    momento_confirmacao = None
    momento_cooldown = None

    texto = ""
    cor = (255, 255, 255)

    try:
        while True:
            sucesso, frame = ler_frame(camera)

            if not sucesso:
                print(
                    "ERRO: nao foi possivel ler "
                    "o frame da camera."
                )
                break

            if estado == "AVALIANDO":

                resultado = identificar_rosto(
                    frame,
                    base_embeddings,
                )

                status = resultado["status"]

                if status == "NO_FACE":

                    cv2.putText(
                        frame,
                        "Nenhum rosto detectado",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (200, 200, 200),
                        2,
                    )

                    contador_repeticoes = 0
                    ultimo_status = None
                    ultimo_user_id = "sem_usuario"

                elif status == "MULTIPLE_FACES":

                    cv2.putText(
                        frame,
                        "Mais de um rosto detectado",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

                    contador_repeticoes = 0
                    ultimo_status = None
                    ultimo_user_id = "sem_usuario"

                elif status == "SYSTEM_ERROR":

                    detalhe = resultado.get(
                        "detalhe",
                        ""
                    )

                    cv2.putText(
                        frame,
                        f"Erro do sistema: {detalhe}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2,
                    )

                    contador_repeticoes = 0
                    ultimo_status = None
                    ultimo_user_id = "sem_usuario"

                elif status in STATUS_CONFIRMAVEIS:

                    user_id_atual = resultado.get(
                        "user_id",
                        "sem_usuario",
                    )

                    if (
                        status == ultimo_status
                        and
                        user_id_atual == ultimo_user_id
                    ):
                        contador_repeticoes += 1

                    else:
                        contador_repeticoes = 1
                        ultimo_status = status
                        ultimo_user_id = user_id_atual

                    cv2.putText(
                        frame,
                        "Avaliando...",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (200, 200, 0),
                        2,
                    )

                    if (
                        contador_repeticoes
                        >= FRAMES_PARA_CONFIRMAR
                    ):

                        if status == "AUTHORIZED_FACE":

                            registrar_log(
                                resultado["user_id"],
                                "FACE",
                                "AUTHORIZED",
                                None,
                            )

                            texto = (
                                f"{resultado['name']} "
                                f"(ID {resultado['public_id']}) "
                                f"- AUTORIZADO "
                                f"- sim: "
                                f"{resultado['similarity']:.2f}"
                            )

                            cor = (0, 255, 0)

                        else:

                            registrar_log(
                                None,
                                "FACE",
                                "DENIED",
                                "UNKNOWN_FACE",
                            )

                            texto = (
                                "DESCONHECIDO "
                                f"- sim: "
                                f"{resultado['similarity']:.2f}"
                            )

                            cor = (0, 0, 255)

                        estado = "CONFIRMADO"
                        momento_confirmacao = time.time()

            elif estado == "CONFIRMADO":

                cv2.putText(
                    frame,
                    texto,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    cor,
                    2,
                )

                if (
                    time.time() - momento_confirmacao
                    >= DURACAO_RESULTADO_SEGUNDOS
                ):
                    estado = "COOLDOWN"
                    momento_cooldown = time.time()

            elif estado == "COOLDOWN":

                cv2.putText(
                    frame,
                    "Aguardando...",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (150, 150, 150),
                    2,
                )

                if (
                    time.time() - momento_cooldown
                    >= DURACAO_COOLDOWN_SEGUNDOS
                ):
                    estado = "AVALIANDO"

                    ultimo_status = None
                    ultimo_user_id = "sem_usuario"

                    contador_repeticoes = 0

            cv2.imshow(
                "Teste de reconhecimento "
                "- pressione q para sair",
                frame,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:
        fechar_camera(camera)

        print(
            "Camera liberada. Teste encerrado."
        )