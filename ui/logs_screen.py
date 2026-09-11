import tkinter as tk

from modules.logs import listar_logs


def criar_tela(container, voltar_callback):
    """Tela de consulta dos logs de acesso."""
    titulo = tk.Label(
        container,
        text="LOGS DE ACESSO",
        font=("Arial", 18, "bold"),
    )
    titulo.pack(pady=(0, 10))

    frame_lista = tk.Frame(container)
    frame_lista.pack(pady=5)

    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")

    lista = tk.Listbox(
        frame_lista,
        width=70,
        height=18,
        font=("Courier", 9),
        yscrollcommand=scrollbar.set,
    )
    lista.pack(side="left")

    scrollbar.config(command=lista.yview)

    label_aviso = tk.Label(
        container,
        text="",
        font=("Arial", 10),
        fg="red",
    )
    label_aviso.pack(pady=5)

    def carregar_logs():
        lista.delete(0, tk.END)

        try:
            logs = listar_logs()

        except Exception as erro:
            label_aviso.config(
                text=f"Erro ao consultar logs: {erro}"
            )
            return

        label_aviso.config(text="")

        if len(logs) == 0:
            lista.insert(
                tk.END,
                "Nenhum registro encontrado.",
            )
            return

        for log in logs:
            if log["public_id"]:
                identificacao = (
                    f"{log['name']} "
                    f"({log['public_id']})"
                )
            else:
                identificacao = "Desconhecido"

            motivo = (
                f" - {log['reason']}"
                if log["reason"]
                else ""
            )

            linha = (
                f"{log['timestamp']}  "
                f"{log['method']:<5} "
                f"{log['result']:<10} "
                f"{identificacao}"
                f"{motivo}"
            )

            lista.insert(tk.END, linha)

    tk.Button(
        container,
        text="Atualizar",
        width=20,
        command=carregar_logs,
    ).pack(pady=5)

    tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    ).pack(pady=5)

    carregar_logs()