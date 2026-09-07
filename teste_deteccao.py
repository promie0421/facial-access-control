import cv2

from modules.camera import (
    abrir_camera,
    camera_esta_aberta,
    ler_frame,
    fechar_camera,
)

from modules.face_engine import analisar_frame
from modules.face_detection import contar_rostos, obter_bounding_boxes


print("Abrindo a câmera...")
camera = abrir_camera()

if not camera_esta_aberta(camera):
    print("ERRO: não foi possível abrir a câmera.")
else:
    print("Câmera aberta.")
    print("Pressione 'q' na janela para encerrar.")

    try:
        while True:
            sucesso, frame = ler_frame(camera)

            if not sucesso:
                print("ERRO: não foi possível ler o frame.")
                break

            rostos = analisar_frame(frame)

            quantidade = contar_rostos(rostos)
            boxes = obter_bounding_boxes(rostos)

            for x1, y1, x2, y2 in boxes:
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

            if quantidade == 0:
                status = "Nenhum rosto detectado"
            elif quantidade == 1:
                status = "1 rosto detectado"
            else:
                status = f"{quantidade} rostos detectados"

            cv2.putText(
                frame,
                status,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(
                "Teste de deteccao - pressione q para sair",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        fechar_camera(camera)
        print("Câmera liberada. Teste encerrado.")