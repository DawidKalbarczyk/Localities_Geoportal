from fastapi import APIRouter

router = APIRouter(prefix="/spatial-analysis", tags=["Spatial-Analysis-Operations"])

@router.get("/test-spatial")
def testSpatial():
    return {"message": "Spatial analysis test successful!"}