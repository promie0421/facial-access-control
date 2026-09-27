from fastapi import APIRouter

from cloud.schemas import TerminalRegistro
from cloud.services.terminals import processar_registro_terminal


router = APIRouter(
    prefix="/terminals",
    tags=["Terminals"],
)


@router.post("/register")
def registrar_terminal_endpoint(terminal: TerminalRegistro):
    return processar_registro_terminal(terminal)