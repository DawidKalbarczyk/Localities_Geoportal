import json

import pytest
from services.service_calc_tool import ExpressionParser


def evaluate(expression):
    parser = ExpressionParser(expression, table=[], tableKeys=[])
    parser.find_function_call()
    parser.writeFunctions()
    return parser.parse_expression()


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("from_json('{\"a\": 1}')", {"a": 1}),
        ('from_json(\'{"text": "map(1,2)"}\')', {"text": "map(1,2)"}),
        ("map('a', 1, 'b', 2)", {"a": 1, "b": 2}),
        ("map('a', 1, 'a', 2)", {"a": 2}),
        ("map_concat(map('a', 1), map('a', 2, 'b', 3))", {"a": 2, "b": 3}),
        ("map_delete(map('a', 1, 'b', 2), 'a')", {"b": 2}),
        ("map_get(map('a', 1), 'a')", 1),
        ("map_get(map('a, b', 'x, y'), 'a, b')", "x, y"),
        ("map_exist(map('a', 'b'), 'b')", False),
        ("map_exist(map('a', 1), 'a')", True),
        ("map_insert(map('a', 1), 'b', 2)", {"a": 1, "b": 2}),
        ("map_insert(map('a', 1), 'a', 2)", {"a": 2}),
        ("map_prefix_keys(map('a', 1), 'x_')", {"x_a": 1}),
        ("map_akeys(map('a', 1, 'b', 2))", ["a", "b"]),
        ("map_avals(map('a', 1, 'b', 2))", [1, 2]),
        ("map_get(map_insert(map('a', 1), 'b', 2), 'b')", 2),
        (
            "map_to_html_dl(map('tekst', '<b>Jan & Ola</b>'))",
            "<dl><dt>tekst</dt><dd>&lt;b&gt;Jan &amp; Ola&lt;/b&gt;</dd></dl>",
        ),
        (
            "map_to_html_table(map('imie', 'Jan', 'wiek', 25))",
            "<table><thead><tr><th>imie</th><th>wiek</th></tr></thead><tbody><tr><td>Jan</td><td>25</td></tr></tbody></table>",
        ),
        (
            "map_to_html_table(map('<key>', '<b>Jan</b>'))",
            "<table><thead><tr><th>&lt;key&gt;</th></tr></thead><tbody><tr><td>&lt;b&gt;Jan&lt;/b&gt;</td></tr></tbody></table>",
        ),
        (
            "url_encode(map('imie', 'Jan Kowalski', 'wiek', 25))",
            "imie=Jan%20Kowalski&wiek=25",
        ),
        (
            "url_encode(map('a&+b', 'a and plus b', 'a=b', 'a equals b'))",
            "a%26+b=a%20and%20plus%20b&a%3Db=a%20equals%20b",
        ),
        ("url_encode(map('miasto', 'Łódź'))", "miasto=%C5%81%C3%B3d%C5%BA"),
        ("from_json(to_json(map('a', 1)))", {"a": 1}),
    ],
)
def test_dictionary_expressions(expression, expected):
    assert evaluate(expression) == expected, expression


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("to_json(map('a', 1))", {"a": 1}),
        ("to_json(map('a', 0))", {"a": 0}),
        ("to_json(map('a', 1.5))", {"a": 1.5}),
        ("to_json(map('a', 1 + 2))", {"a": 3}),
        ("to_json(map('a', 1 / 2))", {"a": 0.5}),
        ("to_json([1, 2])", [1, 2]),
        ("to_json((1, 2))", [1, 2]),
        ("to_json(1)", 1),
        ("to_json(1.5)", 1.5),
        ("to_json('Zażółć🙂')", "Zażółć🙂"),
        ("to_json(map('a', map('b', [1, 1.5, 1 / 2])))", {"a": {"b": [1, 1.5, 0.5]}}),
        ("to_json(map(1, 2))", {"1": 2}),
        ("to_json(map('a', -2, 'b', 1e-6))", {"a": -2, "b": 1e-6}),
        (
            "to_json(map('a', True, 'b', False, 'c', None))",
            {"a": True, "b": False, "c": None},
        ),
        ("to_json(map('a', true, 'b', false))", {"a": True, "b": False}),
        ("to_json(true)", True),
        ("to_json(false)", False),
        ("to_json([true, false, True, False])", [True, False, True, False]),
        (
            "to_json(map('nested', map('flags', [true, false])))",
            {"nested": {"flags": [True, False]}},
        ),
        ("to_json(from_json('{\"a\": 1}'))", {"a": 1}),
        ("to_json(map('a', abs(-1)))", {"a": 1.0}),
        ("to_json(map('a', length('abc')))", {"a": 3}),
        ("to_json([])", []),
        ("to_json({})", {}),
    ],
)
def test_to_json_expressions(expression, expected):
    # Dokładny tekst sprawdza również zachowanie typów: 1 zamiast 1.0 oraz bool zamiast napisu.
    actual = evaluate(expression)
    assert actual == json.dumps(expected), expression
    assert json.loads(actual) == expected, expression


def test_to_json_10_000_parser_variants():
    for i in range(10_000):
        flag = "true" if i % 2 else "false"
        expression = (
            f"to_json(map('int', {i - 5000}, 'float', {i / 8}, 'fraction', {i}/2, "
            f"'nested', map('list', [{i}, {i + 1}/2, {flag}])))"
        )
        expected = {
            "int": i - 5000,
            "float": i / 8,
            "fraction": i / 2 if i % 2 else i // 2,
            "nested": {
                "list": [i, (i + 1) / 2 if (i + 1) % 2 else (i + 1) // 2, bool(i % 2)]
            },
        }
        assert evaluate(expression) == json.dumps(expected), expression


@pytest.mark.parametrize(
    "expression",
    [
        "map('a', 1, 'b')",
        "map('', 1)",
        "map_get(map('a', 1), 'missing')",
        "map_delete(map('a', 1), 'missing')",
        "map_get(map('a', 1))",
        "map_insert(map('a', 1), 'b')",
        "map_exist(map('a', 1), '')",
        "map_insert(map('a', 1), '', 2)",
        "map_concat(map('a', 1), 'text')",
        "map_akeys('text')",
        "map_avals('text')",
        "map_prefix_keys('text', 'x_')",
        "map_to_html_dl('text')",
        "map_to_html_table('text')",
        "url_encode('text')",
        "from_json('{')",
        "to_json(None)",
        "to_json('')",
        "to_json(map('a', x))",
        "unknown_function(1)",
    ],
)
def test_invalid_expressions(expression):
    with pytest.raises(ValueError):
        evaluate(expression)
