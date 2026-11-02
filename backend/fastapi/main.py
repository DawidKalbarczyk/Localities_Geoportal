from fastapi import FastAPI

from .routers import calculate_tool, spatial_analysis

app = FastAPI()

app.include_router(calculate_tool.router)
app.include_router(spatial_analysis.router)


#FOR RestAPI communication use httpx library.