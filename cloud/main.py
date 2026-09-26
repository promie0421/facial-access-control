from fastapi import FastAPI
from pydantic import BaseModel

from cloud.database import inicializar_banco, registrar_terminal


app = FastAPI(
    title="Lancaster Access Cloud",
    version="0.1.0",
)

inicializar_banco()


class TerminalRegistro(BaseModel):
    product: str
    version: str
    company_id: str
    company_name: str
    terminal_id: str
    terminal_name: str


@app.get("/health")
def health():
    return {
        "status": "online",
        "service": "Lancaster Access Cloud",
    }


@app.post("/terminals/register")
def registrar_terminal_endpoint(terminal: TerminalRegistro):
    registrar_terminal(
        company_id=terminal.company_id,
        company_name=terminal.company_name,
        terminal_id=terminal.terminal_id,
        terminal_name=terminal.terminal_name,
        product=terminal.product,
        version=terminal.version,
    )

    return {
        "status": "registered",
        "company_id": terminal.company_id,
        "terminal_id": terminal.terminal_id,
        "terminal_name": terminal.terminal_name,
    }