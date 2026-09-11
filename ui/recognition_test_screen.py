import time
import tkinter as tk
import cv2

from PIL import Image, ImageTk

from modules.camera import (
    abrir_camera,
    camera_esta_aberta,
    ler_frame,
    fechar_camera,
)
from modules.authentication import (
    carregar_base_embeddings,
    identificar_rosto,
)
from modules.recognition_session import SessaoReconhecimento
from config.settings import INTERVALO_RECONHECIMENTO_MS


INTERVALO_VIDEO_MS = 30

TEXTOS_E_CORES = {
    "SEM_ROSTO": (
        "Aguardando rosto...",
        "gray20",
    ),
    "MULTIPLOS_ROSTOS": (
        "Mais de um rosto detectado",
        "red",
    ),
    "AVALIANDO": (
        "Avaliando...",
        "goldenrod",
    ),
    "AUTORIZADO": (
        "ACESSO AUTORIZADO",
        "green",
    ),
    "NEGADO": (
        "ACESSO NEGADO",
        "red",
    ),
    "ERRO": (
        "Erro do sistema",
        "red",
    ),
}


def criar_tela(container, voltar_callback):
    """Tela de teste de reconhecimento facial."""

    estado = {
        "camera": None,
        "atualizando": False,
        "after_id": None,
        "base_embeddings": None,
        "sessao": None,
        "momento_ultima_avaliacao": 0.0,
    }

    titulo = tk.Label(
        container,
        text="TESTAR RECONHECIMENTO",
        font=("Arial", 18, "bold"),
    )
    titulo.pack(pady=(0, 10))

    label_video = tk.Label(container)
    label_video.pack()

    label_status = tk.Label(
        container,
        text="Status: Carregando...",
        font=("Arial", 11, "bold"),
    )
    label_status.pack(pady=(10, 0))

    label_nome = tk.Label(
        container,
        text="Nome: -",
        font=("Arial", 11),
    )
    label_nome.pack()

    label_similaridade = tk.Label(
        container,
        text="Similaridade: -",
        font=("Arial", 11),
    )
    label_similaridade.pack()

    def parar_camera():
        estado["atualizando"] = False

        if estado["after_id"] is not None:
            label_video.after_cancel(
                estado["after_id"]
            )
            estado["after_id"] = None

        if estado["camera"] is not None:
            fechar_camera(
                estado["camera"]
            )
            estado["camera"] = None

        label_status.config(
            text="Status: Câmera desligada"
        )
        label_video.config(image="")

    def atualizar_labels_pela_sessao():
        saida = estado["sessao"].obter_saida()

        tipo = saida.get(
            "tipo",
            "SEM_ROSTO",
        )

        texto_status, cor = TEXTOS_E_CORES.get(
            tipo,
            (
                "Aguardando rosto...",
                "gray20",
            ),
        )

        if tipo == "AUTORIZADO":
            label_status.config(
                text=f"Status: {texto_status}",
                fg=cor,
            )

            label_nome.config(
                text=(
                    f"Nome: {saida['nome']} "
                    f"(ID {saida['public_id']})"
                )
            )

            label_similaridade.config(
                text=(
                    "Similaridade: "
                    f"{saida['similaridade']:.2f}"
                )
            )

        elif tipo == "NEGADO":
            label_status.config(
                text=f"Status: {texto_status}",
                fg=cor,
            )

            label_nome.config(
                text="Nome: Desconhecido"
            )

            label_similaridade.config(
                text=(
                    "Similaridade: "
                    f"{saida['similaridade']:.2f}"
                )
            )

        elif tipo == "ERRO":
            label_status.config(
                text=(
                    f"Status: {texto_status} - "
                    f"{saida.get('detalhe', '')}"
                ),
                fg=cor,
            )

            label_nome.config(
                text="Nome: -"
            )

            label_similaridade.config(
                text="Similaridade: -"
            )

        else:
            label_status.config(
                text=f"Status: {texto_status}",
                fg=cor,
            )

            label_nome.config(
                text="Nome: -"
            )

            label_similaridade.config(
                text="Similaridade: -"
            )

    def atualizar_frame():
        if not estado["atualizando"]:
            return

        sucesso, frame = ler_frame(
            estado["camera"]
        )

        if not sucesso:
            label_status.config(
                text="Status: erro ao ler frame",
                fg="red",
            )
            parar_camera()
            return

        estado["sessao"].atualizar_estado()

        agora = time.time()

        tempo_desde_ultima_avaliacao = (
            agora
            - estado["momento_ultima_avaliacao"]
        ) * 1000

        if (
            estado["sessao"].deve_avaliar()
            and tempo_desde_ultima_avaliacao
            >= INTERVALO_RECONHECIMENTO_MS
        ):
            resultado = identificar_rosto(
                frame,
                estado["base_embeddings"],
            )

            estado["sessao"].processar_resultado(
                resultado
            )

            estado["momento_ultima_avaliacao"] = agora

        atualizar_labels_pela_sessao()

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        imagem = Image.fromarray(
            frame_rgb
        )

        # redimensiona a imagem para caber na interface
        imagem.thumbnail((440, 330))

        imagem_tk = ImageTk.PhotoImage(
            image=imagem
        )

        label_video.imgtk = imagem_tk
        label_video.config(
            image=imagem_tk
        )

        estado["after_id"] = label_video.after(
            INTERVALO_VIDEO_MS,
            atualizar_frame,
        )

    def iniciar_camera():
        if estado["camera"] is not None:
            return

        label_status.config(
            text=(
                "Status: Carregando base "
                "de embeddings..."
            ),
            fg="gray20",
        )

        container.update_idletasks()

        try:
            estado["base_embeddings"] = (
                carregar_base_embeddings()
            )

        except Exception as erro:
            label_status.config(
                text=(
                    "Status: Erro ao acessar "
                    f"o banco de dados ({erro})"
                ),
                fg="red",
            )
            return

        estado["sessao"] = (
            SessaoReconhecimento()
        )

        camera = abrir_camera()

        if not camera_esta_aberta(camera):
            label_status.config(
                text=(
                    "Status: Não foi possível "
                    "abrir a câmera"
                ),
                fg="red",
            )
            return

        estado["camera"] = camera
        estado["atualizando"] = True

        label_status.config(
            text="Status: Aguardando rosto...",
            fg="gray20",
        )

        atualizar_frame()

    botao_encerrar = tk.Button(
        container,
        text="Encerrar câmera",
        width=20,
        command=parar_camera,
    )
    botao_encerrar.pack(
        pady=(15, 5)
    )

    botao_voltar = tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    )
    botao_voltar.pack(pady=5)

    iniciar_camera()

    return parar_camera