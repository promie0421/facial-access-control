import tkinter as tk

from modules.authentication import autenticar_por_pin
from config.settings import PIN_TAMANHO


def criar_tela(container, voltar_callback):
    """Tela de autenticacao por ID publico e PIN."""

    titulo = tk.Label(
        container,
        text="AUTENTICAR COM PIN",
        font=("Arial", 18, "bold"),
    )
    titulo.pack(pady=(0, 20))

    tk.Label(
        container,
        text="ID:",
        font=("Arial", 11),
    ).pack()

    entrada_id = tk.Entry(
        container,
        font=("Arial", 11),
        width=15,
        justify="center",
    )
    entrada_id.pack(pady=5)

    tk.Label(
        container,
        text="PIN:",
        font=("Arial", 11),
    ).pack()

    entrada_pin = tk.Entry(
        container,
        font=("Arial", 11),
        width=15,
        justify="center",
        show="*",
    )
    entrada_pin.pack(pady=5)

    label_status = tk.Label(
        container,
        text="",
        font=("Arial", 12, "bold"),
    )
    label_status.pack(pady=15)

    def autenticar():
        public_id = entrada_id.get().strip()
        pin = entrada_pin.get().strip()

        entrada_pin.delete(0, tk.END)

        if not public_id or not pin:
            label_status.config(
                text="Informe o ID e o PIN.",
                fg="red",
            )
            return

        if (
            len(pin) != PIN_TAMANHO
            or not pin.isdigit()
        ):
            label_status.config(
                text=(
                    f"O PIN deve ter "
                    f"{PIN_TAMANHO} dígitos numéricos."
                ),
                fg="red",
            )
            return

        try:
            resultado = autenticar_por_pin(
                public_id,
                pin,
            )

        except Exception as erro:
            label_status.config(
                text=f"Erro no sistema: {erro}",
                fg="red",
            )
            return

        status = resultado["status"]

        if status == "AUTHORIZED_PIN":
            label_status.config(
                text=(
                    f"ACESSO AUTORIZADO - "
                    f"{resultado['name']} "
                    f"(ID {resultado['public_id']})"
                ),
                fg="green",
            )

        elif status == "LOCKOUT":
            label_status.config(
                text=(
                    "Muitas tentativas inválidas. "
                    "Aguarde antes de tentar novamente."
                ),
                fg="red",
            )

        elif status == "SYSTEM_ERROR":
            label_status.config(
                text=(
                    "Erro no sistema: "
                    f"{resultado.get('detalhe', '')}"
                ),
                fg="red",
            )

        else:
            label_status.config(
                text="ID ou PIN inválido.",
                fg="red",
            )

    tk.Button(
        container,
        text="Autenticar",
        width=20,
        command=autenticar,
    ).pack(pady=10)

    tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    ).pack(pady=5)