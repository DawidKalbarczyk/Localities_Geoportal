def fields_and_values_match(func, table: list[dict], tableKeys: list[str]):
    queried_column = []
    if func not in tableKeys:
        raise ValueError(f"Column '{func}' is not known.")
    for record in table:
        queried_column.append(record.get(func))

    def _get_column():
        return queried_column
    return _get_column
    