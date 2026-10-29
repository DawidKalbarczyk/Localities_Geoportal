import os

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
FASTAPI_PORT = (os.environ["FASTAPI_PORT"])
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

FASTAPI_BASE_URL = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}"

FASTAPI_CALCULATE_TOOL_URL = f"{FASTAPI_BASE_URL}/calculate-tool"
FASTAPI_SPATIAL_ANALYSIS_URL = f"{FASTAPI_BASE_URL}/spatial-analysis"