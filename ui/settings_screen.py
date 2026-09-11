import tkinter as tk

from config.settings import (
    RECOGNITION_THRESHOLD,
    FRAMES_PARA_CONFIRMAR,
    DURACAO_RESULTADO_SEGUNDOS,
    DURACAO_COOLDOWN_SEGUNDOS,
    INTERVALO_RECONHECIMENTO_MS,
    PIN_TAMANHO,
    PIN_MAX_TENTATIVAS,
    PIN_BLOQUEIO_SEGUNDOS,
    LOGS_LIMITE_EXIBICAO,
)


def criar_tela(container, voltar_callback):
    """Tela de configuracoes atuais do sistema."""
    titulo = tk.Label(
        container,
        text="CONFIGURAÇÕES",
        font=("Arial", 18, "bold"),
    )
    titulo.pack(pady=(0, 20))

    configuracoes = [
        (
            "Threshold de reconhecimento facial",
            RECOGNITION_THRESHOLD,
        ),
        (
            "Frames para confirmar reconhecimento",
            FRAMES_PARA_CONFIRMAR,
        ),
        (
            "Duração do resultado exibido (segundos)",
            DURACAO_RESULTADO_SEGUNDOS,
        ),
        (
            "Duração do cooldown (segundos)",
            DURACAO_COOLDOWN_SEGUNDOS,
        ),
        (
            "Intervalo entre análises de reconhecimento (ms)",
            INTERVALO_RECONHECIMENTO_MS,
        ),
        (
            "Tamanho do PIN",
            PIN_TAMANHO,
        ),
        (
            "Tentativas máximas de PIN",
            PIN_MAX_TENTATIVAS,
        ),
        (
            "Bloqueio de PIN (segundos)",
            PIN_BLOQUEIO_SEGUNDOS,
        ),
        (
            "Logs exibidos por consulta",
            LOGS_LIMITE_EXIBICAO,
        ),
    ]

    for nome, valor in configuracoes:
        linha = tk.Frame(container)
        linha.pack(
            fill="x",
            padx=20,
            pady=3,
        )

        tk.Label(
            linha,
            text=nome,
            font=("Arial", 10),
            anchor="w",
        ).pack(side="left")

        tk.Label(
            linha,
            text=str(valor),
            font=("Arial", 10, "bold"),
            anchor="e",
        ).pack(side="right")

    aviso = tk.Label(
        container,
        text=(
            "Estes valores são provisórios e ainda serão calibrados\n"
            "com testes reais (Etapa 16)."
        ),
        font=("Arial", 9),
        fg="gray30",
    )
    aviso.pack(pady=15)

    tk.Button(
        container,
        text="Voltar",
        width=20,
        command=voltar_callback,
    ).pack(pady=10)