import tkinter as tk


def criar_tela(container, voltar_callback):
    label = tk.Label(
        container,
        text="Visualizar câmera — em breve",
        font=("Arial", 14),
    )

    label.pack(
        pady=40
    )

    botao_voltar = tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    )

    botao_voltar.pack(
        pady=10
    )