from datetime import datetime

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


class AccessLogSync(BaseModel):
    event_id: str
    company_id: str
    terminal_id: str
    user_public_id: str | None = None
    method: str
    result: str
    reason: str | None = None
    event_timestamp: datetime