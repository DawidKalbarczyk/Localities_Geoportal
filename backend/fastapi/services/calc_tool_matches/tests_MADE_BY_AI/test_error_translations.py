import ast
import json
import re
from pathlib import Path

import pytest
from services.calc_tool_matches.date_and_time import date_and_time_match
from services.calc_tool_matches.dictionary import dictionary_match
from services.calc_tool_matches.fields_and_values import fields_and_values_match
from services.calc_tool_matches.math import math_match
from services.calc_tool_matches.string import string_match
from services.service_calc_tool import ExpressionParser
from services.service_translate_errors import CalculationError

PREFIX = "ATTRIBUTE-TOOLBAR.CALCULATE-FIELD.ERRORS."
ROOT = Path(__file__).resolve().parents[5]


@pytest.mark.parametrize(
    "module", ["date_and_time", "string", "math", "fields_and_values", "dictionary"]
)
def test_all_explicit_errors_have_polish_translations_and_matching_parameters(module):
    source = Path(__file__).resolve().parents[1] / f"{module}.py"
    translations = json.loads((ROOT / "frontend/public/i18n/pl.json").read_text())
    errors = translations["ATTRIBUTE-TOOLBAR"]["CALCULATE-FIELD"]["ERRORS"]
    checked = 0
    for node in ast.walk(ast.parse(source.read_text())):
        if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
            continue
        assert isinstance(node.exc.func, ast.Name)
        assert node.exc.func.id in ("CalculationError", "CalculationTypeError")
        arguments = {argument.arg: argument.value for argument in node.exc.keywords}
        code = ast.literal_eval(arguments["code"])
        assert code.startswith(PREFIX)
        translation = errors[code.removeprefix(PREFIX)]
        placeholders = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", translation))
        params = {ast.literal_eval(key) for key in arguments["params"].keys}
        assert placeholders == params, (source.name, node.lineno, code)
        checked += 1
    assert checked > 0


@pytest.mark.parametrize(
    "matcher, function, args, code, params",
    [
        (
            date_and_time_match,
            "age",
            ("2026-01-01, 2026-01-02",),
            "INVALID_DATE_EARLIER",
            {"start": "2026-01-02", "end": "2026-01-01"},
        ),
        (
            date_and_time_match,
            "make_date",
            ("bad-date",),
            "MAKE_DATE_FORMAT",
            {"date": "bad-date"},
        ),
        (
            date_and_time_match,
            "to_datetime",
            ("2026-10-30, unknown",),
            "TO_DATETIME_FORMAT",
            {"format": "unknown"},
        ),
        (
            date_and_time_match,
            "format_date",
            ("2026-10-30, wrong.format.tokens",),
            "PROPER_FORMAT",
            {"format": "wrong.format.tokens"},
        ),
        (
            date_and_time_match,
            "to_interval",
            ("nan days",),
            "INTERVAL_NON_NEGATIVE_VALUE",
            {"value": "nan"},
        ),
        (string_match, "ascii", (), "STRING_SINGLE_ARGUMENT", {"function": "ascii"}),
        (string_match, "ascii", ("🙂",), "INVALID_ASCII_SYMBOL", {"symbol": "🙂"}),
        (math_match, "pi", ("1",), "PI_ARGUMENTS", {}),
        (
            math_match,
            "scale_linear",
            ("5, 10, 0, 0, 100",),
            "SCALE_DOMAIN_RANGE",
            {"min": "10.0", "max": "0.0"},
        ),
        (
            dictionary_match,
            "map_get",
            ({"present": 1}, "missing"),
            "MAP_KEY_NOT_FOUND",
            {"function": "map_get", "key": "missing"},
        ),
        (
            dictionary_match,
            "map_get",
            ("not-a-dictionary", "key"),
            "MAP_FIRST_ARGUMENT_TYPE",
            {"function": "map_get"},
        ),
    ],
)
def test_error_metadata_and_parameters_are_json_serializable(
    matcher, function, args, code, params
):
    with pytest.raises(CalculationError) as caught:
        matcher(function)(*args)
    error = caught.value
    assert error.code == PREFIX + code
    assert error.params == params
    json.dumps({"code": error.code, "params": error.params}, allow_nan=False)


def test_unknown_column_has_translation_metadata():
    with pytest.raises(CalculationError) as caught:
        fields_and_values_match("missing", [{"present": 1}], ["present"])
    assert caught.value.code == PREFIX + "UNKNOWN_COLUMN"
    assert caught.value.params == {"column": "missing"}


@pytest.mark.parametrize(
    "expression, code, params",
    [
        ("pi(1)", "PI_ARGUMENTS", {}),
        ("length(pi(1))", "PI_ARGUMENTS", {}),
        (
            "map_get(map('a', 1), 'missing')",
            "MAP_KEY_NOT_FOUND",
            {"function": "map_get", "key": "missing"},
        ),
        (
            "map_get(1, 'a')",
            "MAP_FIRST_ARGUMENT_TYPE",
            {"function": "map_get"},
        ),
        (
            "make_date('bad-date')",
            "MAKE_DATE_FORMAT",
            {"date": "bad-date"},
        ),
        (
            "ascii('🙂')",
            "INVALID_ASCII_SYMBOL",
            {"symbol": "🙂"},
        ),
    ],
)
def test_parser_preserves_function_error_metadata(expression, code, params):
    parser = ExpressionParser(expression, table=[], tableKeys=[])
    parser.find_function_call()
    parser.writeFunctions()
    with pytest.raises(CalculationError) as caught:
        parser.parse_expression()
    assert caught.value.code == PREFIX + code
    assert caught.value.params == params


def test_translated_type_error_preserves_type_error_contract():
    with pytest.raises(TypeError, match="must be a dictionary") as caught:
        dictionary_match("url_encode")("not-a-dictionary")
    assert isinstance(caught.value, CalculationError)
    assert caught.value.code == PREFIX + "URL_ENCODE_DICTIONARY"
