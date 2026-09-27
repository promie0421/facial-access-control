import sqlite3

import psycopg
from fastapi import HTTPException

from cloud.database import (
    buscar_empresa,
    cadastrar_empresa,
    listar_empresas,
)
from cloud.schemas import CompanyCreate


def obter_empresas():
    """Retorna as empresas cadastradas na Lancaster Cloud."""
    empresas = listar_empresas()

    return [
        {
            "company_id": empresa[0],
            "company_name": empresa[1],
            "status": empresa[2],
            "created_at": empresa[3],
        }
        for empresa in empresas
    ]


def obter_empresa(company_id):
    """Retorna uma empresa pelo company_id."""
    empresa = buscar_empresa(company_id)

    if empresa is None:
        raise HTTPException(
            status_code=404,
            detail="empresa nao encontrada",
        )

    return {
        "company_id": empresa[0],
        "company_name": empresa[1],
        "status": empresa[2],
        "created_at": empresa[3],
    }


def criar_empresa(company: CompanyCreate):
    """Cadastra uma empresa na Lancaster Cloud."""
    try:
        cadastrar_empresa(
            company_id=company.company_id,
            company_name=company.company_name,
        )
    except (sqlite3.IntegrityError, psycopg.IntegrityError):
        raise HTTPException(
            status_code=409,
            detail="company_id ja cadastrado",
        )

    return {
        "status": "created",
        "company_id": company.company_id,
        "company_name": company.company_name,
    }