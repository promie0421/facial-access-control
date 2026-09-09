import tkinter as tk

import cv2
from PIL import Image, ImageTk

from modules.camera import (
    abrir_camera,
    camera_esta_aberta,
    ler_frame,
    fechar_camera,
)


INTERVALO_ATUALIZACAO_MS = 30
LARGURA_VIDEO = 440
ALTURA_VIDEO = 330


def criar_tela(container, voltar_callback):
    """Mostra a webcam dentro da interface."""

    estado = {
        "camera": None,
        "atualizando": False,
        "after_id": None,
    }

    titulo = tk.Label(
        container,
        text="VISUALIZAR CÂMERA",
        font=("Arial", 18, "bold"),
    )
    titulo.pack(pady=(0, 10))

    label_video = tk.Label(container)
    label_video.pack()

    label_status = tk.Label(
        container,
        text="Status: Câmera desligada",
        font=("Arial", 11),
    )
    label_status.pack(pady=10)

    def parar_camera():
        estado["atualizando"] = False

        if estado["after_id"] is not None:
            try:
                label_video.after_cancel(
                    estado["after_id"]
                )
            except tk.TclError:
                pass

            estado["after_id"] = None

        if estado["camera"] is not None:
            fechar_camera(
                estado["camera"]
            )
            estado["camera"] = None

        label_status.config(
            text="Status: Câmera desligada"
        )

        label_video.config(
            image=""
        )

        label_video.imgtk = None

    def atualizar_frame():
        if not estado["atualizando"]:
            return

        sucesso, frame = ler_frame(
            estado["camera"]
        )

        if not sucesso:
            label_status.config(
                text="Status: erro ao ler frame"
            )
            parar_camera()
            return

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        imagem = Image.fromarray(
            frame_rgb
        )

        imagem.thumbnail(
            (LARGURA_VIDEO, ALTURA_VIDEO)
        )

        imagem_tk = ImageTk.PhotoImage(
            image=imagem
        )

        label_video.imgtk = imagem_tk

        label_video.config(
            image=imagem_tk
        )

        estado["after_id"] = label_video.after(
            INTERVALO_ATUALIZACAO_MS,
            atualizar_frame,
        )

    def iniciar_camera():
        if estado["camera"] is not None:
            return

        camera = abrir_camera()

        if not camera_esta_aberta(camera):
            fechar_camera(camera)

            label_status.config(
                text="Status: Não foi possível abrir a câmera"
            )
            return

        estado["camera"] = camera
        estado["atualizando"] = True

        label_status.config(
            text="Status: Câmera online"
        )

        atualizar_frame()

    botao_encerrar = tk.Button(
        container,
        text="Encerrar câmera",
        width=20,
        command=parar_camera,
    )
    botao_encerrar.pack(pady=5)

    botao_voltar = tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    )
    botao_voltar.pack(pady=5)

    iniciar_camera()

    return parar_camera