from fastapi import FastAPI

from .routers import calculate_tool, spatial_analysis

app = FastAPI()

app.include_router(calculate_tool)
app.include_router(spatial_analysis)


#FOR RestAPI communication use httpx library.