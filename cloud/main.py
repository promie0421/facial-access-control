from fastapi import FastAPI

from cloud.database import inicializar_banco
from cloud.routers.access_logs import router as access_logs_router
from cloud.routers.companies import router as companies_router
from cloud.routers.health import router as health_router
from cloud.routers.terminals import router as terminals_router


app = FastAPI(
    title="Lancaster Access Cloud",
    version="0.1.0",
)

inicializar_banco()

app.include_router(health_router)
app.include_router(companies_router)
app.include_router(terminals_router)
app.include_router(access_logs_router)