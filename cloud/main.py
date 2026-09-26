from fastapi import FastAPI

app = FastAPI(
    title="Lancaster Access Cloud",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "online",
        "service": "Lancaster Access Cloud",
    }