from fastapi import APIRouter

from cloud.schemas import AccessLogSync
from cloud.services.access_logs import processar_access_log


router = APIRouter(
    prefix="/access-logs",
    tags=["Access Logs"],
)


@router.post("/sync")
def sincronizar_access_log(log: AccessLogSync):
    return processar_access_log(log)