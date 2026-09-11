import tkinter as tk

from ui.registration_screen import criar_tela as criar_tela_cadastro
from ui.users_screen import criar_tela as criar_tela_usuarios
from ui.camera_view_screen import criar_tela as criar_tela_camera
from ui.recognition_test_screen import criar_tela as criar_tela_reconhecimento
from ui.pin_auth_screen import criar_tela as criar_tela_pin
from ui.logs_screen import criar_tela as criar_tela_logs
from ui.settings_screen import criar_tela as criar_tela_configuracoes


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Controle de Acesso")
        self.root.geometry("600x650")
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

        # guarda a funcao de limpeza da tela atual
        self.cleanup_tela_atual = None

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.encerrar_aplicacao,
        )

        self.mostrar_menu_principal()

    def iniciar(self):
        self.root.mainloop()

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def executar_cleanup_se_existir(self):
        if self.cleanup_tela_atual is not None:
            self.cleanup_tela_atual()
            self.cleanup_tela_atual = None

    def mostrar_tela(self, funcao_da_tela):
        self.executar_cleanup_se_existir()
        self.limpar_container()

        cleanup = funcao_da_tela(
            self.container,
            self.mostrar_menu_principal,
        )

        self.cleanup_tela_atual = cleanup

    def mostrar_menu_principal(self):
        self.executar_cleanup_se_existir()
        self.limpar_container()

        titulo = tk.Label(
            self.container,
            text="CONTROLE DE ACESSO",
            font=("Arial", 18, "bold"),
        )
        titulo.pack(pady=(0, 20))

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
                "Autenticar com PIN",
                lambda: self.mostrar_tela(
                    criar_tela_pin
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
                self.encerrar_aplicacao,
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
            botao.pack(pady=5)

    def encerrar_aplicacao(self):
        self.executar_cleanup_se_existir()
        self.root.destroy()