import tkinter as tk

from ui.registration_screen import criar_tela as criar_tela_cadastro
from ui.users_screen import criar_tela as criar_tela_usuarios
from ui.camera_view_screen import criar_tela as criar_tela_camera
from ui.recognition_test_screen import criar_tela as criar_tela_reconhecimento
from ui.logs_screen import criar_tela as criar_tela_logs
from ui.settings_screen import criar_tela as criar_tela_configuracoes


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("Controle de Acesso")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.container = tk.Frame(
            self.root,
            padx=20,
            pady=20,
        )

        self.container.pack(
            fill="both",
            expand=True,
        )

        self.mostrar_menu_principal()

    def iniciar(self):
        self.root.mainloop()

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_tela(self, funcao_da_tela):
        self.limpar_container()

        funcao_da_tela(
            self.container,
            self.mostrar_menu_principal,
        )

    def mostrar_menu_principal(self):
        self.limpar_container()

        titulo = tk.Label(
            self.container,
            text="CONTROLE DE ACESSO",
            font=("Arial", 18, "bold"),
        )

        titulo.pack(
            pady=(0, 20)
        )

        botoes = [
            (
                "Cadastrar pessoa",
                lambda: self.mostrar_tela(
                    criar_tela_cadastro
                ),
            ),
            (
                "Usuários cadastrados",
                lambda: self.mostrar_tela(
                    criar_tela_usuarios
                ),
            ),
            (
                "Visualizar câmera",
                lambda: self.mostrar_tela(
                    criar_tela_camera
                ),
            ),
            (
                "Testar reconhecimento",
                lambda: self.mostrar_tela(
                    criar_tela_reconhecimento
                ),
            ),
            (
                "Logs de acesso",
                lambda: self.mostrar_tela(
                    criar_tela_logs
                ),
            ),
            (
                "Configurações",
                lambda: self.mostrar_tela(
                    criar_tela_configuracoes
                ),
            ),
            (
                "Sair",
                self.root.destroy,
            ),
        ]

        for texto, comando in botoes:
            botao = tk.Button(
                self.container,
                text=texto,
                width=30,
                height=2,
                command=comando,
            )

            botao.pack(
                pady=5
            )