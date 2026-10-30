from pydantic import BaseModel

from fastapi import APIRouter

router = APIRouter(prefix="/calculate-tool", tags=["Calculate-Field-Tool"])

class UserExpression(BaseModel):
    expression: str

fake_expression = "x^2 + 2*x + 1"  # Example expression for testing purposes

#Avoiding search params in user url
@router.post("/calculate-field")
async def calculate_field(user_expression: UserExpression):
    return {"result": fake_expression}