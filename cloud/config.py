import os


CLOUD_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_ENGINE = os.getenv("LANCASTER_DATABASE_ENGINE", "sqlite")

SQLITE_DATABASE_PATH = os.path.join(CLOUD_DIR, "cloud.db")

POSTGRES_HOST = os.getenv("LANCASTER_POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("LANCASTER_POSTGRES_PORT", "5432"))
POSTGRES_DATABASE = os.getenv("LANCASTER_POSTGRES_DATABASE", "lancaster_access")
POSTGRES_USER = os.getenv("LANCASTER_POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("LANCASTER_POSTGRES_PASSWORD", "")