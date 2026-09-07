import cv2
import time

from modules.camera import (
    abrir_camera,
    camera_esta_aberta,
    ler_frame,
    fechar_camera,
)


print("Abrindo a câmera...")

camera = abrir_camera()

if not camera_esta_aberta(camera):
    print("ERRO: não foi possível abrir a câmera.")
    print("Verifique se ela está sendo usada por outro programa.")
else:
    print("Câmera aberta.")
    print("Pressione 'q' na janela do vídeo para encerrar.")

    tempo_do_ultimo_frame = time.time()

    try:
        while True:
            sucesso, frame = ler_frame(camera)

            if not sucesso:
                print("ERRO: não foi possível ler o frame da câmera.")
                break

            agora = time.time()
            tempo_decorrido = agora - tempo_do_ultimo_frame
            tempo_do_ultimo_frame = agora

            fps = 1 / tempo_decorrido if tempo_decorrido > 0 else 0

            texto_fps = f"FPS: {fps:.1f}"

            cv2.putText(
                frame,
                texto_fps,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(
                "Teste de camera - pressione q para sair",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        fechar_camera(camera)
        print("Câmera liberada. Teste encerrado.")