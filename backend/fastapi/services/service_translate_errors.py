class CalculationError(ValueError):
    def __init__(self, code: str, params: dict[str, str | int | float], message: str):
        super().__init__(message)
        self.code = code
        self.params = params


class CalculationTypeError(CalculationError, TypeError):
    pass
