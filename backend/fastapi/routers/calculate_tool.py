from fastapi import APIRouter

router = APIRouter(prefix="/calculate-tool", tags=["Calculate-Field-Tool"])

@router.get("/test-int")
def testInteger():
    return {"message": "Integer test successful!"}