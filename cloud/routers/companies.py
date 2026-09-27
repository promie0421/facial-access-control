from fastapi import APIRouter

from cloud.schemas import CompanyCreate
from cloud.services.companies import (
    criar_empresa,
    obter_empresa,
    obter_empresas,
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("")
def listar_empresas_endpoint():
    return obter_empresas()


@router.get("/{company_id}")
def buscar_empresa_endpoint(company_id: str):
    return obter_empresa(company_id)


@router.post("")
def criar_empresa_endpoint(company: CompanyCreate):
    return criar_empresa(company)
