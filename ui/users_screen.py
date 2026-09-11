import tkinter as tk
from tkinter import messagebox, simpledialog

from modules.database import (
    listar_usuarios,
    ativar_usuario,
    desativar_usuario,
    remover_usuario,
)
from modules.authentication import definir_pin_usuario


def criar_tela(container, voltar_callback):
    """Tela de gerenciamento de usuarios cadastrados."""
    estado = {
        "usuarios": [],
    }

    titulo = tk.Label(
        container,
        text="USUÁRIOS CADASTRADOS",
        font=("Arial", 18, "bold"),
    )
    titulo.pack(pady=(0, 10))

    lista = tk.Listbox(
        container,
        width=60,
        height=15,
        font=("Courier", 10),
    )
    lista.pack(pady=5)

    label_aviso = tk.Label(
        container,
        text="",
        font=("Arial", 10),
    )
    label_aviso.pack(pady=5)

    def carregar_usuarios():
        lista.delete(0, tk.END)

        try:
            estado["usuarios"] = listar_usuarios()

        except Exception as erro:
            label_aviso.config(
                text=f"Erro ao consultar usuarios: {erro}",
                fg="red",
            )
            return

        label_aviso.config(text="")

        for usuario in estado["usuarios"]:
            status = (
                "Ativo"
                if usuario["active"] == 1
                else "Inativo"
            )

            linha = (
                f"{usuario['public_id']}  "
                f"{usuario['name']:<25} "
                f"{status}"
            )

            lista.insert(tk.END, linha)

    def obter_usuario_selecionado():
        selecao = lista.curselection()

        if not selecao:
            label_aviso.config(
                text="Selecione um usuario na lista primeiro.",
                fg="red",
            )
            return None

        indice = selecao[0]
        return estado["usuarios"][indice]

    def alternar_status():
        usuario = obter_usuario_selecionado()

        if usuario is None:
            return

        try:
            if usuario["active"] == 1:
                desativar_usuario(usuario["id"])
            else:
                ativar_usuario(usuario["id"])

        except Exception as erro:
            label_aviso.config(
                text=f"Erro ao atualizar status: {erro}",
                fg="red",
            )
            return

        carregar_usuarios()

    def definir_pin():
        usuario = obter_usuario_selecionado()

        if usuario is None:
            return

        pin = simpledialog.askstring(
            "Definir PIN",
            f"Digite um PIN de 6 dígitos para {usuario['name']}:",
            show="*",
        )

        if pin is None:
            return

        try:
            definir_pin_usuario(
                usuario["id"],
                pin,
            )

            label_aviso.config(
                text="PIN atualizado com sucesso.",
                fg="green",
            )

        except ValueError as erro:
            label_aviso.config(
                text=str(erro),
                fg="red",
            )

        except Exception as erro:
            label_aviso.config(
                text=f"Erro ao salvar PIN: {erro}",
                fg="red",
            )

    def excluir():
        usuario = obter_usuario_selecionado()

        if usuario is None:
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            (
                f"Excluir permanentemente {usuario['name']} "
                f"(ID {usuario['public_id']})?\n"
                "Os embeddings faciais dele também serão removidos."
            ),
        )

        if not confirmar:
            return

        try:
            remover_usuario(usuario["id"])

        except Exception as erro:
            label_aviso.config(
                text=f"Erro ao excluir usuario: {erro}",
                fg="red",
            )
            return

        label_aviso.config(
            text="Usuário excluído.",
            fg="green",
        )

        carregar_usuarios()

    frame_botoes = tk.Frame(container)
    frame_botoes.pack(pady=10)

    tk.Button(
        frame_botoes,
        text="Atualizar lista",
        width=16,
        command=carregar_usuarios,
    ).grid(
        row=0,
        column=0,
        padx=3,
        pady=3,
    )

    tk.Button(
        frame_botoes,
        text="Ativar/Desativar",
        width=16,
        command=alternar_status,
    ).grid(
        row=0,
        column=1,
        padx=3,
        pady=3,
    )

    tk.Button(
        frame_botoes,
        text="Definir PIN",
        width=16,
        command=definir_pin,
    ).grid(
        row=1,
        column=0,
        padx=3,
        pady=3,
    )

    tk.Button(
        frame_botoes,
        text="Excluir",
        width=16,
        command=excluir,
    ).grid(
        row=1,
        column=1,
        padx=3,
        pady=3,
    )

    tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    ).pack(pady=10)

    carregar_usuarios()