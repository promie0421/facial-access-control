import tkinter as tk
import cv2
from PIL import Image, ImageTk

from modules.camera import abrir_camera, camera_esta_aberta, ler_frame, fechar_camera
from modules.registration_session import SessaoCadastro


INTERVALO_VIDEO_MS = 30


def criar_tela(container, voltar_callback):
    """
    Tela de cadastro facial.
    Pede o nome e depois captura as amostras faciais pela webcam.
    """

    estado = {
        "camera": None,
        "atualizando": False,
        "after_id": None,
        "sessao": None,
        "nome": None,
        "captura_solicitada": False,
    }

    def limpar_widgets():
        for widget in container.winfo_children():
            widget.destroy()

    def liberar_camera():
        estado["atualizando"] = False

        if estado["after_id"] is not None:
            try:
                container.after_cancel(estado["after_id"])
            except tk.TclError:
                pass

            estado["after_id"] = None

        if estado["camera"] is not None:
            fechar_camera(estado["camera"])
            estado["camera"] = None

    # Etapa 1: pedir o nome

    def mostrar_tela_nome():
        limpar_widgets()

        titulo = tk.Label(
            container,
            text="CADASTRAR PESSOA",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=(0, 20))

        label_nome = tk.Label(
            container,
            text="Nome da pessoa:",
            font=("Arial", 11)
        )
        label_nome.pack()

        entrada_nome = tk.Entry(
            container,
            font=("Arial", 11),
            width=30
        )
        entrada_nome.pack(pady=5)
        entrada_nome.focus()

        label_aviso = tk.Label(
            container,
            text="",
            font=("Arial", 10),
            fg="red"
        )
        label_aviso.pack(pady=5)

        def iniciar_cadastro():
            nome = entrada_nome.get().strip()

            if not nome:
                label_aviso.config(
                    text="Digite um nome antes de continuar."
                )
                return

            camera = abrir_camera()

            if not camera_esta_aberta(camera):
                label_aviso.config(
                    text="Não foi possível abrir a câmera."
                )
                return

            estado["nome"] = nome
            estado["sessao"] = SessaoCadastro()
            estado["camera"] = camera
            estado["atualizando"] = True
            estado["captura_solicitada"] = False

            mostrar_tela_captura()
            atualizar_frame()

        botao_iniciar = tk.Button(
            container,
            text="Iniciar cadastro",
            width=20,
            command=iniciar_cadastro
        )
        botao_iniciar.pack(pady=10)

        botao_voltar = tk.Button(
            container,
            text="Voltar",
            width=20,
            command=voltar_callback
        )
        botao_voltar.pack(pady=5)

    # Etapa 2: captura das amostras

    def mostrar_tela_captura():
        limpar_widgets()

        titulo = tk.Label(
            container,
            text="CADASTRAR PESSOA",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=(0, 10))

        label_video = tk.Label(container)
        label_video.pack()

        label_instrucao = tk.Label(
            container,
            text="",
            font=("Arial", 11, "bold")
        )
        label_instrucao.pack(pady=(8, 0))

        label_progresso = tk.Label(
            container,
            text="",
            font=("Arial", 10)
        )
        label_progresso.pack()

        label_aviso = tk.Label(
            container,
            text="",
            font=("Arial", 10),
            fg="red"
        )
        label_aviso.pack(pady=3)

        botao_capturar = tk.Button(
            container,
            text="Capturar amostra",
            width=20,
            command=solicitar_captura,
            state="disabled"
        )
        botao_capturar.pack(pady=5)

        botao_voltar = tk.Button(
            container,
            text="Voltar",
            width=20,
            command=voltar_callback
        )
        botao_voltar.pack(pady=5)

        estado["label_video"] = label_video
        estado["label_instrucao"] = label_instrucao
        estado["label_progresso"] = label_progresso
        estado["label_aviso"] = label_aviso
        estado["botao_capturar"] = botao_capturar

    def solicitar_captura():
        # A captura será feita usando o próximo frame analisado.
        estado["captura_solicitada"] = True

    def atualizar_frame():
        if not estado["atualizando"]:
            return

        sucesso, frame = ler_frame(estado["camera"])

        if not sucesso:
            estado["label_aviso"].config(
                text="Erro ao ler frame da câmera.",
                fg="red"
            )
            liberar_camera()
            return

        sessao = estado["sessao"]

        try:
            rostos = sessao.avaliar_frame(frame)
        except Exception as erro:
            estado["label_aviso"].config(
                text=f"Erro ao analisar rosto: {erro}",
                fg="red"
            )
            liberar_camera()
            return

        if len(rostos) == 1:
            x1, y1, x2, y2 = rostos[0].bbox.astype(int)

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            estado["botao_capturar"].config(state="normal")

            if not estado["captura_solicitada"]:
                estado["label_aviso"].config(text="")

        elif len(rostos) == 0:
            estado["botao_capturar"].config(state="disabled")

            estado["label_aviso"].config(
                text="Nenhum rosto detectado.",
                fg="red"
            )

        else:
            estado["botao_capturar"].config(state="disabled")

            estado["label_aviso"].config(
                text="Mais de um rosto detectado.",
                fg="red"
            )

        estado["label_instrucao"].config(
            text=sessao.instrucao_atual()
        )

        estado["label_progresso"].config(
            text=f"Amostras: {sessao.progresso_texto()}"
        )

        if estado["captura_solicitada"]:
            estado["captura_solicitada"] = False

            sucesso_captura, mensagem = sessao.tentar_capturar(rostos)

            if sucesso_captura:
                estado["label_aviso"].config(
                    text=mensagem,
                    fg="green"
                )
            else:
                estado["label_aviso"].config(
                    text=mensagem,
                    fg="red"
                )

            if sucesso_captura and sessao.completo():
                estado["botao_capturar"].config(state="disabled")

                finalizar_cadastro()
                return

        # Converte o frame para exibir no Tkinter.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagem = Image.fromarray(frame_rgb)

        # Limita o tamanho do vídeo para os botões continuarem visíveis.
        imagem.thumbnail((440, 330))

        imagem_tk = ImageTk.PhotoImage(image=imagem)

        estado["label_video"].imgtk = imagem_tk
        estado["label_video"].config(image=imagem_tk)

        estado["after_id"] = container.after(
            INTERVALO_VIDEO_MS,
            atualizar_frame
        )

    # Etapa 3: finalização

    def finalizar_cadastro():
        estado["atualizando"] = False

        try:
            user_id, public_id = estado["sessao"].finalizar(
                estado["nome"]
            )

        except Exception as erro:
            liberar_camera()
            mostrar_tela_erro(str(erro))
            return

        liberar_camera()
        mostrar_tela_sucesso(public_id)

    def mostrar_tela_sucesso(public_id):
        limpar_widgets()

        titulo = tk.Label(
            container,
            text="CADASTRO CONCLUÍDO",
            font=("Arial", 18, "bold"),
            fg="green"
        )
        titulo.pack(pady=(0, 20))

        mensagem = tk.Label(
            container,
            text=(
                "Usuário cadastrado com sucesso.\n"
                f"ID: {public_id}"
            ),
            font=("Arial", 12)
        )
        mensagem.pack(pady=10)

        botao_voltar = tk.Button(
            container,
            text="Voltar ao menu",
            width=20,
            command=voltar_callback
        )
        botao_voltar.pack(pady=20)

    def mostrar_tela_erro(mensagem_erro):
        limpar_widgets()

        titulo = tk.Label(
            container,
            text="ERRO NO CADASTRO",
            font=("Arial", 18, "bold"),
            fg="red"
        )
        titulo.pack(pady=(0, 20))

        mensagem = tk.Label(
            container,
            text=(
                "Não foi possível salvar o cadastro:\n"
                f"{mensagem_erro}"
            ),
            font=("Arial", 11),
            wraplength=400
        )
        mensagem.pack(pady=10)

        botao_voltar = tk.Button(
            container,
            text="Voltar ao menu",
            width=20,
            command=voltar_callback
        )
        botao_voltar.pack(pady=20)

    mostrar_tela_nome()

    return liberar_camera