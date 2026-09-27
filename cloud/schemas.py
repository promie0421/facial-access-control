from pydantic import BaseModel


class TerminalRegistro(BaseModel):
    product: str
    version: str
    company_id: str
    company_name: str
    terminal_id: str
    terminal_name: str


class CompanyCreate(BaseModel):
    company_id: str
    company_name: str