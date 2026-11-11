import math as m

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from ..services.service_calc_tool import ExpressionParser
from ..services.service_translate_errors import CalculationError

router = APIRouter(prefix="/calculate-tool", tags=["Calculate-Field-Tool"])

class UserExpression(BaseModel):
    expression: str
    table: list[dict]
    tableKeys: list[str]

#Avoiding search params in user url
@router.post("/calculate-field")
async def calculate_field(user_expression: UserExpression):
    try:
        CalcExpressionParser= ExpressionParser(user_expression.expression, user_expression.table, user_expression.tableKeys)
        CalcExpressionParser.find_function_call()
        CalcExpressionParser.writeFunctions()
        result = CalcExpressionParser.parse_expression()
        if isinstance(result, float) and not m.isfinite(result):
            raise CalculationError(
                code="ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.ERRORS.NON_FINITE_RESULT",
                params={"result": result},
                message=f"Result is not a finite number: {result}",
            )
        if isinstance(result, complex) and (not m.isfinite(result.real) or not m.isfinite(result.imag)):
            raise CalculationError(
                code="ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.ERRORS.NON_FINITE_COMPLEX_RESULT",
                params={"result": result},
                message=f"Result is not a finite complex number: {result}",
            )

    except CalculationError as exc:
        raise HTTPException(status_code=400, detail={"code": exc.code, "params": exc.params}) from exc
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(result, complex):
        result = {
            "real": result.real,
            "imag": result.imag
        }
    return {"RESULT": result}
